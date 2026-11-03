from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import re

from backend.app.core.database import get_db
from backend.app.models.models import (
    BuyingGroup, GroupMember, VehicleVariant, VehicleModel, VehicleBrand,
    VehicleCategory, City, Quotation, Dealer, User, BuyerIntentConfirmation
)
from backend.app.schemas.schemas import (
    BuyingGroupCreate, BuyingGroupResponse, QuotationResponse, JoinGroupRequest
)
from backend.app.services.group_engine import GroupEngine
from backend.app.services.notification_service import NotificationService
from backend.app.api.deps import get_current_user, get_current_user_optional, require_buyer

router = APIRouter(prefix="/groups", tags=["Buying Groups"])

@router.get("", response_model=List[BuyingGroupResponse])
async def list_buying_groups(
    city_id: Optional[str] = Query(None),
    category_slug: Optional[str] = Query(None),
    brand_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(BuyingGroup)
        .options(
            selectinload(BuyingGroup.city),
            selectinload(BuyingGroup.variant)
            .selectinload(VehicleVariant.model)
            .selectinload(VehicleModel.brand)
            .selectinload(VehicleBrand.category),
            selectinload(BuyingGroup.members)
        )
        .order_by(BuyingGroup.created_at.desc())
    )

    if city_id:
        query = query.where(BuyingGroup.city_id == city_id)
    if status:
        query = query.where(BuyingGroup.status == status)
    else:
        # By default exclude CANCELLED from public discovery
        query = query.where(BuyingGroup.status != "CANCELLED")

    res = await db.execute(query)
    groups = res.scalars().all()

    output = []
    for g in groups:
        variant = g.variant
        model = variant.model
        brand = model.brand
        cat = brand.category

        if category_slug and cat.slug != category_slug:
            continue
        if brand_id and brand.id != brand_id:
            continue
        if search:
            search_str = f"{brand.name} {model.name} {variant.name} {g.group_code}".lower()
            if search.lower() not in search_str:
                continue

        # Check if current user is member
        is_member = False
        if current_user:
            is_member = any(m.user_id == current_user.id and m.status == "ACTIVE" for m in g.members)

        # Count approved quotations
        quote_cnt = await db.execute(
            select(func.count(Quotation.id)).where(
                Quotation.group_id == g.id,
                Quotation.status == "APPROVED"
            )
        )
        approved_quotes = quote_cnt.scalar() or 0

        output.append(
            BuyingGroupResponse(
                id=g.id,
                group_code=g.group_code,
                vehicle_variant_id=g.vehicle_variant_id,
                city_id=g.city_id,
                created_by_user_id=g.created_by_user_id,
                status=g.status,
                target_members=g.target_members,
                current_members_count=g.current_members_count,
                target_purchase_timeline=g.target_purchase_timeline,
                bidding_start_time=g.bidding_start_time,
                bidding_end_time=g.bidding_end_time,
                additional_notes=g.additional_notes,
                created_at=g.created_at,
                updated_at=g.updated_at,
                vehicle_name=f"{brand.name} {model.name}",
                brand_name=brand.name,
                variant_name=variant.name,
                vehicle_image_url=model.image_url,
                fuel_type=variant.fuel_type,
                transmission=variant.transmission,
                reference_ex_showroom=variant.reference_ex_showroom,
                city_name=g.city.name,
                is_current_user_member=is_member,
                approved_quotations_count=approved_quotes
            )
        )

    return output

@router.get("/{id}")
async def get_buying_group(
    id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(BuyingGroup)
        .options(
            selectinload(BuyingGroup.city),
            selectinload(BuyingGroup.variant)
            .selectinload(VehicleVariant.model)
            .selectinload(VehicleModel.brand),
            selectinload(BuyingGroup.members)
        )
        .where(BuyingGroup.id == id)
    )
    g = res.scalar_one_or_none()
    if not g:
        raise HTTPException(status_code=404, detail="Buying group not found")

    is_member = False
    if current_user:
        is_member = any(m.user_id == current_user.id and m.status == "ACTIVE" for m in g.members)

    # Approved quotes count
    quote_cnt = await db.execute(
        select(func.count(Quotation.id)).where(
            Quotation.group_id == g.id,
            Quotation.status == "APPROVED"
        )
    )
    approved_quotes = quote_cnt.scalar() or 0

    return {
        "id": g.id,
        "group_code": g.group_code,
        "vehicle_variant_id": g.vehicle_variant_id,
        "city_id": g.city_id,
        "city_name": g.city.name,
        "status": g.status,
        "target_members": g.target_members,
        "current_members_count": g.current_members_count,
        "target_purchase_timeline": g.target_purchase_timeline,
        "bidding_start_time": g.bidding_start_time,
        "bidding_end_time": g.bidding_end_time,
        "additional_notes": g.additional_notes,
        "created_at": g.created_at,
        "vehicle": {
            "model_name": g.variant.model.name,
            "brand_name": g.variant.model.brand.name,
            "variant_name": g.variant.name,
            "image_url": g.variant.model.image_url,
            "fuel_type": g.variant.fuel_type,
            "transmission": g.variant.transmission,
            "seating_capacity": g.variant.seating_capacity,
            "engine_cc_or_battery_kwh": g.variant.engine_cc_or_battery_kwh,
            "reference_ex_showroom": float(g.variant.reference_ex_showroom),
            "specifications": g.variant.specifications
        },
        "is_current_user_member": is_member,
        "approved_quotations_count": approved_quotes
        # NOTE: Buyer PII strictly excluded to preserve privacy requirement 9.
    }

async def enrich_and_discover_vehicle_background(
    model_id: str,
    brand_name: str,
    model_name: str,
    category_slug: Optional[str] = "car",
    user_id: Optional[str] = None
):
    """
    Asynchronously queries the vehicle intelligence engine (OEM, Wikimedia Commons, Wikidata)
    to discover specifications, dimensions, variants, and real photographic images from the internet,
    updating the newly created model in the catalog and notifying the user.
    """
    from backend.app.core.database import AsyncSessionLocal
    from backend.app.services.vehicle_intelligence.oem_adapters import OEMSpecificationRegistry
    from backend.app.services.vehicle_intelligence.wikimedia_image_service import WikimediaImageService
    from backend.app.services.vehicle_intelligence.wikidata_enricher import WikidataEnricher
    from backend.app.services.vehicle_intelligence.discovery_service import DiscoveryService
    from backend.app.models.models import VehicleModel, VehicleVariant, VehicleImage

    query = f"{brand_name} {model_name}".strip()
    print(f"[BACKGROUND DISCOVERY] Commencing automated internet discovery for: {query}")

    try:
        async with AsyncSessionLocal() as db:
            m_res = await db.execute(
                select(VehicleModel)
                .options(selectinload(VehicleModel.variants))
                .where(VehicleModel.id == model_id)
            )
            model = m_res.scalar_one_or_none()
            if not model:
                return

            # 1. Search OEM direct registry
            oem_match = OEMSpecificationRegistry.match_model(query)
            if oem_match:
                details = oem_match["details"]
                if details.get("length_mm"): model.length_mm = details["length_mm"]
                if details.get("width_mm"): model.width_mm = details["width_mm"]
                if details.get("height_mm"): model.height_mm = details["height_mm"]
                if details.get("wheelbase_mm"): model.wheelbase_mm = details["wheelbase_mm"]
                if details.get("ground_clearance_mm"): model.ground_clearance_mm = details["ground_clearance_mm"]
                if details.get("safety_rating"):
                    model.safety_rating_stars = details["safety_rating"]
                    model.safety_rating_agency = details.get("safety_agency", "BHARAT_NCAP")

                # Add OEM variants if any
                for v in details.get("variants", []):
                    existing_v = any(ev.name.lower() == v["name"].lower() for ev in model.variants)
                    if not existing_v:
                        new_v = VehicleVariant(
                            model_id=model.id,
                            name=v["name"],
                            fuel_type=v.get("fuel", "PETROL"),
                            transmission=v.get("trans", "MANUAL"),
                            seating_capacity=v.get("seating", 5),
                            engine_cc_or_battery_kwh=v.get("engine") or v.get("battery"),
                            reference_ex_showroom=Decimal(str(v.get("price", 1000000))),
                            claimed_range_km=Decimal(str(v["range_claimed"])) if v.get("range_claimed") else None,
                            tested_range_km=Decimal(str(v["range_tested"])) if v.get("range_tested") else None,
                            claimed_mileage_kmpl=Decimal(str(v["mileage"])) if v.get("mileage") else None,
                            specifications=v,
                            source_priority=1,
                            last_verified_at=datetime.now(timezone.utc),
                            is_active=True
                        )
                        db.add(new_v)

            # 2. Search Wikimedia Commons for real photography
            try:
                wiki_images = await WikimediaImageService.search_vehicle_images(brand_name, model_name, limit=3)
                if wiki_images:
                    primary = wiki_images[0]
                    model.image_url = primary["image_url"]
                    for wimg in wiki_images:
                        db.add(VehicleImage(
                            vehicle_model_id=model.id,
                            image_url=wimg["image_url"],
                            thumbnail_url=wimg.get("thumbnail_url"),
                            source_url=wimg["source_url"],
                            source_page_url=wimg.get("source_page_url"),
                            author_name=wimg.get("author_name"),
                            license_name=wimg.get("license_name"),
                            license_url=wimg.get("license_url"),
                            attribution_html=wimg.get("attribution_html"),
                            usage_rights_status="PUBLIC_COMMONS",
                            verification_status="VERIFIED",
                            width=wimg.get("width"),
                            height=wimg.get("height")
                        ))
            except Exception as e:
                print(f"[BACKGROUND DISCOVERY] Wikimedia image fetch error: {e}")

            # 3. Search Wikidata
            try:
                wiki_entity = await WikidataEnricher.search_entity(query)
                if wiki_entity and wiki_entity.get("id"):
                    model.wikidata_id = wiki_entity["id"]
            except Exception as e:
                print(f"[BACKGROUND DISCOVERY] Wikidata search error: {e}")

            # 4. Trigger Customer Discovery Request record for audit trail
            try:
                await DiscoveryService.create_customer_discovery_request(
                    search_query=query,
                    customer_name="Group Initiator",
                    customer_email="buyer@gaadilelo.com",
                    customer_phone=None,
                    category_slug=category_slug,
                    target_city_id=None,
                    user_id=user_id,
                    db=db
                )
            except Exception as e:
                print(f"[BACKGROUND DISCOVERY] Discovery dossier creation note: {e}")

            model.last_verified_at = datetime.now(timezone.utc)
            await db.commit()
            print(f"[BACKGROUND DISCOVERY] Successfully enriched {brand_name} {model_name} with specifications & real images!")
    except Exception as ex:
        print(f"[BACKGROUND DISCOVERY] Error during background discovery: {ex}")

@router.post("", response_model=BuyingGroupResponse)
async def create_buying_group(
    payload: BuyingGroupCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    variant_id = payload.vehicle_variant_id
    needs_discovery = False
    custom_model_id = None
    custom_brand_name = None
    custom_model_name = None
    category_slug = "car"

    # Check if this is a custom vehicle submission ("OTHER" or custom brand/model provided)
    if not variant_id or variant_id in ("custom", "other", "") or payload.custom_model_name:
        if not payload.custom_model_name:
            raise HTTPException(status_code=400, detail="Custom vehicle model name is required")

        # 1. Resolve Category
        cat = None
        if payload.category_id:
            cat_res = await db.execute(select(VehicleCategory).where(
                or_(VehicleCategory.id == payload.category_id, VehicleCategory.slug == payload.category_id)
            ))
            cat = cat_res.scalar_one_or_none()
        if not cat:
            cat_res = await db.execute(select(VehicleCategory).where(VehicleCategory.slug == "car"))
            cat = cat_res.scalar_one_or_none()
            if not cat:
                cat_res = await db.execute(select(VehicleCategory))
                cat = cat_res.scalars().first()
        category_slug = cat.slug if cat else "car"

        # 2. Resolve or Create Brand
        b_name = (payload.custom_brand_name or "Custom Brand").strip()
        brand_res = await db.execute(select(VehicleBrand).where(VehicleBrand.name.ilike(b_name)))
        brand = brand_res.scalars().first()
        if not brand:
            brand_slug = re.sub(r'[^a-zA-Z0-9]+', '-', b_name.lower()).strip('-') or 'custom-brand'
            brand = VehicleBrand(
                name=b_name,
                slug=f"{brand_slug}-{uuid.uuid4().hex[:4]}",
                category_id=cat.id if cat else None
            )
            db.add(brand)
            await db.flush()

        # 3. Resolve or Create Model
        m_name = payload.custom_model_name.strip()
        model_res = await db.execute(
            select(VehicleModel).where(
                VehicleModel.brand_id == brand.id,
                VehicleModel.name.ilike(m_name)
            )
        )
        model = model_res.scalars().first()
        if not model:
            # Check if exists anywhere by name
            model_res2 = await db.execute(select(VehicleModel).where(VehicleModel.name.ilike(m_name)))
            model = model_res2.scalars().first()

        if not model:
            model_slug = re.sub(r'[^a-zA-Z0-9]+', '-', m_name.lower()).strip('-') or 'custom-model'
            is_ev = "electric" in m_name.lower() or "ev" in m_name.lower() or "electric" in category_slug
            model = VehicleModel(
                brand_id=brand.id,
                name=m_name,
                slug=f"{brand.slug}-{model_slug}-{uuid.uuid4().hex[:4]}",
                vehicle_category_slug="electric-vehicle" if is_ev else category_slug,
                body_type=payload.custom_body_type or ("Electric SUV" if is_ev else "Hatchback / SUV"),
                model_year=datetime.now().year,
                canonical_brand_name=brand.name,
                canonical_model_name=m_name,
                image_url=f"https://placehold.co/800x500/1e293b/ffffff?text={m_name.replace(' ', '+')}+%28Searching+Internet...%29",
                last_verified_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(model)
            await db.flush()

        custom_model_id = model.id
        custom_brand_name = brand.name
        custom_model_name = model.name
        needs_discovery = True

        # 4. Resolve or Create Variant
        v_name = (payload.custom_variant_name or f"{m_name} Standard").strip()
        variant_res = await db.execute(
            select(VehicleVariant).where(
                VehicleVariant.model_id == model.id,
                VehicleVariant.name.ilike(v_name)
            )
        )
        variant = variant_res.scalars().first()
        if not variant:
            # Check if any variant exists for this model
            any_v = await db.execute(select(VehicleVariant).where(VehicleVariant.model_id == model.id))
            variant = any_v.scalars().first()

        if not variant:
            fuel = payload.custom_fuel_type or ("ELECTRIC" if "electric" in m_name.lower() or "ev" in m_name.lower() else "PETROL")
            trans = "SINGLE_SPEED_EV" if fuel == "ELECTRIC" else "MANUAL"
            ref_price = Decimal(str(payload.estimated_price or (2200000.0 if fuel == "ELECTRIC" else 1150000.0)))
            variant = VehicleVariant(
                model_id=model.id,
                name=v_name,
                fuel_type=fuel,
                transmission=trans,
                seating_capacity=5,
                engine_cc_or_battery_kwh="79 kWh" if fuel == "ELECTRIC" else "1.5L",
                reference_ex_showroom=ref_price,
                is_active=True,
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(variant)
            await db.flush()

        variant_id = variant.id

    group = await GroupEngine.create_group(
        db=db,
        creator_user_id=current_user.id,
        variant_id=variant_id,
        city_id=payload.city_id,
        target_members=payload.target_members,
        timeline=payload.target_purchase_timeline,
        notes=payload.additional_notes
    )

    # Record Buyer Intent Affirmation (Requirement 6)
    intent = payload.buyer_intent
    db.add(BuyerIntentConfirmation(
        group_id=group.id,
        user_id=current_user.id,
        purchase_timeline=intent.purchase_timeline if intent else payload.target_purchase_timeline,
        is_genuine_intent=intent.is_genuine_intent if intent else True,
        is_non_binding_acknowledged=intent.is_non_binding_acknowledged if intent else True,
        agreed_to_contact=intent.agreed_to_contact if intent else True
    ))
    await db.commit()

    if needs_discovery and custom_model_id:
        background_tasks.add_task(
            enrich_and_discover_vehicle_background,
            custom_model_id,
            custom_brand_name,
            custom_model_name,
            category_slug,
            current_user.id
        )

    # In-App Notification
    await NotificationService.notify(
        db=db,
        user_id=current_user.id,
        title="Buying Group Created!",
        message=f"Your buying group {group.group_code} has been created and is now accepting buyers.",
        event_type="GROUP_CREATED",
        link_url=f"/groups/{group.id}"
    )

    # Load details for response
    return await get_group_response_object(db, group.id, current_user.id)

@router.post("/{id}/join")
async def join_buying_group(
    id: str,
    payload: Optional[JoinGroupRequest] = None,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    notes = payload.notes if payload else None
    intent = payload.buyer_intent if payload else None

    group = await GroupEngine.join_group(
        db=db,
        group_id=id,
        user_id=current_user.id,
        notes=notes
    )

    # Record Buyer Intent Affirmation for joining member
    db.add(BuyerIntentConfirmation(
        group_id=group.id,
        user_id=current_user.id,
        purchase_timeline=intent.purchase_timeline if intent else group.target_purchase_timeline,
        is_genuine_intent=intent.is_genuine_intent if intent else True,
        is_non_binding_acknowledged=intent.is_non_binding_acknowledged if intent else True,
        agreed_to_contact=intent.agreed_to_contact if intent else True
    ))
    await db.commit()

    # Notify member
    await NotificationService.notify(
        db=db,
        user_id=current_user.id,
        title="Joined Group Successfully",
        message=f"You joined buying group {group.group_code}. Total cohort members: {group.current_members_count}/{group.target_members}.",
        event_type="GROUP_JOINED",
        link_url=f"/groups/{group.id}"
    )

    # If reached milestone, notify creator
    if group.status == "QUALIFYING" and group.created_by_user_id != current_user.id:
        await NotificationService.notify(
            db=db,
            user_id=group.created_by_user_id,
            title="Group Target Milestone Reached!",
            message=f"Group {group.group_code} has reached its target of {group.target_members} members and entered the QUALIFYING phase.",
            event_type="MILESTONE_REACHED",
            link_url=f"/groups/{group.id}"
        )

    return {"message": "Successfully joined group", "group_status": group.status, "current_members": group.current_members_count}

@router.post("/{id}/leave")
async def leave_buying_group(
    id: str,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    group = await GroupEngine.leave_group(
        db=db,
        group_id=id,
        user_id=current_user.id
    )

    await NotificationService.notify(
        db=db,
        user_id=current_user.id,
        title="Withdrawn from Group",
        message=f"You have left buying group {group.group_code}.",
        event_type="GROUP_WITHDRAWN"
    )

    return {"message": "Successfully left group", "current_members": group.current_members_count}

@router.get("/{id}/offers", response_model=List[QuotationResponse])
async def get_group_offers(
    id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns approved dealer quotations for side-by-side comparison.
    Dealers can only see their own quote or approved public quotes.
    """
    res = await db.execute(
        select(Quotation)
        .options(selectinload(Quotation.dealer).selectinload(Dealer.city))
        .where(
            Quotation.group_id == id,
            Quotation.status == "APPROVED"
        )
        .order_by(Quotation.final_on_road_price.asc())
    )
    quotes = res.scalars().all()

    output = []
    for q in quotes:
        output.append(
            QuotationResponse(
                id=q.id,
                group_id=q.group_id,
                dealer_id=q.dealer_id,
                revision_number=q.revision_number,
                status=q.status,
                admin_review_notes=q.admin_review_notes,
                base_ex_showroom=q.base_ex_showroom,
                rto_road_tax=q.rto_road_tax,
                insurance_amount=q.insurance_amount,
                tcs_amount=q.tcs_amount,
                mfg_discount=q.mfg_discount,
                dealer_discount=q.dealer_discount,
                exchange_bonus=q.exchange_bonus,
                corporate_discount=q.corporate_discount,
                accessories_amount=q.accessories_amount,
                logistics_handling=q.logistics_handling,
                other_statutory_charges=q.other_statutory_charges,
                final_on_road_price=q.final_on_road_price,
                delivery_timeline_days=q.delivery_timeline_days,
                offer_valid_until=q.offer_valid_until,
                remarks=q.remarks,
                created_at=q.created_at,
                updated_at=q.updated_at,
                dealership_name=q.dealer.dealership_name,
                dealer_city=q.dealer.city.name
            )
        )
    return output

async def get_group_response_object(db: AsyncSession, group_id: str, current_user_id: str) -> BuyingGroupResponse:
    res = await db.execute(
        select(BuyingGroup)
        .options(
            selectinload(BuyingGroup.city),
            selectinload(BuyingGroup.variant)
            .selectinload(VehicleVariant.model)
            .selectinload(VehicleModel.brand),
            selectinload(BuyingGroup.members)
        )
        .where(BuyingGroup.id == group_id)
    )
    g = res.scalar_one()
    variant = g.variant
    model = variant.model
    brand = model.brand
    is_member = any(m.user_id == current_user_id and m.status == "ACTIVE" for m in g.members)

    return BuyingGroupResponse(
        id=g.id,
        group_code=g.group_code,
        vehicle_variant_id=g.vehicle_variant_id,
        city_id=g.city_id,
        created_by_user_id=g.created_by_user_id,
        status=g.status,
        target_members=g.target_members,
        current_members_count=g.current_members_count,
        target_purchase_timeline=g.target_purchase_timeline,
        bidding_start_time=g.bidding_start_time,
        bidding_end_time=g.bidding_end_time,
        additional_notes=g.additional_notes,
        created_at=g.created_at,
        updated_at=g.updated_at,
        vehicle_name=f"{brand.name} {model.name}",
        brand_name=brand.name,
        variant_name=variant.name,
        vehicle_image_url=model.image_url,
        fuel_type=variant.fuel_type,
        transmission=variant.transmission,
        reference_ex_showroom=variant.reference_ex_showroom,
        city_name=g.city.name,
        is_current_user_member=is_member,
        approved_quotations_count=0
    )

