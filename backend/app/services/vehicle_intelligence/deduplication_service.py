import re
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.models.models import VehicleBrand, VehicleModel, VehicleVariant

class DeduplicationResult:
    def __init__(
        self,
        is_duplicate_model: bool,
        existing_model: Optional[VehicleModel],
        existing_brand: Optional[VehicleBrand],
        new_variants_count: int,
        matched_variants_count: int
    ):
        self.is_duplicate_model = is_duplicate_model
        self.existing_model = existing_model
        self.existing_brand = existing_brand
        self.new_variants_count = new_variants_count
        self.matched_variants_count = matched_variants_count


class DeduplicationService:
    """
    Identifies existing brands, models, and variants in the database to avoid duplication.
    """

    @staticmethod
    def normalize_key(text: str) -> str:
        if not text:
            return ""
        s = re.sub(r"[^a-zA-Z0-9]+", "", text.lower())
        return s

    @classmethod
    async def match_existing_vehicle(
        cls,
        brand_name: str,
        model_name: str,
        variants_candidate: list,
        db: AsyncSession
    ) -> DeduplicationResult:
        norm_brand = cls.normalize_key(brand_name)
        norm_model = cls.normalize_key(model_name)

        # 1. Look for existing Brand
        brands_res = await db.execute(select(VehicleBrand))
        brands = brands_res.scalars().all()
        matched_brand = None
        for b in brands:
            if cls.normalize_key(b.name) == norm_brand or norm_brand in cls.normalize_key(b.name):
                matched_brand = b
                break

        # 2. Look for existing Model
        matched_model = None
        if matched_brand:
            models_res = await db.execute(
                select(VehicleModel)
                .options(selectinload(VehicleModel.variants))
                .where(VehicleModel.brand_id == matched_brand.id)
            )
            models = models_res.scalars().all()
            for m in models:
                m_norm = cls.normalize_key(m.name)
                if m_norm == norm_model or norm_model in m_norm or m_norm in norm_model:
                    matched_model = m
                    break
        else:
            # Fallback scan across all models
            models_res = await db.execute(
                select(VehicleModel).options(selectinload(VehicleModel.variants))
            )
            for m in models_res.scalars().all():
                m_norm = cls.normalize_key(m.name)
                if m_norm == norm_model:
                    matched_model = m
                    break

        # 3. Check Variants if Model matched
        new_v_cnt = len(variants_candidate)
        matched_v_cnt = 0

        if matched_model and matched_model.variants:
            existing_v_names = {cls.normalize_key(v.name) for v in matched_model.variants}
            for cand in variants_candidate:
                cand_name = cls.normalize_key(cand.get("name") or cand.get("variant_name") or "")
                if cand_name in existing_v_names:
                    matched_v_cnt += 1
                    new_v_cnt -= 1

        is_dup = (matched_model is not None) and (new_v_cnt == 0)

        return DeduplicationResult(
            is_duplicate_model=is_dup,
            existing_model=matched_model,
            existing_brand=matched_brand,
            new_variants_count=max(0, new_v_cnt),
            matched_variants_count=matched_v_cnt
        )

