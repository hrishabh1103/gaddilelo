from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timezone
from decimal import Decimal

from backend.app.core.database import get_db
from backend.app.models.models import (
    Dealer, DealerGroupInvitation, Quotation, QuotationRevision,
    QuotationLineItem, BuyerLead, BuyingGroup, VehicleVariant, VehicleModel,
    VehicleBrand, City, User
)
from backend.app.schemas.schemas import (
    DealerDashboardStats, QuotationCreate, QuotationResponse,
    BuyerLeadResponse, BuyerLeadStatusUpdate
)
from backend.app.services.pricing_engine import PricingEngine
from backend.app.services.notification_service import NotificationService
from backend.app.api.deps import require_dealer

router = APIRouter(prefix="/dealers", tags=["Dealer Portal"])

@router.get("/dashboard", response_model=DealerDashboardStats)
async def get_dealer_dashboard(
    current_user: User = Depends(require_dealer),
    db: AsyncSession = Depends(get_db)
):
    dealer = current_user.dealer
    if not dealer:
        raise HTTPException(status_code=400, detail="Dealer profile not linked to user")

    # 1. Invitations count
    inv_cnt = await db.execute(
        select(func.count(DealerGroupInvitation.id)).where(DealerGroupInvitation.dealer_id == dealer.id)
    )
    invitations = inv_cnt.scalar() or 0

    # 2. Active bidding opportunities (group status = BIDDING_OPEN and invited)
    active_bids_cnt = await db.execute(
        select(func.count(DealerGroupInvitation.id))
        .join(BuyingGroup, DealerGroupInvitation.group_id == BuyingGroup.id)
        .where(
            DealerGroupInvitation.dealer_id == dealer.id,
            BuyingGroup.status == "BIDDING_OPEN"
        )
    )
    active_bidding = active_bids_cnt.scalar() or 0

    # 3. Quotations submitted
    quotes_cnt = await db.execute(
        select(func.count(Quotation.id)).where(Quotation.dealer_id == dealer.id)
    )
    quotes = quotes_cnt.scalar() or 0

    # 4. Leads / customer enquiries
    leads_cnt = await db.execute(
        select(func.count(BuyerLead.id)).where(BuyerLead.dealer_id == dealer.id)
    )
    leads = leads_cnt.scalar() or 0

    # 5. Conversions
    conv_cnt = await db.execute(
        select(func.count(BuyerLead.id)).where(
            BuyerLead.dealer_id == dealer.id,
            BuyerLead.status == "PURCHASE_COMPLETED"
        )
    )
    conversions = conv_cnt.scalar() or 0

    return DealerDashboardStats(
        invitations_count=invitations,
        active_bidding_count=active_bidding,
        quotations_submitted_count=quotes,
        leads_count=leads,
        conversions_count=conversions
    )

@router.get("/invitations")
async def list_invitations(
    current_user: User = Depends(require_dealer),
    db: AsyncSession = Depends(get_db)
):
    dealer = current_user.dealer
    if not dealer:
        raise HTTPException(status_code=400, detail="Dealer profile not found")

    res = await db.execute(
        select(DealerGroupInvitation)
        .options(
            selectinload(DealerGroupInvitation.group)
            .selectinload(BuyingGroup.city),
            selectinload(DealerGroupInvitation.group)
            .selectinload(BuyingGroup.variant)
            .selectinload(VehicleVariant.model)
            .selectinload(VehicleModel.brand),
            selectinload(DealerGroupInvitation.group)
            .selectinload(BuyingGroup.quotations)
        )
        .where(DealerGroupInvitation.dealer_id == dealer.id)
        .order_by(DealerGroupInvitation.invited_at.desc())
    )
    invitations = res.scalars().all()

    output = []
    for inv in invitations:
        g = inv.group
        # check if this dealer already submitted a quote
        my_quote = next((q for q in g.quotations if q.dealer_id == dealer.id), None)

        output.append({
            "invitation_id": inv.id,
            "status": inv.status,
            "invited_at": inv.invited_at,
            "group_id": g.id,
            "group_code": g.group_code,
            "group_status": g.status,
            "city_name": g.city.name,
            "current_members": g.current_members_count,
            "target_members": g.target_members,
            "target_purchase_timeline": g.target_purchase_timeline,
            "bidding_end_time": g.bidding_end_time,
            "vehicle": {
                "name": f"{g.variant.model.brand.name} {g.variant.model.name}",
                "variant": g.variant.name,
                "image_url": g.variant.model.image_url,
                "fuel_type": g.variant.fuel_type,
                "transmission": g.variant.transmission,
                "reference_ex_showroom": float(g.variant.reference_ex_showroom)
            },
            "has_submitted_quote": my_quote is not None,
            "submitted_quote_id": my_quote.id if my_quote else None,
            "submitted_quote_price": float(my_quote.final_on_road_price) if my_quote else None,
            "submitted_quote_status": my_quote.status if my_quote else None
        })

    return output

@router.post("/quotations", response_model=QuotationResponse)
async def submit_quotation(
    payload: QuotationCreate,
    current_user: User = Depends(require_dealer),
    db: AsyncSession = Depends(get_db)
):
    dealer = current_user.dealer
    if not dealer:
        raise HTTPException(status_code=400, detail="Dealer profile not found")

    if dealer.verification_status != "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dealership verification is pending or rejected. Only verified dealers can submit quotations."
        )

    # Check invitation
    inv_res = await db.execute(
        select(DealerGroupInvitation).where(
            DealerGroupInvitation.group_id == payload.group_id,
            DealerGroupInvitation.dealer_id == dealer.id
        )
    )
    invitation = inv_res.scalar_one_or_none()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dealership has not been invited to this buying group"
        )

    # Check group status and bidding timeline
    group_res = await db.execute(select(BuyingGroup).where(BuyingGroup.id == payload.group_id))
    group = group_res.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Buying group not found")

    if group.status != "BIDDING_OPEN":
        raise HTTPException(
            status_code=400,
            detail=f"Bidding is not open for this group (Current status: {group.status})"
        )

    if group.bidding_end_time and datetime.now(timezone.utc) > group.bidding_end_time.replace(tzinfo=timezone.utc if group.bidding_end_time.tzinfo is None else None):
        raise HTTPException(status_code=400, detail="Bidding period for this group has expired")

    # Validate arithmetic with vehicle-agnostic PricingEngine
    is_valid, calculated_price, err = PricingEngine.validate_quotation_math(
        base=payload.base_ex_showroom,
        rto=payload.rto_road_tax,
        insurance=payload.insurance_amount,
        tcs=payload.tcs_amount,
        acc=payload.accessories_amount,
        logistics=payload.logistics_handling,
        other=payload.other_statutory_charges,
        mfg_disc=payload.mfg_discount,
        dealer_disc=payload.dealer_discount,
        exchange=payload.exchange_bonus,
        corp_disc=payload.corporate_discount,
        submitted_final_price=(
            (payload.base_ex_showroom + payload.rto_road_tax + payload.insurance_amount + payload.tcs_amount +
             payload.accessories_amount + payload.logistics_handling + payload.other_statutory_charges)
            - (payload.mfg_discount + payload.dealer_discount + payload.exchange_bonus + payload.corporate_discount)
        )
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail=err)

    # Check if existing quotation
    existing_quote = await db.execute(
        select(Quotation).where(
            Quotation.group_id == payload.group_id,
            Quotation.dealer_id == dealer.id
        )
    )
    quote = existing_quote.scalar_one_or_none()

    if quote:
        raise HTTPException(
            status_code=400,
            detail="A quotation has already been submitted for this group. Please use the revision endpoint to update it."
        )

    # Create new quotation
    new_quote = Quotation(
        group_id=payload.group_id,
        dealer_id=dealer.id,
        revision_number=1,
        status="SUBMITTED", # Admin reviews and approves before publishing to buyers
        base_ex_showroom=payload.base_ex_showroom,
        rto_road_tax=payload.rto_road_tax,
        insurance_amount=payload.insurance_amount,
        tcs_amount=payload.tcs_amount,
        mfg_discount=payload.mfg_discount,
        dealer_discount=payload.dealer_discount,
        exchange_bonus=payload.exchange_bonus,
        corporate_discount=payload.corporate_discount,
        accessories_amount=payload.accessories_amount,
        logistics_handling=payload.logistics_handling,
        other_statutory_charges=payload.other_statutory_charges,
        final_on_road_price=calculated_price,
        delivery_timeline_days=payload.delivery_timeline_days,
        offer_valid_until=payload.offer_valid_until,
        remarks=payload.remarks
    )
    db.add(new_quote)
    await db.flush()

    # Save line items
    if payload.line_items:
        for item in payload.line_items:
            li = QuotationLineItem(
                quotation_id=new_quote.id,
                item_name=item.item_name,
                item_type=item.item_type,
                amount=item.amount
            )
            db.add(li)

    # Update invitation status
    invitation.status = "SUBMITTED"
    await db.commit()
    await db.refresh(new_quote)

    # Notify dealer
    await NotificationService.notify(
        db=db,
        user_id=current_user.id,
        title="Quotation Submitted",
        message=f"Your quotation for {group.group_code} at ₹{calculated_price:,.2f} is under review.",
        event_type="QUOTATION_SUBMITTED"
    )

    return QuotationResponse(
        id=new_quote.id,
        group_id=new_quote.group_id,
        dealer_id=new_quote.dealer_id,
        revision_number=new_quote.revision_number,
        status=new_quote.status,
        base_ex_showroom=new_quote.base_ex_showroom,
        rto_road_tax=new_quote.rto_road_tax,
        insurance_amount=new_quote.insurance_amount,
        tcs_amount=new_quote.tcs_amount,
        mfg_discount=new_quote.mfg_discount,
        dealer_discount=new_quote.dealer_discount,
        exchange_bonus=new_quote.exchange_bonus,
        corporate_discount=new_quote.corporate_discount,
        accessories_amount=new_quote.accessories_amount,
        logistics_handling=new_quote.logistics_handling,
        other_statutory_charges=new_quote.other_statutory_charges,
        final_on_road_price=new_quote.final_on_road_price,
        delivery_timeline_days=new_quote.delivery_timeline_days,
        offer_valid_until=new_quote.offer_valid_until,
        remarks=new_quote.remarks,
        created_at=new_quote.created_at,
        updated_at=new_quote.updated_at,
        dealership_name=dealer.dealership_name
    )

@router.put("/quotations/{id}", response_model=QuotationResponse)
async def revise_quotation(
    id: str,
    payload: QuotationCreate,
    current_user: User = Depends(require_dealer),
    db: AsyncSession = Depends(get_db)
):
    dealer = current_user.dealer
    if not dealer:
        raise HTTPException(status_code=400, detail="Dealer profile not found")

    res = await db.execute(
        select(Quotation)
        .options(selectinload(Quotation.group))
        .where(Quotation.id == id, Quotation.dealer_id == dealer.id)
    )
    quote = res.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")

    if quote.group.status != "BIDDING_OPEN":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot revise quotation. Group bidding is not open (status: {quote.group.status})"
        )

    # Validate arithmetic
    is_valid, calculated_price, err = PricingEngine.validate_quotation_math(
        base=payload.base_ex_showroom,
        rto=payload.rto_road_tax,
        insurance=payload.insurance_amount,
        tcs=payload.tcs_amount,
        acc=payload.accessories_amount,
        logistics=payload.logistics_handling,
        other=payload.other_statutory_charges,
        mfg_disc=payload.mfg_discount,
        dealer_disc=payload.dealer_discount,
        exchange=payload.exchange_bonus,
        corp_disc=payload.corporate_discount,
        submitted_final_price=(
            (payload.base_ex_showroom + payload.rto_road_tax + payload.insurance_amount + payload.tcs_amount +
             payload.accessories_amount + payload.logistics_handling + payload.other_statutory_charges)
            - (payload.mfg_discount + payload.dealer_discount + payload.exchange_bonus + payload.corporate_discount)
        )
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=err)

    # Archive previous revision snapshot
    snapshot = {
        "revision_number": quote.revision_number,
        "base_ex_showroom": float(quote.base_ex_showroom),
        "rto_road_tax": float(quote.rto_road_tax),
        "insurance_amount": float(quote.insurance_amount),
        "final_on_road_price": float(quote.final_on_road_price),
        "discounts": float(quote.mfg_discount + quote.dealer_discount + quote.exchange_bonus + quote.corporate_discount),
        "delivery_timeline_days": quote.delivery_timeline_days,
        "remarks": quote.remarks,
        "status": quote.status
    }

    revision_log = QuotationRevision(
        quotation_id=quote.id,
        revision_number=quote.revision_number,
        snapshot=snapshot,
        revised_by_user_id=current_user.id
    )
    db.add(revision_log)

    # Update quotation
    quote.revision_number += 1
    quote.status = "SUBMITTED" # requires re-approval
    quote.base_ex_showroom = payload.base_ex_showroom
    quote.rto_road_tax = payload.rto_road_tax
    quote.insurance_amount = payload.insurance_amount
    quote.tcs_amount = payload.tcs_amount
    quote.mfg_discount = payload.mfg_discount
    quote.dealer_discount = payload.dealer_discount
    quote.exchange_bonus = payload.exchange_bonus
    quote.corporate_discount = payload.corporate_discount
    quote.accessories_amount = payload.accessories_amount
    quote.logistics_handling = payload.logistics_handling
    quote.other_statutory_charges = payload.other_statutory_charges
    quote.final_on_road_price = calculated_price
    quote.delivery_timeline_days = payload.delivery_timeline_days
    quote.offer_valid_until = payload.offer_valid_until
    quote.remarks = payload.remarks
    quote.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(quote)

    return QuotationResponse(
        id=quote.id,
        group_id=quote.group_id,
        dealer_id=quote.dealer_id,
        revision_number=quote.revision_number,
        status=quote.status,
        base_ex_showroom=quote.base_ex_showroom,
        rto_road_tax=quote.rto_road_tax,
        insurance_amount=quote.insurance_amount,
        tcs_amount=quote.tcs_amount,
        mfg_discount=quote.mfg_discount,
        dealer_discount=quote.dealer_discount,
        exchange_bonus=quote.exchange_bonus,
        corporate_discount=quote.corporate_discount,
        accessories_amount=quote.accessories_amount,
        logistics_handling=quote.logistics_handling,
        other_statutory_charges=quote.other_statutory_charges,
        final_on_road_price=quote.final_on_road_price,
        delivery_timeline_days=quote.delivery_timeline_days,
        offer_valid_until=quote.offer_valid_until,
        remarks=quote.remarks,
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        dealership_name=dealer.dealership_name,
        revisions_count=quote.revision_number
    )

@router.get("/quotations", response_model=List[QuotationResponse])
async def list_dealer_quotations(
    current_user: User = Depends(require_dealer),
    db: AsyncSession = Depends(get_db)
):
    dealer = current_user.dealer
    if not dealer:
        raise HTTPException(status_code=400, detail="Dealer profile not found")

    res = await db.execute(
        select(Quotation)
        .options(selectinload(Quotation.revisions))
        .where(Quotation.dealer_id == dealer.id)
        .order_by(Quotation.updated_at.desc())
    )
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
            dealership_name=dealer.dealership_name,
            revisions_count=len(q.revisions) + 1
        )
        for q in quotes
    ]

@router.get("/leads", response_model=List[BuyerLeadResponse])
async def list_dealer_leads(
    current_user: User = Depends(require_dealer),
    db: AsyncSession = Depends(get_db)
):
    dealer = current_user.dealer
    if not dealer:
        raise HTTPException(status_code=400, detail="Dealer profile not found")

    res = await db.execute(
        select(BuyerLead)
        .options(
            selectinload(BuyerLead.buyer).selectinload(User.profile),
            selectinload(BuyerLead.group)
            .selectinload(BuyingGroup.variant)
            .selectinload(VehicleVariant.model)
            .selectinload(VehicleModel.brand),
            selectinload(BuyerLead.quotation)
        )
        .where(BuyerLead.dealer_id == dealer.id)
        .order_by(BuyerLead.created_at.desc())
    )
    leads = res.scalars().all()

    output = []
    for l in leads:
        output.append(
            BuyerLeadResponse(
                id=l.id,
                group_id=l.group_id,
                buyer_id=l.buyer_id,
                dealer_id=l.dealer_id,
                quotation_id=l.quotation_id,
                status=l.status,
                buyer_consent_given=l.buyer_consent_given,
                notes=l.notes,
                created_at=l.created_at,
                buyer_name=l.buyer.profile.full_name if l.buyer.profile else "Valued Buyer",
                buyer_phone=l.buyer.phone, # Only exposed with explicit buyer consent
                buyer_email=l.buyer.email,
                dealership_name=dealer.dealership_name,
                vehicle_name=f"{l.group.variant.model.brand.name} {l.group.variant.model.name} {l.group.variant.name}",
                quoted_price=l.quotation.final_on_road_price
            )
        )
    return output

@router.put("/leads/{id}/status")
async def update_lead_status(
    id: str,
    payload: BuyerLeadStatusUpdate,
    current_user: User = Depends(require_dealer),
    db: AsyncSession = Depends(get_db)
):
    dealer = current_user.dealer
    if not dealer:
        raise HTTPException(status_code=400, detail="Dealer profile not found")

    res = await db.execute(
        select(BuyerLead).where(BuyerLead.id == id, BuyerLead.dealer_id == dealer.id)
    )
    lead = res.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead enquiry not found")

    lead.status = payload.status
    if payload.notes:
        lead.notes = payload.notes
    lead.updated_at = datetime.now(timezone.utc)

    await db.commit()

    # Notify buyer about progress
    status_messages = {
        "CONTACTED": "Dealership has logged your callback enquiry and will reach out.",
        "TEST_DRIVE_SCHEDULED": "Dealership has scheduled your test drive appointment.",
        "BOOKING_IN_PROGRESS": "Dealership has initiated your vehicle booking process.",
        "PURCHASE_COMPLETED": "Congratulations! Your vehicle purchase has been recorded.",
        "LOST": "Your lead status was closed."
    }

    if payload.status in status_messages:
        await NotificationService.notify(
            db=db,
            user_id=lead.buyer_id,
            title="Dealership Enquiry Update",
            message=status_messages[payload.status],
            event_type="LEAD_UPDATED"
        )

    return {"message": "Lead status updated successfully", "new_status": lead.status}
