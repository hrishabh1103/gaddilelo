from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.models.models import (
    VehicleDiscoveryJob, VehicleDiscoveryRecord, VehicleDataSource,
    VehicleUpdateHistory, VehiclePriceHistory, VehicleSpecificationSource,
    VehicleImage, VehicleDiscoverySubscription, VehicleDatasetSync,
    VehicleModel, VehicleVariant, VehicleBrand, VehicleCategory, User
)
from backend.app.schemas.schemas import (
    CustomerDiscoveryRequest, VehicleDiscoveryJobResponse,
    VehicleDiscoveryRecordResponse, VehicleDiscoveryRecordDetail,
    VehicleDiscoveryApprovalRequest, VehicleDataSourceCreate,
    VehicleDataSourceUpdate, VehicleDataSourceResponse,
    VehicleIntelligenceOverviewStats, VehiclePriceHistoryResponse,
    VehicleUpdateHistoryResponse
)
from backend.app.services.vehicle_intelligence import (
    SearchService, DiscoveryService, SourceRegistry,
    VehiclesDBService, WikimediaImageService, WikidataEnricher,
    IndianGovernmentDataService, OEMSpecificationRegistry, MeterAppService
)
from backend.app.api.deps import get_current_user_optional, require_admin

router = APIRouter(prefix="/intelligence", tags=["Vehicle Intelligence & Discovery"])

# ====================================================================
# 1. PUBLIC & CUSTOMER DISCOVERY ENDPOINTS
# ====================================================================

@router.get("/search")
async def search_vehicles_with_discovery(
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Two-stage search: Queries internal catalogue first. If no results,
    suggests customer-triggered automated discovery.
    """
    res = await SearchService.search_catalogue(query=q, category_slug=category, db=db)
    return res.to_dict()


@router.post("/discovery-requests")
async def submit_discovery_request(
    request: CustomerDiscoveryRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Customer requests discovery of an unlisted vehicle.
    Queries authorized sources, extracts specifications, checks duplicates,
    and queues for admin review.
    """
    user_id = current_user.id if current_user else None
    result = await DiscoveryService.create_customer_discovery_request(
        search_query=request.search_query,
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        category_slug=request.category_slug,
        target_city_id=request.target_city_id,
        user_id=user_id,
        db=db
    )
    return result


@router.get("/discovery-requests/{job_id}", response_model=VehicleDiscoveryJobResponse)
async def get_discovery_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    job_res = await db.execute(select(VehicleDiscoveryJob).where(VehicleDiscoveryJob.id == job_id))
    job = job_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Discovery job not found")
    return job


# ====================================================================
# 2. ADMIN VEHICLE INTELLIGENCE DASHBOARD ENDPOINTS
# ====================================================================

@router.get("/overview", response_model=VehicleIntelligenceOverviewStats)
async def get_intelligence_overview(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    total_disc = await db.execute(select(func.count(VehicleDiscoveryRecord.id)))
    pending_cnt = await db.execute(
        select(func.count(VehicleDiscoveryRecord.id)).where(VehicleDiscoveryRecord.review_status == "PENDING_REVIEW")
    )
    approved_cnt = await db.execute(
        select(func.count(VehicleDiscoveryRecord.id)).where(VehicleDiscoveryRecord.review_status == "APPROVED")
    )
    rejected_cnt = await db.execute(
        select(func.count(VehicleDiscoveryRecord.id)).where(VehicleDiscoveryRecord.review_status == "REJECTED")
    )
    active_sources_cnt = await db.execute(
        select(func.count(VehicleDataSource.id)).where(VehicleDataSource.enabled == True)
    )
    failed_jobs_cnt = await db.execute(
        select(func.count(VehicleDiscoveryJob.id)).where(VehicleDiscoveryJob.status == "FAILED")
    )
    total_requests_cnt = await db.execute(
        select(func.count(VehicleDiscoverySubscription.id))
    )

    return VehicleIntelligenceOverviewStats(
        total_discovered_vehicles=total_disc.scalar() or 0,
        pending_review_count=pending_cnt.scalar() or 0,
        approved_count=approved_cnt.scalar() or 0,
        rejected_count=rejected_cnt.scalar() or 0,
        active_sources_count=active_sources_cnt.scalar() or 0,
        failed_jobs_count=failed_jobs_cnt.scalar() or 0,
        total_customer_discovery_requests=total_requests_cnt.scalar() or 0
    )


@router.get("/queue", response_model=List[VehicleDiscoveryRecordResponse])
async def list_discovery_queue(
    review_status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(VehicleDiscoveryRecord).order_by(desc(VehicleDiscoveryRecord.created_at)).limit(limit)
    if review_status:
        query = query.where(VehicleDiscoveryRecord.review_status == review_status)
    if category:
        query = query.where(VehicleDiscoveryRecord.category_slug == category)

    res = await db.execute(query)
    return res.scalars().all()


@router.get("/records/{record_id}", response_model=VehicleDiscoveryRecordDetail)
async def get_discovery_record_detail(
    record_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(VehicleDiscoveryRecord)
        .options(
            selectinload(VehicleDiscoveryRecord.spec_sources),
            selectinload(VehicleDiscoveryRecord.price_histories),
            selectinload(VehicleDiscoveryRecord.images),
            selectinload(VehicleDiscoveryRecord.subscriptions)
        )
        .where(VehicleDiscoveryRecord.id == record_id)
    )
    res = await db.execute(stmt)
    rec = res.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Discovery record not found")

    spec_sources_out = [
        {
            "field_name": s.field_name,
            "field_value": s.field_value,
            "unit": s.unit,
            "source_url": s.source_url,
            "source_name": s.source_name,
            "confidence": float(s.confidence_score),
            "is_conflict": s.is_conflict
        }
        for s in rec.spec_sources
    ]

    images_out = [
        {
            "id": img.id,
            "image_url": img.image_url,
            "source_url": img.source_url,
            "usage_rights_status": img.usage_rights_status,
            "is_primary": img.is_primary
        }
        for img in rec.images
    ]

    price_histories_out = [
        {
            "id": p.id,
            "amount": float(p.amount),
            "currency": p.currency,
            "price_type": p.price_type,
            "source_url": p.source_url
        }
        for p in rec.price_histories
    ]

    return VehicleDiscoveryRecordDetail(
        id=rec.id,
        job_id=rec.job_id,
        discovered_brand=rec.discovered_brand,
        discovered_model=rec.discovered_model,
        category_slug=rec.category_slug,
        body_type=rec.body_type,
        launch_status=rec.launch_status,
        model_year=rec.model_year,
        reference_ex_showroom_min=rec.reference_ex_showroom_min,
        reference_ex_showroom_max=rec.reference_ex_showroom_max,
        confidence_score=rec.confidence_score,
        review_status=rec.review_status,
        primary_source_url=rec.primary_source_url,
        primary_source_name=rec.primary_source_name,
        published_model_id=rec.published_model_id,
        created_at=rec.created_at,
        extracted_data=rec.extracted_data or {},
        admin_notes=rec.admin_notes,
        subscribers_count=len(rec.subscriptions),
        spec_sources=spec_sources_out,
        price_histories=price_histories_out,
        images=images_out
    )


@router.post("/records/{record_id}/approve")
async def approve_discovery_record(
    record_id: str,
    approval: VehicleDiscoveryApprovalRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin verifies and approves a discovered vehicle.
    Publishes to the live vehicle catalogue and notifies all subscribers.
    """
    try:
        model = await DiscoveryService.approve_and_publish_record(
            record_id=record_id,
            reviewer_user_id=current_user.id,
            admin_notes=approval.admin_notes,
            db=db
        )
        return {
            "status": "APPROVED",
            "published_model_id": model.id,
            "model_name": model.name,
            "message": f"Successfully published '{model.name}' to vehicle catalogue. Subscribed customers have been notified."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/{record_id}/reject")
async def reject_discovery_record(
    record_id: str,
    approval: VehicleDiscoveryApprovalRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    try:
        rec = await DiscoveryService.reject_record(
            record_id=record_id,
            reviewer_user_id=current_user.id,
            admin_notes=approval.admin_notes,
            db=db
        )
        return {"status": "REJECTED", "record_id": rec.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/scan-now")
async def trigger_manual_scan(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers automated scan of all registered and enabled automotive sources.
    """
    scan_res = await DiscoveryService.run_scheduled_scan(db=db)
    return scan_res


@router.get("/sources", response_model=List[VehicleDataSourceResponse])
async def list_data_sources(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(VehicleDataSource).order_by(VehicleDataSource.source_name))
    sources = res.scalars().all()
    
    # If table empty, seed default providers into database
    if not sources:
        default_sources = [
            VehicleDataSource(
                source_name="Authorized Indian OEM Newsroom",
                source_url="https://press.gaadilelo.com/oem",
                source_type="MANUFACTURER_WEBSITE",
                access_method="RSS_FEED",
                licensing_status="OFFICIAL_PUBLIC",
                enabled=True,
                update_frequency="DAILY"
            ),
            VehicleDataSource(
                source_name="Tata Motors Official Pressroom",
                source_url="https://www.tatamotors.com/media/press-releases",
                source_type="PRESS_RELEASE",
                access_method="RSS_FEED",
                licensing_status="OFFICIAL_PUBLIC",
                enabled=True,
                update_frequency="DAILY"
            ),
            VehicleDataSource(
                source_name="Mahindra Automotive Media Center",
                source_url="https://auto.mahindra.com/newsroom",
                source_type="PRESS_RELEASE",
                access_method="RSS_FEED",
                licensing_status="OFFICIAL_PUBLIC",
                enabled=True,
                update_frequency="DAILY"
            )
        ]
        db.add_all(default_sources)
        await db.commit()
        res = await db.execute(select(VehicleDataSource).order_by(VehicleDataSource.source_name))
        sources = res.scalars().all()

    return sources


@router.post("/sources", response_model=VehicleDataSourceResponse)
async def create_data_source(
    data: VehicleDataSourceCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    source = VehicleDataSource(**data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.put("/sources/{source_id}", response_model=VehicleDataSourceResponse)
async def update_data_source(
    source_id: str,
    data: VehicleDataSourceUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(VehicleDataSource).where(VehicleDataSource.id == source_id))
    source = res.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(source, k, v)

    await db.commit()
    await db.refresh(source)
    return source


@router.get("/history", response_model=List[VehicleUpdateHistoryResponse])
async def list_vehicle_update_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(VehicleUpdateHistory)
        .options(selectinload(VehicleUpdateHistory.model))
        .order_by(desc(VehicleUpdateHistory.changed_at))
        .limit(limit)
    )
    res = await db.execute(stmt)
    updates = res.scalars().all()

    out = []
    for u in updates:
        out.append(
            VehicleUpdateHistoryResponse(
                id=u.id,
                vehicle_model_id=u.vehicle_model_id,
                model_name=u.model.name if u.model else "Catalog Item",
                change_type=u.change_type,
                previous_data=u.previous_data,
                new_data=u.new_data,
                source_url=u.source_url,
                source_name=u.source_name,
                changed_at=u.changed_at
            )
        )
    return out


# ====================================================================
# 4. FREE DATASET SYNC & REPORTING ENDPOINTS
# ====================================================================

@router.post("/sync/vehiclesdb")
async def trigger_vehiclesdb_sync(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers incremental synchronization from the VehiclesDB open dataset (CC BY 4.0).
    Imports Indian-market manufacturers and models without paid API dependencies.
    """
    result = await VehiclesDBService.sync_incremental(db=db)
    return result


@router.post("/models/{model_id}/enrich-wikidata")
async def enrich_model_via_wikidata(
    model_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Enriches an existing vehicle model with structured Wikidata properties (dimensions, QID).
    """
    result = await WikidataEnricher.enrich_model(model_id=model_id, db=db)
    return result


@router.post("/models/{model_id}/discover-images")
async def discover_wikimedia_images(
    model_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Searches and links free Wikimedia Commons images for a vehicle model with license validation.
    """
    attached = await WikimediaImageService.attach_images_to_model(model_id=model_id, db=db)
    return {
        "model_id": model_id,
        "images_attached": len(attached),
        "images": [
            {
                "id": img.id,
                "url": img.image_url,
                "thumbnail_url": img.thumbnail_url,
                "license": img.license_name,
                "author": img.author_name,
                "attribution_html": img.attribution_html
            }
            for img in attached
        ]
    }


@router.get("/datasets")
async def list_dataset_syncs(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Lists status and history of free dataset synchronizations."""
    res = await db.execute(select(VehicleDatasetSync).order_by(desc(VehicleDatasetSync.started_at)).limit(20))
    syncs = res.scalars().all()
    return [
        {
            "id": s.id,
            "dataset_name": s.dataset_name,
            "records_processed": s.records_processed,
            "records_imported": s.records_imported,
            "records_updated": s.records_updated,
            "status": s.status,
            "started_at": s.started_at,
            "completed_at": s.completed_at,
            "sync_metadata": s.sync_metadata
        }
        for s in syncs
    ]


@router.get("/reports/coverage")
async def get_coverage_report(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Reports vehicle catalogue coverage by category and manufacturer.
    """
    # Categories count
    cats_res = await db.execute(select(VehicleCategory))
    categories = cats_res.scalars().all()

    coverage_by_category = []
    for cat in categories:
        models_count = await db.execute(
            select(func.count(VehicleModel.id))
            .join(VehicleBrand, VehicleModel.brand_id == VehicleBrand.id)
            .where(VehicleBrand.category_id == cat.id)
        )
        coverage_by_category.append({
            "category_name": cat.name,
            "category_slug": cat.slug,
            "models_count": models_count.scalar() or 0
        })

    # Brands count
    brands_res = await db.execute(
        select(VehicleBrand.name, func.count(VehicleModel.id))
        .join(VehicleModel, VehicleModel.brand_id == VehicleBrand.id)
        .group_by(VehicleBrand.name)
        .order_by(desc(func.count(VehicleModel.id)))
    )
    brand_counts = [{"brand": r[0], "models_count": r[1]} for r in brands_res.all()]

    return {
        "categories": coverage_by_category,
        "brands": brand_counts
    }


@router.get("/reports/missing-images")
async def get_missing_images_report(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists catalog vehicles currently lacking verified images.
    """
    res = await db.execute(
        select(VehicleModel)
        .options(selectinload(VehicleModel.brand), selectinload(VehicleModel.images))
        .where(VehicleModel.is_active == True)
    )
    models = res.scalars().all()
    missing = []
    for m in models:
        verified_images = [img for img in m.images if img.verification_status == "VERIFIED"]
        if not verified_images and (not m.image_url or "unsplash" in m.image_url):
            missing.append({
                "model_id": m.id,
                "model_name": m.name,
                "brand_name": m.brand.name if m.brand else "Unknown",
                "body_type": m.body_type,
                "has_placeholder": bool(m.image_url)
            })
    return {"total_missing": len(missing), "models": missing}


@router.get("/reports/missing-specs")
async def get_missing_specs_report(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists vehicle models or variants lacking verified technical specifications (dimensions, safety rating, range).
    """
    res = await db.execute(
        select(VehicleModel)
        .options(selectinload(VehicleModel.brand), selectinload(VehicleModel.variants))
        .where(VehicleModel.is_active == True)
    )
    models = res.scalars().all()
    missing = []
    for m in models:
        issues = []
        if not m.length_mm or not m.width_mm or not m.height_mm:
            issues.append("Missing physical dimensions (length/width/height)")
        if not m.safety_rating_stars:
            issues.append("Awaiting safety rating (Bharat NCAP / Global NCAP)")
        for v in m.variants:
            if v.fuel_type == "ELECTRIC" and not v.claimed_range_km:
                issues.append(f"Variant '{v.name}' missing claimed EV range")

        if issues:
            missing.append({
                "model_id": m.id,
                "model_name": m.name,
                "brand_name": m.brand.name if m.brand else "Unknown",
                "issues": issues
            })
    return {"total_with_missing_specs": len(missing), "models": missing}


@router.get("/reports/conflicts")
async def get_data_conflicts_report(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists active specification discrepancies flagged across multiple sources for admin review.
    """
    res = await db.execute(
        select(VehicleSpecificationSource)
        .where(VehicleSpecificationSource.is_conflict == True)
        .order_by(desc(VehicleSpecificationSource.created_at))
    )
    conflicts = res.scalars().all()
    return [
        {
            "id": c.id,
            "field_name": c.field_name,
            "field_value": c.field_value,
            "source_url": c.source_url,
            "source_name": c.source_name,
            "created_at": c.created_at
        }
        for c in conflicts
    ]


# ====================================================================
# 8. METERAPP CANONICAL CATALOGUE & ADMIN MANAGEMENT
# ====================================================================

@router.post("/meterapp/preview")
async def preview_meterapp_import(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates an import preview from MeterApp (@meterapp/vehicle-db, ISC License)
    without modifying production database records.
    """
    return await MeterAppService.preview_import(db)


@router.post("/meterapp/sync")
async def sync_meterapp_catalogue(
    limit: Optional[int] = Query(None, description="Optional cap on new models to import"),
    auto_enrich_images: bool = Query(False, description="Whether to query Wikimedia Commons for images"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes incremental synchronization of the MeterApp Indian vehicle catalogue:
    - Normalizes canonical makes, models, and categories.
    - Zero-loss deduplication preserving existing verified variants and buying groups.
    - Attaches clean OEM specifications and variants.
    - Records provenance, timestamps, and ISC licensing.
    """
    return await MeterAppService.sync_incremental(
        db=db,
        auto_enrich_images=auto_enrich_images,
        limit_new_models=limit
    )


@router.get("/admin/catalogue-summary")
async def get_admin_catalogue_summary(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Provides administrative catalogue health and provenance telemetry:
    - Total imported makes & models
    - Deduplicated records
    - Missing variants, missing specs, missing images
    - Source provenance breakdown (MeterApp vs VehiclesDB vs OEM)
    - Sync history and verification timestamps
    """
    return await MeterAppService.get_catalogue_summary(db)


