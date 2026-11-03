from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.models import (
    VehicleModel, VehicleVariant, VehicleUpdateHistory, VehiclePriceHistory
)

class UpdateService:
    """
    Tracks and records specification revisions, price changes, and variant additions.
    """

    @classmethod
    async def record_price_history(
        cls,
        variant_id: str,
        amount: Decimal,
        price_type: str = "EX_SHOWROOM_REFERENCE",
        city_id: Optional[str] = None,
        source_url: Optional[str] = None,
        source_name: Optional[str] = None,
        discovery_record_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> VehiclePriceHistory:
        history = VehiclePriceHistory(
            vehicle_variant_id=variant_id,
            discovery_record_id=discovery_record_id,
            city_id=city_id,
            price_type=price_type,
            amount=amount,
            currency="INR",
            source_url=source_url,
            source_name=source_name,
            effective_from=datetime.now(timezone.utc),
            verified_at=datetime.now(timezone.utc)
        )
        if db:
            db.add(history)
            await db.commit()
            await db.refresh(history)
        return history

    @classmethod
    async def track_model_updates(
        cls,
        model: VehicleModel,
        incoming_data: Dict[str, Any],
        source_url: Optional[str],
        source_name: Optional[str],
        db: AsyncSession
    ) -> List[VehicleUpdateHistory]:
        updates = []

        # Check for price change
        new_min_price = incoming_data.get("min_price") or incoming_data.get("reference_ex_showroom_min")
        if new_min_price and model.variants:
            current_min = min([float(v.reference_ex_showroom) for v in model.variants]) if model.variants else 0
            if abs(float(new_min_price) - current_min) > 1000:
                change = VehicleUpdateHistory(
                    vehicle_model_id=model.id,
                    change_type="PRICE_REVISION",
                    previous_data={"reference_min": current_min},
                    new_data={"reference_min": float(new_min_price)},
                    source_url=source_url,
                    source_name=source_name,
                    changed_at=datetime.now(timezone.utc)
                )
                db.add(change)
                updates.append(change)

        # Check for variant additions
        incoming_variants = incoming_data.get("variants", [])
        existing_names = {v.name.lower() for v in model.variants} if model.variants else set()
        new_variants = [v for v in incoming_variants if (v.get("name") or v.get("variant_name") or "").lower() not in existing_names]

        if new_variants:
            change = VehicleUpdateHistory(
                vehicle_model_id=model.id,
                change_type="NEW_VARIANT",
                previous_data={"variant_count": len(model.variants) if model.variants else 0},
                new_data={"new_variants": [v.get("name") or v.get("variant_name") for v in new_variants]},
                source_url=source_url,
                source_name=source_name,
                changed_at=datetime.now(timezone.utc)
            )
            db.add(change)
            updates.append(change)

        if updates:
            await db.commit()

        return updates

