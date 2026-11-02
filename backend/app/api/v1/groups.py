from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.models.models import (
    BuyingGroup, GroupMember, VehicleVariant, VehicleModel, VehicleBrand,
    VehicleCategory, City, Quotation, Dealer, User
)
from backend.app.schemas.schemas import (
    BuyingGroupCreate, BuyingGroupResponse, QuotationResponse
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

@router.post("", response_model=BuyingGroupResponse)
async def create_buying_group(
    payload: BuyingGroupCreate,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    group = await GroupEngine.create_group(
        db=db,
        creator_user_id=current_user.id,
        variant_id=payload.vehicle_variant_id,
        city_id=payload.city_id,
        target_members=payload.target_members,
        timeline=payload.target_purchase_timeline,
        notes=payload.additional_notes
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
    notes: Optional[str] = None,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    group = await GroupEngine.join_group(
        db=db,
        group_id=id,
        user_id=current_user.id,
        notes=notes
    )

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

