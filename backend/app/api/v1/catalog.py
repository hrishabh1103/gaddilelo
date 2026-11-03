from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, exists
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
        cat_res = await db.execute(
            select(VehicleCategory).where(
                or_(VehicleCategory.id == category_id, VehicleCategory.slug == category_id)
            )
        )
        cat_obj = cat_res.scalar_one_or_none()
        c_id = cat_obj.id if cat_obj else category_id
        c_slug = cat_obj.slug if cat_obj else category_id

        cat_match = or_(VehicleBrand.category_id == c_id, VehicleCategory.slug == c_slug)
        has_model_in_cat = exists().where(
            VehicleModel.brand_id == VehicleBrand.id,
            VehicleModel.is_active == True,
            VehicleModel.vehicle_category_slug == c_slug
        )
        query = query.outerjoin(VehicleCategory, VehicleBrand.category_id == VehicleCategory.id).where(
            or_(cat_match, has_model_in_cat)
        ).distinct()
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/models")
async def list_models(
    category_id: Optional[str] = Query(None),
    brand_id: Optional[str] = Query(None),
    body_type: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(48, ge=1, le=500),
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
        search_term = search.strip()
        query = query.join(VehicleBrand, VehicleModel.brand_id == VehicleBrand.id).where(
            or_(
                VehicleModel.name.ilike(f"%{search_term}%"),
                VehicleBrand.name.ilike(f"%{search_term}%"),
                VehicleModel.canonical_brand_name.ilike(f"%{search_term}%"),
                VehicleModel.canonical_model_name.ilike(f"%{search_term}%")
            )
        )

    res = await db.execute(query)
    models = res.scalars().all()

    target_category_slug = None
    target_category_id = None
    if category_id:
        cat_res = await db.execute(
            select(VehicleCategory).where(
                or_(VehicleCategory.id == category_id, VehicleCategory.slug == category_id)
            )
        )
        cat_obj = cat_res.scalar_one_or_none()
        target_category_slug = cat_obj.slug if cat_obj else category_id
        target_category_id = cat_obj.id if cat_obj else category_id

    # Batch count active buying groups in a single query instead of N queries
    bg_counts_res = await db.execute(
        select(BuyingGroup.vehicle_variant_id, func.count(BuyingGroup.id))
        .where(BuyingGroup.status.in_(["OPEN", "QUALIFYING", "READY_FOR_BIDDING", "BIDDING_OPEN", "OFFERS_AVAILABLE"]))
        .group_by(BuyingGroup.vehicle_variant_id)
    )
    bg_count_map = dict(bg_counts_res.all())

    # Hydrate rich data
    output = []
    for m in models:
        # Filter category if specified
        if target_category_slug:
            if m.vehicle_category_slug:
                if m.vehicle_category_slug != target_category_slug:
                    continue
            else:
                if m.brand and m.brand.category_id != target_category_id and m.brand.category.slug != target_category_slug:
                    continue

        # Filter fuel_type if specified
        if fuel_type:
            has_fuel = any(v.fuel_type.upper() == fuel_type.upper() for v in m.variants)
            if not has_fuel:
                continue

        # Count active buying groups for this model variants (from pre-aggregated map)
        groups_count = sum(bg_count_map.get(v.id, 0) for v in m.variants)

        # Calculate reference price range
        prices = [float(v.reference_ex_showroom) for v in m.variants]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        placeholder = f"https://placehold.co/800x500/1e293b/ffffff?text={m.name.replace(' ', '+')}+%28GaadiLelo%29"
        output.append({
            "id": m.id,
            "brand_id": m.brand_id,
            "brand_name": m.brand.name,
            "category_slug": m.brand.category.slug,
            "name": m.name,
            "slug": m.slug,
            "body_type": m.body_type,
            "image_url": m.image_url or placeholder,
            "is_active": m.is_active,
            "safety_rating_stars": m.safety_rating_stars,
            "last_verified_at": m.last_verified_at,
            "min_price": min_price,
            "max_price": max_price,
            "variants_count": len([v for v in m.variants if v.is_active]),
            "active_groups_count": groups_count,
            "variants": [
                {
                    "id": v.id,
                    "name": v.name,
                    "fuel_type": v.fuel_type,
                    "transmission": v.transmission,
                    "reference_ex_showroom": float(v.reference_ex_showroom),
                    "engine_cc_or_battery_kwh": v.engine_cc_or_battery_kwh,
                    "claimed_range_km": float(v.claimed_range_km) if v.claimed_range_km else None,
                    "tested_range_km": float(v.tested_range_km) if v.tested_range_km else None,
                    "claimed_mileage_kmpl": float(v.claimed_mileage_kmpl) if v.claimed_mileage_kmpl else None,
                    "specifications": v.specifications
                }
                for v in m.variants if v.is_active
            ]
        })

    # Prioritize flagship Indian models and models with rich official variants first
    def model_priority(item):
        name_lower = item["name"].lower()
        v_count = item["variants_count"]
        # Indian flagship model names (including Top 50 bestsellers)
        is_flagship = any(tag in name_lower for tag in [
            "baleno", "nexon", "punch", "fronx", "wagon r", "wagonr", "dzire",
            "creta", "swift", "scorpio", "ertiga", "brezza", "celerio", "eeco",
            "venue", "seltos", "thar", "alto", "sonet", "bolero", "innova",
            "xuv 3xo", "xuv3xo", "xuv700", "grand vitara", "tiago", "hyryder",
            "aura", "carens", "i20", "altroz", "amaze", "tigor", "grand i10",
            "safari", "harrier", "kylaq", "exter", "elevate", "virtus", "slavia",
            "glanza", "taigun", "kushaq", "hector", "windsor", "magnite", "triber",
            "kiger", "fortuner", "alcazar", "xev", "be 6", "activa", "jupiter",
            "hunter", "classic", "splendor", "pulsar", "450x", "ace", "dost"
        ])
        if is_flagship and v_count > 0:
            return (0, -v_count, item["name"])
        elif v_count >= 2:
            return (1, -v_count, item["name"])
        elif v_count == 1:
            return (2, 0, item["name"])
        else:
            return (3, 0, item["name"])

    output.sort(key=model_priority)
    if limit is not None:
        output = output[:limit]
    return output

@router.get("/models/{id}")
async def get_model(id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(VehicleModel)
        .options(
            selectinload(VehicleModel.brand).selectinload(VehicleBrand.category),
            selectinload(VehicleModel.variants),
            selectinload(VehicleModel.images)
        )
        .where(VehicleModel.id == id)
    )
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="Vehicle model not found")

    # If model has 0 variants in database, automatically create baseline variants
    if not m.variants:
        is_2w = "two-wheeler" in (m.brand.category.slug or "")
        is_ev = "electric" in (m.brand.category.slug or "") or "electric" in (m.body_type or "").lower()

        default_v1 = VehicleVariant(
            model_id=m.id,
            name=f"{m.name} Standard (Manual)" if not is_2w else f"{m.name} Standard Drum",
            fuel_type="ELECTRIC" if is_ev else "PETROL",
            transmission="SINGLE_SPEED_EV" if is_ev else "MANUAL",
            seating_capacity=2 if is_2w else 5,
            engine_cc_or_battery_kwh="1.5L" if not is_2w else "125 cc",
            reference_ex_showroom=1150000.00 if not is_2w else 95000.00,
            specifications={"source": "Baseline Variant"},
            is_active=True
        )
        default_v2 = VehicleVariant(
            model_id=m.id,
            name=f"{m.name} Top (Automatic)" if not is_2w else f"{m.name} Deluxe Disc",
            fuel_type="ELECTRIC" if is_ev else "PETROL",
            transmission="SINGLE_SPEED_EV" if is_ev else ("AUTOMATIC" if not is_2w else "MANUAL"),
            seating_capacity=2 if is_2w else 5,
            engine_cc_or_battery_kwh="1.5L" if not is_2w else "125 cc",
            reference_ex_showroom=1350000.00 if not is_2w else 110000.00,
            specifications={"source": "Baseline Variant"},
            is_active=True
        )
        db.add_all([default_v1, default_v2])
        await db.commit()

        # Re-fetch with variants loaded
        res = await db.execute(
            select(VehicleModel)
            .options(
                selectinload(VehicleModel.brand).selectinload(VehicleBrand.category),
                selectinload(VehicleModel.variants),
                selectinload(VehicleModel.images)
            )
            .where(VehicleModel.id == id)
        )
        m = res.scalar_one()

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

    # Images formatted with Wikimedia attribution
    images_out = [
        {
            "id": img.id,
            "image_url": img.image_url,
            "thumbnail_url": img.thumbnail_url or img.image_url,
            "author_name": img.author_name,
            "license_name": img.license_name,
            "license_url": img.license_url,
            "attribution_html": img.attribution_html,
            "is_primary": img.is_primary
        }
        for img in m.images if img.verification_status == "VERIFIED"
    ]

    placeholder = f"https://placehold.co/800x500/1e293b/ffffff?text={m.name.replace(' ', '+')}+%28GaadiLelo%29"
    return {
        "id": m.id,
        "name": m.name,
        "slug": m.slug,
        "body_type": m.body_type,
        "image_url": m.image_url or placeholder,
        "generation": m.generation,
        "model_year": m.model_year,
        "wikidata_id": m.wikidata_id,
        "last_verified_at": m.last_verified_at,
        "dimensions": {
            "length_mm": m.length_mm,
            "width_mm": m.width_mm,
            "height_mm": m.height_mm,
            "wheelbase_mm": m.wheelbase_mm,
            "ground_clearance_mm": m.ground_clearance_mm
        },
        "safety": {
            "stars": m.safety_rating_stars,
            "agency": m.safety_rating_agency
        },
        "images": images_out,
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
                "claimed_range_km": float(v.claimed_range_km) if v.claimed_range_km else None,
                "tested_range_km": float(v.tested_range_km) if v.tested_range_km else None,
                "real_world_range_km": float(v.real_world_range_km) if v.real_world_range_km else None,
                "claimed_mileage_kmpl": float(v.claimed_mileage_kmpl) if v.claimed_mileage_kmpl else None,
                "source_priority": v.source_priority,
                "last_verified_at": v.last_verified_at,
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

