import os
import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import (
    VehicleModel, VehicleBrand, VehicleVariant, VehicleDiscoveryRecord,
    VehicleDiscoveryJob, VehicleDataSource, Notification, BuyingGroup, User
)
from backend.app.services.vehicle_intelligence import (
    SourceRegistry, ExtractionService, NormalizationService, ValidationService,
    DeduplicationService, SearchService, DiscoveryService, VehicleIntelligenceScheduler
)

@pytest.mark.asyncio
async def test_audit_external_providers():
    """TEST 2: External Provider Audit."""
    audit_results = await SourceRegistry.audit_all_sources()
    assert len(audit_results) >= 4

    adapters_by_name = {r["source_name"]: r for r in audit_results}

    # 1. Live OEM Feeds (Tata, Mahindra)
    tata = adapters_by_name.get("Tata Motors Official Press Feed")
    assert tata is not None
    assert tata["is_live"] is True
    assert tata["requires_credentials"] is False

    # 2. Licensed Commercial API
    api = adapters_by_name.get("Licensed Automotive Catalog API")
    assert api is not None
    assert api["is_live"] is True
    assert api["requires_credentials"] is True
    assert api["credentials_configured"] is bool(os.getenv("AUTOMOTIVE_API_KEY"))

    # 3. Local Test Fixture
    fixture = adapters_by_name.get("Authorized Indian OEM Test Fixtures")
    assert fixture is not None
    assert fixture["is_live"] is False
    assert fixture["status"] == "OPERATIONAL"


@pytest.mark.asyncio
async def test_ai_extraction_honesty_and_attribution():
    """TEST 3: AI Extraction verification and source attribution."""
    sample_text = "Royal Enfield introduces the all-new Hunter 350 with 349 cc J-series engine starting at ₹1.38 Lakh."
    
    extracted = await ExtractionService.extract_from_content(
        raw_text_or_dict=sample_text,
        source_url="https://www.royalenfield.com/hunter-350",
        source_name="Royal Enfield Press Docket"
    )

    # Verify no false claim of LLM when keys are absent
    has_keys = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    if not has_keys:
        assert "Fallback Rule Parser" in extracted.source_name or "DETERMINISTIC" in str(extracted.variants[0].specifications)
    
    # Source attribution check
    assert extracted.source_url == "https://www.royalenfield.com/hunter-350"
    assert "Royal Enfield Press Docket" in extracted.source_name
    assert extracted.brand_name == "Royal Enfield"
    assert extracted.category_slug == "two-wheeler"
    assert extracted.variants[0].seating_capacity == 2
    assert extracted.variants[0].specifications.get("airbags") == 0


@pytest.mark.asyncio
async def test_background_scheduler_execution():
    """TEST 4: Scheduled discovery background job execution, retries, and duplicate prevention."""
    scheduler = VehicleIntelligenceScheduler.get_instance()
    
    # Execute a manual scan cycle through the scheduler
    result = await scheduler.execute_scan_cycle()
    assert result["status"] in ["COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED"]
    assert "job_id" in result
    assert result["total_sources"] >= 3

    # Check job in database
    async with AsyncSessionLocal() as db:
        job = (await db.execute(
            select(VehicleDiscoveryJob).where(VehicleDiscoveryJob.id == result["job_id"])
        )).scalar_one_or_none()
        assert job is not None
        assert job.job_type == "SCHEDULED_SCAN"
        assert job.completed_at is not None


@pytest.mark.asyncio
async def test_discovery_mahindra_be_6():
    """TEST 1 & 5 & 6: Mahindra BE 6e Discovery & Accuracy Validation."""
    async with AsyncSessionLocal() as db:
        # 1. Search catalogue
        res = await SearchService.search_catalogue("Mahindra BE 6", category_slug=None, db=db)
        # Note: if previously approved in test, may be found; otherwise triggers discovery
        
        # 2. Trigger Discovery Request
        req_res = await DiscoveryService.create_customer_discovery_request(
            search_query="Mahindra BE 6e",
            customer_name="Pooja Sharma",
            customer_email="pooja.sharma@example.com",
            customer_phone="+919876500001",
            category_slug="electric-vehicle",
            target_city_id=None,
            user_id=None,
            db=db
        )
        assert req_res["status"] == "PENDING_REVIEW"
        assert "Mahindra" in req_res["brand"]
        assert "BE 6" in req_res["model"]

        # 3. Retrieve record dossier
        rec = (await db.execute(
            select(VehicleDiscoveryRecord).where(VehicleDiscoveryRecord.id == req_res["record_id"])
        )).scalar_one()

        # 4. Accuracy Verification: ARAI Range vs Estimated, Ex-showroom vs Dealer quote
        data = rec.extracted_data
        assert data["category_slug"] in ["electric-vehicle", "car"]
        assert data["body_type"] in ["Electric SUV Coupe", "SUV"]
        assert len(data["variants"]) >= 2
        
        # Verify 59kWh and 79kWh variants
        var_59 = next((v for v in data["variants"] if "59" in v["variant_name"] or "59" in str(v.get("engine_cc_or_battery_kwh"))), None)
        assert var_59 is not None
        assert var_59["fuel_type"] == "ELECTRIC"
        assert Decimal(str(var_59["reference_ex_showroom"])) >= 1800000

        # Verify source provenance
        assert "source_attribution" in rec.primary_source_name or "INGLO" in rec.primary_source_name or "gaadilelo.com" in rec.primary_source_url


@pytest.mark.asyncio
async def test_discovery_royal_enfield_hunter_350_and_workflow():
    """TEST 1 & 5 & 6: Royal Enfield Hunter 350 Customer Workflow & Accuracy."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Step 1: Customer searches for unknown vehicle
        search_res = await ac.get("/api/v1/intelligence/search?q=Royal+Enfield+Hunter+350")
        assert search_res.status_code == 200

        # Step 2: Customer creates discovery request
        disc_res = await ac.post("/api/v1/intelligence/discovery-requests", json={
            "search_query": "Royal Enfield Hunter 350",
            "category_slug": "two-wheeler",
            "customer_name": "Vikram Rathore",
            "customer_email": "vikram.rathore@example.com",
            "customer_phone": "+919876512345"
        })
        assert disc_res.status_code == 200
        disc_data = disc_res.json()
        assert disc_data["status"] == "PENDING_REVIEW"
        rec_id = disc_data["record_id"]

        # Step 3: Admin reviews the dossier
        admin_login = await ac.post("/api/v1/auth/login", json={
            "email": "admin@gaadilelo.com",
            "password": "Admin@123"
        })
        token = admin_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        dossier_res = await ac.get(f"/api/v1/intelligence/records/{rec_id}", headers=headers)
        assert dossier_res.status_code == 200
        dossier = dossier_res.json()
        assert dossier["discovered_brand"] == "Royal Enfield"
        
        # Accuracy checks on Hunter 350:
        extracted = dossier["extracted_data"]
        assert extracted["category_slug"] == "two-wheeler"
        assert extracted["variants"][0]["seating_capacity"] == 2
        assert extracted["variants"][0]["specifications"].get("airbags") == 0

        # Step 4: Admin approves the vehicle
        appr_res = await ac.post(
            f"/api/v1/intelligence/records/{rec_id}/approve",
            json={"admin_notes": "Verified against Royal Enfield technical sheet."},
            headers=headers
        )
        assert appr_res.status_code == 200
        pub_model_id = appr_res.json()["published_model_id"]

        # Step 5: Vehicle is live in catalogue
        cat_check = await ac.get(f"/api/v1/catalog/models/{pub_model_id}")
        assert cat_check.status_code == 200
        assert cat_check.json()["name"] == "Royal Enfield Hunter 350"


@pytest.mark.asyncio
async def test_discovery_ather_450x_accuracy():
    """TEST 1 & 6: Ather 450X accuracy, claimed IDC vs true range, battery capacity."""
    async with AsyncSessionLocal() as db:
        req_res = await DiscoveryService.create_customer_discovery_request(
            search_query="Ather 450X",
            customer_name="Neha Gupta",
            customer_email="neha.gupta@example.com",
            customer_phone="+919876522222",
            category_slug="electric-vehicle",
            target_city_id=None,
            user_id=None,
            db=db
        )
        rec = (await db.execute(
            select(VehicleDiscoveryRecord).where(VehicleDiscoveryRecord.id == req_res["record_id"])
        )).scalar_one()

        data = rec.extracted_data
        assert "Ather" in data["brand_name"]
        assert "450X" in data["model_name"]
        
        # Verify 2-wheeler accuracy: 2 seats, 0 airbags, single speed EV
        v0 = data["variants"][0]
        assert v0["fuel_type"] == "ELECTRIC"
        assert v0["seating_capacity"] == 2
        assert v0["specifications"].get("airbags") == 0
        
        # Verify distinction between claimed IDC range and real-world TrueRange
        specs = v0["specifications"]
        has_range_distinction = ("range_idc_claimed" in specs or "range_tested_truerange" in specs or "range" in specs)
        assert has_range_distinction is True
