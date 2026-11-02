from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from backend.app.core.database import get_db
from backend.app.models.models import City, VehicleCategory, VehicleBrand, VehicleModel, VehicleVariant, BuyingGroup
from backend.app.schemas.schemas import (
    CityResponse,
    VehicleCategoryResponse,
    VehicleBrandResponse,
    VehicleModelResponse,
    VehicleVariantResponse
)

router = APIRouter(prefix="/catalog", tags=["Vehicle Catalog"])

@router.get("/cities", response_model=List[CityResponse])
async def list_cities(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(City).where(City.is_active == True).order_by(City.name))
    return res.scalars().all()

@router.get("/categories", response_model=List[VehicleCategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(VehicleCategory).order_by(VehicleCategory.display_order))
    return res.scalars().all()

@router.get("/brands", response_model=List[VehicleBrandResponse])
async def list_brands(
    category_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(VehicleBrand).order_by(VehicleBrand.name)
    if category_id:
        query = query.join(VehicleCategory, VehicleBrand.category_id == VehicleCategory.id).where(
            or_(VehicleBrand.category_id == category_id, VehicleCategory.slug == category_id)
        )
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/models")
async def list_models(
    category_id: Optional[str] = Query(None),
    brand_id: Optional[str] = Query(None),
    body_type: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(VehicleModel)
        .options(
            selectinload(VehicleModel.brand).selectinload(VehicleBrand.category),
            selectinload(VehicleModel.variants)
        )
        .where(VehicleModel.is_active == True)
    )

    if brand_id:
        query = query.where(VehicleModel.brand_id == brand_id)
    if body_type:
        query = query.where(VehicleModel.body_type == body_type)
    if search:
        query = query.where(VehicleModel.name.ilike(f"%{search}%"))

    res = await db.execute(query)
    models = res.scalars().all()

    # Hydrate rich data
    output = []
    for m in models:
        # Filter category if specified (accepts both UUID and slug)
        if category_id and m.brand.category_id != category_id and m.brand.category.slug != category_id:
            continue

        # Filter fuel_type if specified
        if fuel_type:
            has_fuel = any(v.fuel_type.upper() == fuel_type.upper() for v in m.variants)
            if not has_fuel:
                continue

        # Count active buying groups for this model's variants
        variant_ids = [v.id for v in m.variants]
        groups_count = 0
        if variant_ids:
            cnt_res = await db.execute(
                select(func.count(BuyingGroup.id)).where(
                    BuyingGroup.vehicle_variant_id.in_(variant_ids),
                    BuyingGroup.status.in_(["OPEN", "QUALIFYING", "READY_FOR_BIDDING", "BIDDING_OPEN", "OFFERS_AVAILABLE"])
                )
            )
            groups_count = cnt_res.scalar() or 0

        # Calculate reference price range
        prices = [float(v.reference_ex_showroom) for v in m.variants]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        output.append({
            "id": m.id,
            "brand_id": m.brand_id,
            "brand_name": m.brand.name,
            "category_slug": m.brand.category.slug,
            "name": m.name,
            "slug": m.slug,
            "body_type": m.body_type,
            "image_url": m.image_url,
            "is_active": m.is_active,
            "min_price": min_price,
            "max_price": max_price,
            "variants_count": len(m.variants),
            "active_groups_count": groups_count,
            "variants": [
                {
                    "id": v.id,
                    "name": v.name,
                    "fuel_type": v.fuel_type,
                    "transmission": v.transmission,
                    "reference_ex_showroom": float(v.reference_ex_showroom),
                    "engine_cc_or_battery_kwh": v.engine_cc_or_battery_kwh,
                    "specifications": v.specifications
                }
                for v in m.variants if v.is_active
            ]
        })

    return output

@router.get("/models/{id}")
async def get_model(id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(VehicleModel)
        .options(
            selectinload(VehicleModel.brand).selectinload(VehicleBrand.category),
            selectinload(VehicleModel.variants)
        )
        .where(VehicleModel.id == id)
    )
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Vehicle model not found")

    variant_ids = [v.id for v in m.variants]
    groups_res = await db.execute(
        select(BuyingGroup)
        .options(selectinload(BuyingGroup.city), selectinload(BuyingGroup.variant))
        .where(
            BuyingGroup.vehicle_variant_id.in_(variant_ids),
            BuyingGroup.status.in_(["OPEN", "QUALIFYING", "READY_FOR_BIDDING", "BIDDING_OPEN", "OFFERS_AVAILABLE"])
        )
    )
    active_groups = groups_res.scalars().all()

    return {
        "id": m.id,
        "name": m.name,
        "slug": m.slug,
        "body_type": m.body_type,
        "image_url": m.image_url,
        "brand": {
            "id": m.brand.id,
            "name": m.brand.name,
            "logo_url": m.brand.logo_url,
            "category_name": m.brand.category.name,
            "category_slug": m.brand.category.slug
        },
        "variants": [
            {
                "id": v.id,
                "name": v.name,
                "fuel_type": v.fuel_type,
                "transmission": v.transmission,
                "seating_capacity": v.seating_capacity,
                "engine_cc_or_battery_kwh": v.engine_cc_or_battery_kwh,
                "reference_ex_showroom": float(v.reference_ex_showroom),
                "specifications": v.specifications
            }
            for v in m.variants if v.is_active
        ],
        "active_groups": [
            {
                "id": g.id,
                "group_code": g.group_code,
                "variant_name": g.variant.name,
                "city_name": g.city.name,
                "current_members_count": g.current_members_count,
                "target_members": g.target_members,
                "status": g.status,
                "target_purchase_timeline": g.target_purchase_timeline
            }
            for g in active_groups
        ]
    }

@router.get("/variants/{id}", response_model=VehicleVariantResponse)
async def get_variant(id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(VehicleVariant).where(VehicleVariant.id == id))
    v = res.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Variant not found")
    return v

