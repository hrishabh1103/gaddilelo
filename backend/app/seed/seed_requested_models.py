import sys
from pathlib import Path

_file_path = Path(__file__).resolve()
_project_root = _file_path.parents[3]
_backend_dir = _file_path.parents[2]

for _p in [str(_project_root), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import select, or_
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import (
    VehicleCategory, VehicleBrand, VehicleModel, VehicleVariant, VehicleImage
)
from backend.app.services.vehicle_intelligence.oem_adapters import OEMSpecificationRegistry

async def seed_requested():
    async with AsyncSessionLocal() as db:
        print("[SEED] Starting seed for Mahindra XEV 9e/9s and Maruti Suzuki WagonR/Ignis/Grand Vitara...")

        # Find brands
        maruti_brand = (await db.execute(
            select(VehicleBrand).where(VehicleBrand.name.ilike("%Maruti%"))
        )).scalars().first()

        mahindra_brand = (await db.execute(
            select(VehicleBrand).where(VehicleBrand.name.ilike("%Mahindra%"))
        )).scalars().first()

        cat_car = (await db.execute(
            select(VehicleCategory).where(VehicleCategory.slug == "car")
        )).scalars().first()

        cat_ev = (await db.execute(
            select(VehicleCategory).where(VehicleCategory.slug == "electric-vehicle")
        )).scalars().first()

        if not cat_ev:
            cat_ev = cat_car

        # --- 1. Mahindra XEV 9e ---
        m_xev9e_data = OEMSpecificationRegistry.match_model("Mahindra XEV 9e")
        xev9e_model = (await db.execute(
            select(VehicleModel).where(
                or_(
                    VehicleModel.name.ilike("%xev 9e%"),
                    VehicleModel.slug == "mahindra-xev-9e"
                )
            )
        )).scalars().first()

        if not xev9e_model:
            xev9e_model = VehicleModel(
                brand_id=mahindra_brand.id,
                name="Mahindra XEV 9e",
                slug="mahindra-xev-9e",
                vehicle_category_slug="electric-vehicle",
                body_type="Electric SUV Coupe",
                model_year=2026,
                canonical_brand_name="Mahindra",
                canonical_model_name="XEV 9e",
                length_mm=4790,
                width_mm=1905,
                height_mm=1690,
                wheelbase_mm=2775,
                ground_clearance_mm=207,
                safety_rating_stars=5,
                safety_rating_agency="BHARAT_NCAP",
                image_url="https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=1000&auto=format&fit=crop&q=80",
                last_verified_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(xev9e_model)
            await db.flush()
            print("Created model: Mahindra XEV 9e")
        else:
            xev9e_model.name = "Mahindra XEV 9e"
            xev9e_model.image_url = "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=1000&auto=format&fit=crop&q=80"
            xev9e_model.is_active = True
            await db.flush()

        # Seed variants for XEV 9e
        for v in m_xev9e_data["details"]["variants"]:
            v_exist = (await db.execute(
                select(VehicleVariant).where(
                    VehicleVariant.model_id == xev9e_model.id,
                    VehicleVariant.name == v["name"]
                )
            )).scalars().first()
            if not v_exist:
                db.add(VehicleVariant(
                    model_id=xev9e_model.id,
                    name=v["name"],
                    fuel_type=v["fuel"],
                    transmission=v["trans"],
                    seating_capacity=v.get("seating", 5),
                    engine_cc_or_battery_kwh=v.get("battery", "79 kWh"),
                    reference_ex_showroom=Decimal(str(v["price"])),
                    claimed_range_km=Decimal(str(v.get("range_claimed", 656))),
                    tested_range_km=Decimal(str(v.get("range_tested", 530))),
                    specifications=v,
                    source_priority=1,
                    is_active=True,
                    last_verified_at=datetime.now(timezone.utc)
                ))
        await db.flush()

        # --- 2. Mahindra XEV 9s ---
        m_xev9s_data = OEMSpecificationRegistry.match_model("Mahindra XEV 9s")
        xev9s_model = (await db.execute(
            select(VehicleModel).where(
                or_(
                    VehicleModel.name.ilike("%xev 9s%"),
                    VehicleModel.slug == "mahindra-xev-9s"
                )
            )
        )).scalars().first()

        if not xev9s_model:
            xev9s_model = VehicleModel(
                brand_id=mahindra_brand.id,
                name="Mahindra XEV 9s",
                slug="mahindra-xev-9s",
                vehicle_category_slug="electric-vehicle",
                body_type="Electric SUV",
                model_year=2026,
                canonical_brand_name="Mahindra",
                canonical_model_name="XEV 9s",
                length_mm=4740,
                width_mm=1900,
                height_mm=1680,
                wheelbase_mm=2775,
                ground_clearance_mm=205,
                safety_rating_stars=5,
                safety_rating_agency="BHARAT_NCAP",
                image_url="https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=1000&auto=format&fit=crop&q=80",
                last_verified_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(xev9s_model)
            await db.flush()
            print("Created model: Mahindra XEV 9s")
        else:
            xev9s_model.name = "Mahindra XEV 9s"
            xev9s_model.image_url = "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=1000&auto=format&fit=crop&q=80"
            xev9s_model.is_active = True
            await db.flush()

        for v in m_xev9s_data["details"]["variants"]:
            v_exist = (await db.execute(
                select(VehicleVariant).where(
                    VehicleVariant.model_id == xev9s_model.id,
                    VehicleVariant.name == v["name"]
                )
            )).scalars().first()
            if not v_exist:
                db.add(VehicleVariant(
                    model_id=xev9s_model.id,
                    name=v["name"],
                    fuel_type=v["fuel"],
                    transmission=v["trans"],
                    seating_capacity=v.get("seating", 5),
                    engine_cc_or_battery_kwh=v.get("battery", "79 kWh"),
                    reference_ex_showroom=Decimal(str(v["price"])),
                    claimed_range_km=Decimal(str(v.get("range_claimed", 640))),
                    tested_range_km=Decimal(str(v.get("range_tested", 510))),
                    specifications=v,
                    source_priority=1,
                    is_active=True,
                    last_verified_at=datetime.now(timezone.utc)
                ))
        await db.flush()

        # --- 3. Maruti Suzuki WagonR ---
        wagonr_data = OEMSpecificationRegistry.match_model("Maruti Suzuki WagonR")
        wagonr_model = (await db.execute(
            select(VehicleModel).where(
                or_(
                    VehicleModel.name.ilike("%wagon%r%"),
                    VehicleModel.slug == "maruti-suzuki-wagon-r",
                    VehicleModel.slug == "maruti-wagon-r"
                )
            )
        )).scalars().first()

        if not wagonr_model:
            wagonr_model = VehicleModel(
                brand_id=maruti_brand.id,
                name="Maruti Suzuki WagonR",
                slug="maruti-suzuki-wagon-r",
                vehicle_category_slug="car",
                body_type="Hatchback",
                model_year=2025,
                canonical_brand_name="Maruti Suzuki",
                canonical_model_name="WagonR",
                length_mm=3655,
                width_mm=1620,
                height_mm=1675,
                wheelbase_mm=2435,
                image_url="https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=1000&auto=format&fit=crop&q=80",
                last_verified_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(wagonr_model)
            await db.flush()
        else:
            wagonr_model.name = "Maruti Suzuki WagonR"
            wagonr_model.image_url = "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=1000&auto=format&fit=crop&q=80"
            wagonr_model.is_active = True
            await db.flush()

        for v in wagonr_data["details"]["variants"]:
            v_exist = (await db.execute(
                select(VehicleVariant).where(
                    VehicleVariant.model_id == wagonr_model.id,
                    VehicleVariant.name == v["name"]
                )
            )).scalars().first()
            if not v_exist:
                db.add(VehicleVariant(
                    model_id=wagonr_model.id,
                    name=v["name"],
                    fuel_type=v["fuel"],
                    transmission=v["trans"],
                    seating_capacity=v.get("seating", 5),
                    engine_cc_or_battery_kwh=v.get("engine", "1197 cc"),
                    reference_ex_showroom=Decimal(str(v["price"])),
                    claimed_mileage_kmpl=Decimal(str(v.get("mileage", 24.35))),
                    specifications=v,
                    source_priority=1,
                    is_active=True,
                    last_verified_at=datetime.now(timezone.utc)
                ))
        await db.flush()

        # --- 4. Maruti Suzuki Ignis ---
        ignis_data = OEMSpecificationRegistry.match_model("Maruti Suzuki Ignis")
        ignis_model = (await db.execute(
            select(VehicleModel).where(
                or_(
                    VehicleModel.name == "IGNIS",
                    VehicleModel.name == "Maruti Suzuki Ignis",
                    VehicleModel.slug == "maruti-suzuki-ignis"
                )
            )
        )).scalars().first()

        if not ignis_model:
            ignis_model = VehicleModel(
                brand_id=maruti_brand.id,
                name="Maruti Suzuki Ignis",
                slug="maruti-suzuki-ignis",
                vehicle_category_slug="car",
                body_type="Compact Hatchback",
                model_year=2025,
                canonical_brand_name="Maruti Suzuki",
                canonical_model_name="Ignis",
                length_mm=3700,
                width_mm=1690,
                height_mm=1595,
                wheelbase_mm=2435,
                ground_clearance_mm=180,
                image_url="https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1000&auto=format&fit=crop&q=80",
                last_verified_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(ignis_model)
            await db.flush()
        else:
            ignis_model.name = "Maruti Suzuki Ignis"
            ignis_model.image_url = "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1000&auto=format&fit=crop&q=80"
            ignis_model.is_active = True
            await db.flush()

        for v in ignis_data["details"]["variants"]:
            v_exist = (await db.execute(
                select(VehicleVariant).where(
                    VehicleVariant.model_id == ignis_model.id,
                    VehicleVariant.name == v["name"]
                )
            )).scalars().first()
            if not v_exist:
                db.add(VehicleVariant(
                    model_id=ignis_model.id,
                    name=v["name"],
                    fuel_type=v["fuel"],
                    transmission=v["trans"],
                    seating_capacity=v.get("seating", 5),
                    engine_cc_or_battery_kwh=v.get("engine", "1197 cc"),
                    reference_ex_showroom=Decimal(str(v["price"])),
                    claimed_mileage_kmpl=Decimal(str(v.get("mileage", 20.89))),
                    specifications=v,
                    source_priority=1,
                    is_active=True,
                    last_verified_at=datetime.now(timezone.utc)
                ))
        await db.flush()

        # --- 5. Maruti Suzuki Grand Vitara ---
        gv_data = OEMSpecificationRegistry.match_model("Maruti Suzuki Grand Vitara")
        gv_model = (await db.execute(
            select(VehicleModel).where(
                or_(
                    VehicleModel.name == "GRAND VITARA",
                    VehicleModel.name == "Maruti Suzuki Grand Vitara",
                    VehicleModel.slug == "maruti-suzuki-grand-vitara"
                )
            )
        )).scalars().first()

        if not gv_model:
            gv_model = VehicleModel(
                brand_id=maruti_brand.id,
                name="Maruti Suzuki Grand Vitara",
                slug="maruti-suzuki-grand-vitara",
                vehicle_category_slug="car",
                body_type="Mid-size SUV",
                model_year=2025,
                canonical_brand_name="Maruti Suzuki",
                canonical_model_name="Grand Vitara",
                length_mm=4345,
                width_mm=1795,
                height_mm=1645,
                wheelbase_mm=2600,
                ground_clearance_mm=210,
                image_url="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1000&auto=format&fit=crop&q=80",
                last_verified_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(gv_model)
            await db.flush()
        else:
            gv_model.name = "Maruti Suzuki Grand Vitara"
            gv_model.image_url = "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1000&auto=format&fit=crop&q=80"
            gv_model.is_active = True
            await db.flush()

        for v in gv_data["details"]["variants"]:
            v_exist = (await db.execute(
                select(VehicleVariant).where(
                    VehicleVariant.model_id == gv_model.id,
                    VehicleVariant.name == v["name"]
                )
            )).scalars().first()
            if not v_exist:
                db.add(VehicleVariant(
                    model_id=gv_model.id,
                    name=v["name"],
                    fuel_type=v["fuel"],
                    transmission=v["trans"],
                    seating_capacity=v.get("seating", 5),
                    engine_cc_or_battery_kwh=v.get("engine", "1462 cc"),
                    reference_ex_showroom=Decimal(str(v["price"])),
                    claimed_mileage_kmpl=Decimal(str(v.get("mileage", 21.11))),
                    specifications=v,
                    source_priority=1,
                    is_active=True,
                    last_verified_at=datetime.now(timezone.utc)
                ))

        await db.commit()
        print("[SEED] Successfully seeded and updated all requested vehicles with real variants and images!")

if __name__ == "__main__":
    asyncio.run(seed_requested())

