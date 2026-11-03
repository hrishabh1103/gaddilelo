import re
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from backend.app.models.models import VehicleModel, VehicleBrand, VehicleVariant

class SearchResult:
    def __init__(self, found: bool, models: List[Dict[str, Any]], query: str, message: Optional[str] = None):
        self.found = found
        self.models = models
        self.query = query
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "found": self.found,
            "models_count": len(self.models),
            "models": self.models,
            "query": self.query,
            "message": self.message
        }


class SearchService:
    """
    Two-stage search service: Checks internal catalogue first, surfaces discovery option if not found.
    """

    @classmethod
    async def search_catalogue(
        cls,
        query: str,
        category_slug: Optional[str],
        db: AsyncSession
    ) -> SearchResult:
        clean_q = query.strip()
        if not clean_q:
            return SearchResult(found=True, models=[], query="", message="Empty search query")

        # Query internal vehicle models with brand and variants
        stmt = (
            select(VehicleModel)
            .join(VehicleBrand, VehicleModel.brand_id == VehicleBrand.id)
            .options(
                selectinload(VehicleModel.brand).selectinload(VehicleBrand.category),
                selectinload(VehicleModel.variants)
            )
            .where(
                VehicleModel.is_active == True,
                or_(
                    VehicleModel.name.ilike(f"%{clean_q}%"),
                    VehicleBrand.name.ilike(f"%{clean_q}%")
                )
            )
        )

        res = await db.execute(stmt)
        matched_models = res.scalars().all()

        # If matched by category filter if provided
        if category_slug:
            matched_models = [
                m for m in matched_models 
                if m.brand and m.brand.category and m.brand.category.slug == category_slug
            ]

        if matched_models:
            output = []
            for m in matched_models:
                prices = [float(v.reference_ex_showroom) for v in m.variants] if m.variants else [0]
                output.append({
                    "id": m.id,
                    "name": m.name,
                    "brand_name": m.brand.name if m.brand else "Unknown",
                    "category_slug": m.brand.category.slug if (m.brand and m.brand.category) else "car",
                    "body_type": m.body_type,
                    "image_url": m.image_url,
                    "min_price": min(prices) if prices else 0,
                    "max_price": max(prices) if prices else 0,
                    "variants_count": len(m.variants) if m.variants else 0
                })
            return SearchResult(
                found=True,
                models=output,
                query=clean_q,
                message=f"Found {len(output)} vehicle(s) in catalogue."
            )

        # Vehicle NOT FOUND in internal catalogue
        return SearchResult(
            found=False,
            models=[],
            query=clean_q,
            message="We couldn't find this vehicle in our catalogue. Let us discover it for you."
        )

