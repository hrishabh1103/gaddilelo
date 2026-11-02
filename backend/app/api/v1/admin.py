from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.models.models import (
    User, UserProfile, Dealer, DealerDocument, BuyingGroup, GroupMember,
    DealerGroupInvitation, Quotation, BuyerLead, VehicleVariant, VehicleModel,
    VehicleBrand, City, Complaint, AuditLog
)
from backend.app.schemas.schemas import (
    AdminOverviewStats, DealerVerificationUpdate, BuyingGroupStatusUpdate,
    InviteDealersRequest, QuotationResponse, AuditLogResponse
)
from backend.app.services.group_engine import GroupEngine
from backend.app.services.notification_service import NotificationService
from backend.app.api.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("/overview", response_model=AdminOverviewStats)
async def get_admin_overview(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Total registered buyers
    buyers_cnt = await db.execute(select(func.count(User.id)).where(User.role == "BUYER"))
    total_buyers = buyers_cnt.scalar() or 0

    # Dealership counts
    verified_dealers = await db.execute(
        select(func.count(Dealer.id)).where(Dealer.verification_status == "VERIFIED")
    )
    pending_dealers = await db.execute(
        select(func.count(Dealer.id)).where(Dealer.verification_status == "PENDING")
    )

    # Groups counts
    active_groups_cnt = await db.execute(
        select(func.count(BuyingGroup.id)).where(
            BuyingGroup.status.in_(["OPEN", "QUALIFYING", "READY_FOR_BIDDING", "BIDDING_OPEN", "OFFERS_AVAILABLE"])
        )
    )
    bidding_open_cnt = await db.execute(
        select(func.count(BuyingGroup.id)).where(BuyingGroup.status == "BIDDING_OPEN")
    )

    # Quotations counts
    quotes_submitted_cnt = await db.execute(select(func.count(Quotation.id)))
    approved_quotes_cnt = await db.execute(
        select(func.count(Quotation.id)).where(Quotation.status == "APPROVED")
    )

    # Leads & Conversions
    leads_cnt = await db.execute(select(func.count(BuyerLead.id)))
    conversions_cnt = await db.execute(
        select(func.count(BuyerLead.id)).where(BuyerLead.status == "PURCHASE_COMPLETED")
    )

    return AdminOverviewStats(
        total_buyers=total_buyers,
        verified_dealerships=verified_dealers.scalar() or 0,
        pending_dealerships=pending_dealers.scalar() or 0,
        active_groups=active_groups_cnt.scalar() or 0,
        bidding_open_groups=bidding_open_cnt.scalar() or 0,
        quotations_submitted=quotes_submitted_cnt.scalar() or 0,
        approved_quotations=approved_quotes_cnt.scalar() or 0,
        total_leads=leads_cnt.scalar() or 0,
        successful_conversions=conversions_cnt.scalar() or 0
    )

# DEALER MANAGEMENT
@router.get("/dealers")
async def list_dealers(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Dealer)
        .options(
            selectinload(Dealer.user).selectinload(User.profile),
            selectinload(Dealer.city),
            selectinload(Dealer.documents)
        )
        .order_by(Dealer.created_at.desc())
    )
    if status:
        query = query.where(Dealer.verification_status == status)

    res = await db.execute(query)
    dealers = res.scalars().all()

    return [
        {
            "id": d.id,
            "dealership_name": d.dealership_name,
            "legal_entity_name": d.legal_entity_name,
            "gstin": d.gstin,
            "city_name": d.city.name,
            "address": d.address,
            "authorized_brands": d.authorized_brands,
            "verification_status": d.verification_status,
            "verification_notes": d.verification_notes,
            "verified_at": d.verified_at,
            "contact_name": d.user.profile.full_name if d.user.profile else "",
            "contact_email": d.user.email,
            "contact_phone": d.user.phone,
            "documents_count": len(d.documents),
            "created_at": d.created_at
        }
        for d in dealers
    ]

@router.put("/dealers/{id}/verify")
async def verify_dealer(
    id: str,
    payload: DealerVerificationUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Dealer)
        .options(selectinload(Dealer.user))
        .where(Dealer.id == id)
    )
    dealer = res.scalar_one_or_none()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")

    dealer.verification_status = payload.verification_status
    dealer.verification_notes = payload.verification_notes
    if payload.verification_status == "VERIFIED":
        dealer.verified_at = datetime.now(timezone.utc)
        dealer.user.is_verified = True
    else:
        dealer.verified_at = None
        dealer.user.is_verified = False

    # Log audit
    audit = AuditLog(
        actor_user_id=current_user.id,
        action=f"DEALER_STATUS_{payload.verification_status}",
        entity_type="DEALER",
        entity_id=dealer.id,
        payload={"notes": payload.verification_notes}
    )
    db.add(audit)

    await db.commit()

    # Notify dealer
    msg = (
        f"Your dealership {dealer.dealership_name} has been verified! You can now participate in bidding groups."
        if payload.verification_status == "VERIFIED"
        else f"Dealership verification updated: {payload.verification_status}. Notes: {payload.verification_notes}"
    )
    await NotificationService.notify(
        db=db,
        user_id=dealer.user_id,
        title="Dealership Verification Update",
        message=msg,
        event_type="DEALER_VERIFICATION",
        link_url="/dealer/dashboard"
    )

    return {"message": f"Dealer verification updated to {payload.verification_status}"}

# GROUP MODERATION
@router.get("/groups")
async def list_admin_groups(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(BuyingGroup)
        .options(
            selectinload(BuyingGroup.city),
            selectinload(BuyingGroup.variant)
            .selectinload(VehicleVariant.model)
            .selectinload(VehicleModel.brand),
            selectinload(BuyingGroup.invitations),
            selectinload(BuyingGroup.quotations)
        )
        .order_by(BuyingGroup.created_at.desc())
    )
    if status:
        query = query.where(BuyingGroup.status == status)

    res = await db.execute(query)
    groups = res.scalars().all()

    return [
        {
            "id": g.id,
            "group_code": g.group_code,
            "vehicle_name": f"{g.variant.model.brand.name} {g.variant.model.name} {g.variant.name}",
            "city_name": g.city.name,
            "status": g.status,
            "current_members": g.current_members_count,
            "target_members": g.target_members,
            "target_purchase_timeline": g.target_purchase_timeline,
            "bidding_start_time": g.bidding_start_time,
            "bidding_end_time": g.bidding_end_time,
            "invited_dealers_count": len(g.invitations),
            "submitted_quotations_count": len(g.quotations),
            "approved_quotations_count": sum(1 for q in g.quotations if q.status == "APPROVED"),
            "created_at": g.created_at
        }
        for g in groups
    ]

@router.put("/groups/{id}/status")
async def update_group_status(
    id: str,
    payload: BuyingGroupStatusUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    group = await GroupEngine.update_status(
        db=db,
        group_id=id,
        new_status=payload.status,
        bidding_end_time=payload.bidding_end_time
    )

    # Log audit
    audit = AuditLog(
        actor_user_id=current_user.id,
        action=f"GROUP_STATUS_{payload.status}",
        entity_type="BUYING_GROUP",
        entity_id=group.id,
        payload={"new_status": payload.status}
    )
    db.add(audit)
    await db.commit()

    return {"message": f"Group status successfully updated to {group.status}", "status": group.status}

@router.post("/groups/{id}/invite-dealers")
async def invite_dealers_to_group(
    id: str,
    payload: InviteDealersRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    group_res = await db.execute(
        select(BuyingGroup)
        .options(
            selectinload(BuyingGroup.variant)
            .selectinload(VehicleVariant.model)
            .selectinload(VehicleModel.brand)
        )
        .where(BuyingGroup.id == id)
    )
    group = group_res.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Buying group not found")

    invited_count = 0
    for dealer_id in payload.dealer_ids:
        # Check dealer exists and is verified
        d_res = await db.execute(select(Dealer).where(Dealer.id == dealer_id))
        dealer = d_res.scalar_one_or_none()
        if not dealer or dealer.verification_status != "VERIFIED":
            continue

        # Check existing invitation
        inv_check = await db.execute(
            select(DealerGroupInvitation).where(
                DealerGroupInvitation.group_id == group.id,
                DealerGroupInvitation.dealer_id == dealer.id
            )
        )
        if not inv_check.scalar_one_or_none():
            inv = DealerGroupInvitation(
                group_id=group.id,
                dealer_id=dealer.id,
                status="INVITED"
            )
            db.add(inv)
            invited_count += 1

            # Dispatch notification
            await NotificationService.notify(
                db=db,
                user_id=dealer.user_id,
                title="Bidding Invitation Received!",
                message=f"You are invited to quote for {group.variant.model.brand.name} {group.variant.model.name} ({group.current_members_count} buyers pooled in group {group.group_code}).",
                event_type="DEALER_INVITATION",
                link_url="/dealer/invitations"
            )

    await db.commit()
    return {"message": f"Successfully invited {invited_count} verified dealerships to group {group.group_code}"}

# QUOTATION MODERATION
@router.get("/quotations", response_model=List[QuotationResponse])
async def list_admin_quotations(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Quotation)
        .options(
            selectinload(Quotation.dealer).selectinload(Dealer.city),
            selectinload(Quotation.revisions)
        )
        .order_by(Quotation.created_at.desc())
    )
    if status:
        query = query.where(Quotation.status == status)

    res = await db.execute(query)
    quotes = res.scalars().all()

    return [
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
            dealer_city=q.dealer.city.name,
            revisions_count=len(q.revisions) + 1
        )
        for q in quotes
    ]

@router.put("/quotations/{id}/approve")
async def approve_quotation(
    id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Quotation)
        .options(
            selectinload(Quotation.dealer),
            selectinload(Quotation.group).selectinload(BuyingGroup.members)
        )
        .where(Quotation.id == id)
    )
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")

    quote.status = "APPROVED"
    quote.admin_review_notes = notes or "Verified by platform administrator."
    quote.updated_at = datetime.now(timezone.utc)

    # If group is BIDDING_OPEN, change group to OFFERS_AVAILABLE or keep BIDDING_OPEN with offers available
    if quote.group.status in ["BIDDING_OPEN", "READY_FOR_BIDDING"]:
        quote.group.status = "OFFERS_AVAILABLE"

    # Notify dealer
    await NotificationService.notify(
        db=db,
        user_id=quote.dealer.user_id,
        title="Quotation Approved!",
        message=f"Your quotation of ₹{quote.final_on_road_price:,.2f} for group {quote.group.group_code} has been approved and is now live to buyers.",
        event_type="QUOTATION_APPROVED"
    )

    # Notify all active cohort members
    for member in quote.group.members:
        if member.status == "ACTIVE":
            await NotificationService.notify(
                db=db,
                user_id=member.user_id,
                title="New Competitive Offer Received!",
                message=f"A verified quotation of ₹{quote.final_on_road_price:,.2f} from {quote.dealer.dealership_name} is now available for your group {quote.group.group_code}.",
                event_type="NEW_OFFER",
                link_url=f"/groups/{quote.group.id}"
            )

    await db.commit()
    return {"message": "Quotation approved and published to buyers"}

@router.put("/quotations/{id}/reject")
async def reject_quotation(
    id: str,
    notes: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Quotation)
        .options(selectinload(Quotation.dealer), selectinload(Quotation.group))
        .where(Quotation.id == id)
    )
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")

    quote.status = "REJECTED"
    quote.admin_review_notes = notes
    quote.updated_at = datetime.now(timezone.utc)

    # Notify dealer
    await NotificationService.notify(
        db=db,
        user_id=quote.dealer.user_id,
        title="Quotation Action Required",
        message=f"Your quotation for group {quote.group.group_code} was rejected with feedback: {notes}. Please revise and resubmit.",
        event_type="QUOTATION_REJECTED"
    )

    await db.commit()
    return {"message": "Quotation rejected with feedback"}

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100))
    return res.scalars().all()

