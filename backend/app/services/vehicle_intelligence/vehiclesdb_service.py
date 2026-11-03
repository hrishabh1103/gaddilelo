import os
import csv
import io
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.app.models.models import (
    VehicleBrand, VehicleModel, VehicleCategory, VehicleDatasetSync
)

class VehiclesDBService:
    """
    VehiclesDB Open Dataset Integration (https://github.com/vehiclesdb/vehiclesdb).
    Licence: Creative Commons Attribution 4.0 International (CC BY 4.0).
    Attribution: VehiclesDB Contributors (https://github.com/vehiclesdb/vehiclesdb).

    Features:
    - Incremental sync mechanism tracking dataset hash & records.
    - India-focused filtering: imports Indian manufacturers and models sold in India.
    - Deterministic category mapping.
    """

    REPO_RAW_URL = "https://raw.githubusercontent.com/vehiclesdb/vehiclesdb/main/dist/vehicles.csv"
    DATASET_NAME = "VEHICLES_DB"
    ATTRIBUTION_TEXT = "VehiclesDB Contributors (CC BY 4.0, https://github.com/vehiclesdb/vehiclesdb)"

    # Recognized automotive brands with active manufacturing or sales operations in India
    INDIAN_MARKET_MAKES = {
        "tata": "Tata Motors",
        "mahindra": "Mahindra",
        "maruti-suzuki": "Maruti Suzuki",
        "maruti": "Maruti Suzuki",
        "hyundai": "Hyundai",
        "kia": "Kia",
        "toyota": "Toyota",
        "honda": "Honda",
        "renault": "Renault",
        "nissan": "Nissan",
        "volkswagen": "Volkswagen",
        "skoda": "Skoda",
        "mg": "MG Motor",
        "bmw": "BMW",
        "mercedes-benz": "Mercedes-Benz",
        "audi": "Audi",
        "royal-enfield": "Royal Enfield",
        "hero": "Hero MotoCorp",
        "hero-motocorp": "Hero MotoCorp",
        "bajaj": "Bajaj Auto",
        "tvs": "TVS Motor",
        "ather": "Ather Energy",
        "ola": "Ola Electric",
        "ashok-leyland": "Ashok Leyland",
        "eicher": "Eicher Motors",
        "force": "Force Motors"
    }

    @classmethod
    async def fetch_dataset_csv(cls) -> Optional[str]:
        """Fetches latest vehicles.csv from official GitHub repository with compliant User-Agent."""
        headers = {
            "User-Agent": "GaadiLeloBot/1.0 (+https://gaadilelo.com/bot; bot@gaadilelo.com)"
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(cls.REPO_RAW_URL, headers=headers)
                if resp.status_code == 200:
                    return resp.text
        except Exception as e:
            print(f"[VehiclesDBService] Network fetch failed: {e}. Checking local cache.")

        # Local fallback if offline/sandbox
        cache_path = os.path.join(os.path.dirname(__file__), "data", "vehiclesdb_sample.csv")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()

        return None

    @classmethod
    async def sync_incremental(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        Executes incremental import of VehiclesDB into the vehicle catalog.
        Skips existing models, links categories, and preserves CC BY 4.0 attribution.
        """
        raw_csv = await cls.fetch_dataset_csv()
        if not raw_csv:
            return {
                "status": "FAILED",
                "error": "Could not retrieve VehiclesDB dataset from remote repository or local cache."
            }

        csv_hash = hashlib.sha256(raw_csv.encode("utf-8")).hexdigest()

        # Check last sync record
        last_sync_res = await db.execute(
            select(VehicleDatasetSync)
            .where(
                VehicleDatasetSync.dataset_name == cls.DATASET_NAME,
                VehicleDatasetSync.status == "COMPLETED"
            )
            .order_by(VehicleDatasetSync.started_at.desc())
        )
        last_sync = last_sync_res.scalars().first()
        if last_sync and last_sync.sync_metadata.get("content_hash") == csv_hash:
            return {
                "status": "UP_TO_DATE",
                "message": "VehiclesDB dataset is already synchronized with latest content hash.",
                "hash": csv_hash,
                "attribution": cls.ATTRIBUTION_TEXT,
                "last_synced_at": last_sync.completed_at.isoformat() if last_sync.completed_at else None
            }

        # Initialize sync tracking record
        sync_job = VehicleDatasetSync(
            dataset_name=cls.DATASET_NAME,
            status="IN_PROGRESS",
            sync_metadata={"content_hash": csv_hash, "attribution": cls.ATTRIBUTION_TEXT}
        )
        db.add(sync_job)
        await db.commit()

        # Category mapping lookup
        cats_res = await db.execute(select(VehicleCategory))
        categories = {c.slug: c.id for c in cats_res.scalars().all()}
        default_car_cat = categories.get("car")
        two_wheeler_cat = categories.get("two-wheeler")
        cv_cat = categories.get("commercial-vehicle")

        reader = csv.DictReader(io.StringIO(raw_csv))
        processed = 0
        imported = 0
        updated = 0

        try:
            for row in reader:
                processed += 1
                make_slug = row.get("make_slug", "").lower().strip()
                model_slug = row.get("model_slug", "").lower().strip()
                model_name = row.get("model_name", "").strip()
                make_name = row.get("make_name", "").strip()
                countries = (row.get("countries") or "").split("|")
                kind = row.get("kind", "car").lower()

                # Filter for Indian market relevance:
                is_indian_make = make_slug in cls.INDIAN_MARKET_MAKES
                is_sold_in_india = "in" in countries or is_indian_make

                if not is_sold_in_india:
                    continue

                # Determine category
                if kind == "motorcycle" or "bike" in kind:
                    cat_id = two_wheeler_cat or default_car_cat
                elif kind in ["truck", "commercial", "bus"]:
                    cat_id = cv_cat or default_car_cat
                else:
                    cat_id = default_car_cat

                resolved_brand_name = cls.INDIAN_MARKET_MAKES.get(make_slug, make_name)

                # Find or create Brand
                brand_res = await db.execute(
                    select(VehicleBrand).where(VehicleBrand.name.ilike(resolved_brand_name))
                )
                brand = brand_res.scalars().first()
                if not brand:
                    brand = VehicleBrand(
                        name=resolved_brand_name,
                        slug=make_slug,
                        category_id=cat_id
                    )
                    db.add(brand)
                    await db.flush()

                # Check if model exists by name or slug
                candidate_slug = f"{make_slug}-{model_slug}"
                model_res = await db.execute(
                    select(VehicleModel).where(
                        or_(
                            (VehicleModel.brand_id == brand.id) & VehicleModel.name.ilike(model_name),
                            VehicleModel.slug == candidate_slug
                        )
                    )
                )
                model = model_res.scalars().first()
                if not model:
                    unique_slug = candidate_slug
                    slug_check = await db.execute(
                        select(VehicleModel).where(VehicleModel.slug == unique_slug)
                    )
                    if slug_check.scalars().first():
                        unique_slug = f"{candidate_slug}-{str(uuid.uuid4())[:6]}"

                    model = VehicleModel(
                        brand_id=brand.id,
                        name=model_name,
                        slug=unique_slug,
                        body_type=row.get("body_types") or ("Motorcycle" if kind == "motorcycle" else "Car"),
                        is_active=True
                    )
                    db.add(model)
                    await db.flush()
                    imported += 1
                else:
                    updated += 1

            sync_job.records_processed = processed
            sync_job.records_imported = imported
            sync_job.records_updated = updated
            sync_job.status = "COMPLETED"
            sync_job.completed_at = datetime.now(timezone.utc)
            await db.commit()

        except Exception as e:
            sync_job.status = "FAILED"
            sync_job.error_message = str(e)
            sync_job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            raise e

        return {
            "status": "COMPLETED",
            "records_processed": processed,
            "records_imported": imported,
            "records_updated": updated,
            "content_hash": csv_hash,
            "attribution": cls.ATTRIBUTION_TEXT
        }
