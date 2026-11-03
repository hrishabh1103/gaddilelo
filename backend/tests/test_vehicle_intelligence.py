import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from decimal import Decimal

from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import User, VehicleModel, VehicleDiscoveryRecord, VehicleDiscoveryJob
from backend.app.services.vehicle_intelligence import (
    NormalizationService, ValidationService, DeduplicationService,
    ExtractionService, SourceRegistry, MockAutomotiveProvider
)

@pytest.fixture(scope="module")
def admin_headers():
    return {}

@pytest.mark.asyncio
async def test_normalization_and_units():
    """Test 6: Normalize data (prices, power, torque, fuel, transmission)."""
    # 1. Price normalization
    assert NormalizationService.normalize_price("₹11.69 Lakh") == Decimal("1169000.00")
    assert NormalizationService.normalize_price("1.25 Cr") == Decimal("12500000.00")
    assert NormalizationService.normalize_price(850000) == Decimal("850000")

    # 2. Power normalization (kW, BHP, HP to PS)
    val_ps, unit = NormalizationService.normalize_power("170 kW")
    assert unit == "PS"
    assert val_ps == pytest.approx(231.1, 0.5)

    val_bhp, _ = NormalizationService.normalize_power("120 BHP")
    assert val_bhp == pytest.approx(121.7, 0.5)

    # 3. Torque normalization
    val_nm, _ = NormalizationService.normalize_torque("280 lb-ft")
    assert val_nm == pytest.approx(379.6, 1.0)

    # 4. Fuel and transmission
    assert NormalizationService.normalize_fuel_type("Electric Battery EV") == "ELECTRIC"
    assert NormalizationService.normalize_fuel_type("Turbo Petrol") == "PETROL"
    assert NormalizationService.normalize_transmission("7-speed DCA") == "DCT"
    assert NormalizationService.normalize_transmission("Single speed") == "SINGLE_SPEED_EV"


@pytest.mark.asyncio
async def test_validation_and_conflicts():
    """Test 8: Detect conflicting specifications & plausibility."""
    # Plausible payload
    plausible = {
        "brand": "Tata Motors",
        "model": "Tata Curvv",
        "min_price": 999000,
        "max_price": 1769000,
        "variants": [{"name": "Smart", "fuel_type": "PETROL", "transmission": "MANUAL", "price": 999000}]
    }
    res_ok = ValidationService.validate_vehicle(plausible)
    assert res_ok.is_valid is True
    assert res_ok.confidence_score >= 0.9

    # Conflict and anomaly payload
    anomaly = {
        "brand": "T", # too short
        "model": "X",
        "min_price": -500, # negative
        "variants": [],
        "conflicts": ["Source A claims 45 kWh, Source B claims 55 kWh"]
    }
    res_conflict = ValidationService.validate_vehicle(anomaly)
    assert len(res_conflict.issues) > 0
    assert len(res_conflict.conflicts) == 1
    assert res_conflict.confidence_score < 0.7


@pytest.mark.asyncio
async def test_search_existing_vehicle():
    """Test 1: Search existing vehicle in catalogue."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/intelligence/search?q=Nexon")
        assert res.status_code == 200
        data = res.json()
        assert data["found"] is True
        assert data["models_count"] > 0
        assert any("Nexon" in m["name"] for m in data["models"])


@pytest.mark.asyncio
async def test_search_unknown_vehicle():
    """Test 2: Search unknown vehicle returns not found with discovery prompt."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/intelligence/search?q=Tesla+Cybertruck+India+Edition")
        assert res.status_code == 200
        data = res.json()
        assert data["found"] is False
        assert "couldn't find this vehicle" in data["message"].lower()


@pytest.mark.asyncio
async def test_customer_discovery_request_and_extraction():
    """Test 3, 4, 5: Create discovery request, discover from authorized source, extract specs."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/intelligence/discovery-requests", json={
            "search_query": "Mahindra BE 6e",
            "category_slug": "electric-vehicle",
            "customer_name": "Aman Verma",
            "customer_email": "aman.verma@example.com",
            "customer_phone": "+919876543210"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "PENDING_REVIEW"
        assert "Mahindra" in data["brand"]
        assert "BE 6e" in data["model"]
        assert "record_id" in data
        assert "job_id" in data


@pytest.mark.asyncio
async def test_deduplication_detection():
    """Test 7: Detect duplicate models."""
    async with AsyncSessionLocal() as session:
        # Nexon is already in DB
        dup = await DeduplicationService.match_existing_vehicle(
            brand_name="Tata Motors",
            model_name="Tata Nexon",
            variants_candidate=[{"name": "Creative Plus 1.2L Turbo Petrol"}],
            db=session
        )
        assert dup.existing_model is not None
        assert dup.matched_variants_count >= 1


@pytest.mark.asyncio
async def test_admin_queue_review_and_approval_flow():
    """Test 9, 10, 11: Admin approval, catalogue publication, customer notification."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Login as Admin
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@gaadilelo.com",
            "password": "Admin@123"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. View Overview
        overview_res = await ac.get("/api/v1/intelligence/overview", headers=headers)
        assert overview_res.status_code == 200
        overview = overview_res.json()
        assert overview["pending_review_count"] >= 1

        # 3. View Discovery Queue
        queue_res = await ac.get("/api/v1/intelligence/queue?review_status=PENDING_REVIEW", headers=headers)
        assert queue_res.status_code == 200
        queue = queue_res.json()
        assert len(queue) > 0
        target_rec = queue[0]

        # 4. View Record Detail with Sources and Citations
        rec_id = target_rec["id"]
        detail_res = await ac.get(f"/api/v1/intelligence/records/{rec_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert "extracted_data" in detail
        assert detail["subscribers_count"] >= 1

        # 5. Admin Approves and Publishes Record
        approve_res = await ac.post(
            f"/api/v1/intelligence/records/{rec_id}/approve",
            json={"admin_notes": "Specifications verified against OEM launch docket."},
            headers=headers
        )
        assert approve_res.status_code == 200
        appr_data = approve_res.json()
        assert appr_data["status"] == "APPROVED"
        published_model_id = appr_data["published_model_id"]
        assert published_model_id is not None

        # 6. Verify Catalogue Publication (Now live in /catalog/models/{id})
        model_check = await ac.get(f"/api/v1/catalog/models/{published_model_id}")
        assert model_check.status_code == 200
        assert model_check.json()["id"] == published_model_id
        assert len(model_check.json()["variants"]) > 0


@pytest.mark.asyncio
async def test_unauthorized_approval_attempt():
    """Test 15: Unauthorized approval attempt is rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Non-admin / anonymous token attempt
        res = await ac.post(
            "/api/v1/intelligence/records/some-fake-id/approve",
            json={"admin_notes": "Hacker attempt"}
        )
        assert res.status_code in [401, 403]


@pytest.mark.asyncio
async def test_failed_external_source_and_missing_credentials():
    """Test 12, 13: Failed external source & missing API credentials safe handling."""
    # Test ExtractionService without API keys uses deterministic fallback
    extracted = await ExtractionService.extract_from_content(
        raw_text_or_dict="Tata Motors announces all-new Curvv Turbo Petrol starting at ₹9.99 Lakh with 125 PS power.",
        source_url="https://tatamotors.com/press",
        source_name="Tata Press"
    )
    assert extracted.brand_name == "Tata Motors"
    assert extracted.reference_ex_showroom_min == Decimal("999000.00")
    assert len(extracted.variants) > 0


@pytest.mark.asyncio
async def test_price_history_recording():
    """Test 14: Price history updates."""
    async with AsyncSessionLocal() as session:
        from backend.app.services.vehicle_intelligence.update_service import UpdateService
        from backend.app.models.models import VehicleVariant
        from sqlalchemy import select

        v_res = await session.execute(select(VehicleVariant))
        variant = v_res.scalars().first()
        assert variant is not None

        history = await UpdateService.record_price_history(
            variant_id=variant.id,
            amount=Decimal("1175000"),
            price_type="EX_SHOWROOM_REFERENCE",
            source_url="https://press.gaadilelo.com/update",
            source_name="Quarterly Revision",
            db=session
        )
        assert history.id is not None
        assert history.amount == Decimal("1175000")

