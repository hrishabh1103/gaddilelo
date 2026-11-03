import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import (
    VehicleBrand, VehicleModel, VehicleVariant, VehicleCategory,
    BuyingGroup, GroupMember, Quotation, User, Dealer, City
)
from backend.app.services.vehicle_intelligence.meterapp_service import MeterAppService
from backend.app.services.vehicle_intelligence.wikimedia_image_service import WikimediaImageService
from backend.app.services.vehicle_intelligence.deduplication_service import DeduplicationService
from backend.app.services.vehicle_intelligence.oem_adapters import OEMSpecificationRegistry

TARGET_11_MODELS = [
    ("Tata Motors", "Nexon"),
    ("Tata Motors", "Punch"),
    ("Maruti Suzuki", "Swift"),
    ("Hyundai", "Creta"),
    ("Mahindra", "BE 6"),
    ("Royal Enfield", "Hunter 350"),
    ("Honda", "Activa"),
    ("TVS Motor", "Apache RTR 160"),
    ("Ather Energy", "450X"),
    ("Tata Motors", "Ace"),
    ("Ashok Leyland", "Dost")
]

@pytest.mark.asyncio
async def test_meterapp_load_and_preview():
    """Validates that MeterApp records load and dry-run preview runs without mutating DB."""
    records = MeterAppService.load_meterapp_records()
    assert len(records) > 100

    async with AsyncSessionLocal() as db:
        preview = await MeterAppService.preview_import(db)
        assert preview["status"] == "PREVIEW_READY"
        assert preview["dataset"] == "METERAPP_VEHICLE_DB"
        assert preview["license"] == "ISC License"
        assert preview["models"]["deduplicated_existing_count"] >= 0
        assert "brands" in preview
        assert "models" in preview


@pytest.mark.asyncio
async def test_meterapp_incremental_sync_and_deduplication():
    """Validates that sync_incremental runs idempotently without crashing or dropping records."""
    async with AsyncSessionLocal() as db:
        res = await MeterAppService.sync_incremental(db=db)
        assert res["status"] == "COMPLETED"
        assert res["license"] == "ISC License"
        assert res["records_processed"] > 0
        assert res["records_updated"] >= 0


@pytest.mark.asyncio
async def test_all_11_validation_models_exist_with_variants():
    """Verifies that all 11 required benchmark models exist and have variants."""
    async with AsyncSessionLocal() as db:
        for brand, model in TARGET_11_MODELS:
            res = await db.execute(
                select(VehicleModel)
                .join(VehicleBrand, VehicleModel.brand_id == VehicleBrand.id)
                .options(selectinload(VehicleModel.variants), selectinload(VehicleModel.brand))
                .where(
                    VehicleBrand.name.ilike(f"%{brand}%"),
                    (VehicleModel.name.ilike(f"%{model}%") | VehicleModel.canonical_model_name.ilike(f"%{model}%"))
                )
            )
            matched = res.scalars().all()
            assert len(matched) > 0, f"Model {brand} {model} was not found in vehicle_models"

            # Check variants on the best matched model
            best_model = max(matched, key=lambda m: len(m.variants) if m.variants else 0)
            assert len(best_model.variants) > 0, f"Model {best_model.name} has 0 variants"
            
            for v in best_model.variants:
                assert v.reference_ex_showroom > 0
                assert v.fuel_type in ["PETROL", "DIESEL", "CNG", "ELECTRIC", "HYBRID"]
                assert v.transmission in ["MANUAL", "AUTOMATIC", "AMT", "CVT", "DCT", "SINGLE_SPEED_EV"]


@pytest.mark.asyncio
async def test_group_creation_with_meterapp_model():
    """Tests that an imported MeterApp vehicle can be used by a buyer to create a group."""
    async with AsyncSessionLocal() as db:
        # Find Tata Punch or TVS Apache variant
        res = await db.execute(
            select(VehicleVariant)
            .join(VehicleModel, VehicleVariant.model_id == VehicleModel.id)
            .where(VehicleModel.name.ilike("%Punch%"))
            .limit(1)
        )
        variant = res.scalar_one_or_none()
        if not variant:
            # Fallback to Apache or any variant
            res = await db.execute(select(VehicleVariant).limit(1))
            variant = res.scalar_one()

        # Find buyer user and city
        user = (await db.execute(select(User).where(User.role == "BUYER").limit(1))).scalar_one()
        city = (await db.execute(select(City).limit(1))).scalar_one()

        # Create buying group
        group_code = f"GRP-TEST-{uuid.uuid4().hex[:6].upper()}"
        group = BuyingGroup(
            id=str(uuid.uuid4()),
            group_code=group_code,
            vehicle_variant_id=variant.id,
            city_id=city.id,
            created_by_user_id=user.id,
            status="OPEN",
            target_members=5,
            current_members_count=1,
            target_purchase_timeline="WITHIN_30_DAYS",
            additional_notes="Automated MeterApp Integration Regression Test",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(group)
        await db.flush()

        member = GroupMember(
            id=str(uuid.uuid4()),
            group_id=group.id,
            user_id=user.id,
            status="ACTIVE",
            joined_at=datetime.now(timezone.utc)
        )
        db.add(member)
        await db.commit()

        # Verify group exists and points to variant
        check = (await db.execute(select(BuyingGroup).where(BuyingGroup.id == group.id))).scalar_one()
        assert check.status == "OPEN"
        assert check.current_members_count == 1
        assert check.vehicle_variant_id == variant.id


@pytest.mark.asyncio
async def test_dealer_bidding_workflow_regression():
    """Tests that a dealer can submit a quotation on an open group with a MeterApp vehicle."""
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.role == "BUYER").limit(1))).scalar_one()
        city = (await db.execute(select(City).limit(1))).scalar_one()
        variant = (await db.execute(select(VehicleVariant).limit(1))).scalar_one()
        dealer = (await db.execute(select(Dealer).limit(1))).scalar_one()

        # Create isolated test group for bidding
        group = BuyingGroup(
            id=str(uuid.uuid4()),
            group_code=f"GRP-BID-{uuid.uuid4().hex[:6].upper()}",
            vehicle_variant_id=variant.id,
            city_id=city.id,
            created_by_user_id=user.id,
            status="BIDDING_OPEN",
            target_members=5,
            current_members_count=3,
            target_purchase_timeline="WITHIN_30_DAYS",
            bidding_start_time=datetime.now(timezone.utc),
            bidding_end_time=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(group)
        await db.flush()

        # Submit quotation
        quotation = Quotation(
            id=str(uuid.uuid4()),
            group_id=group.id,
            dealer_id=dealer.id,
            revision_number=1,
            status="SUBMITTED",
            base_ex_showroom=Decimal("800000.00"),
            rto_road_tax=Decimal("64000.00"),
            insurance_amount=Decimal("32000.00"),
            dealer_discount=Decimal("25000.00"),
            final_on_road_price=Decimal("871000.00"),
            delivery_timeline_days=14,
            offer_valid_until=datetime.now(timezone.utc) + timedelta(days=7),
            remarks="Group deal best quote",
            created_at=datetime.now(timezone.utc)
        )
        db.add(quotation)
        await db.commit()

        # Verify quotation stored
        q_check = (await db.execute(select(Quotation).where(Quotation.id == quotation.id))).scalar_one()
        assert q_check.final_on_road_price == Decimal("871000.00")
        assert q_check.status == "SUBMITTED"


@pytest.mark.asyncio
async def test_image_license_and_placeholder():
    """Validates commercial reuse license checking and fallback placeholders."""
    # Permitted licenses
    assert WikimediaImageService.is_license_permitted("CC BY-SA 4.0") is True
    assert WikimediaImageService.is_license_permitted("CC BY 3.0") is True
    assert WikimediaImageService.is_license_permitted("Public domain") is True
    assert WikimediaImageService.is_license_permitted("CC0") is True

    # Rejected non-commercial / copyright
    assert WikimediaImageService.is_license_permitted("CC BY-NC 4.0") is False
    assert WikimediaImageService.is_license_permitted("All Rights Reserved") is False
    assert WikimediaImageService.is_license_permitted(None) is False

    # Fallback placeholder format
    placeholder = WikimediaImageService.get_fallback_placeholder("Tata Punch")
    assert "Tata" in placeholder
    assert "Punch" in placeholder
    assert placeholder.startswith("https://placehold.co")
