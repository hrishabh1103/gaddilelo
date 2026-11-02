from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.models import BuyerLead, Quotation, BuyingGroup, GroupMember, User, Dealer
from backend.app.schemas.schemas import BuyerLeadRequest, BuyerLeadResponse
from backend.app.services.notification_service import NotificationService
from backend.app.api.deps import require_buyer

router = APIRouter(prefix="/leads", tags=["Buyer Leads"])

@router.post("/request-callback", response_model=BuyerLeadResponse)
async def request_callback(
    payload: BuyerLeadRequest,
    current_user: User = Depends(require_buyer),
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify buyer is member of group
    member_res = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == payload.group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.status == "ACTIVE"
        )
    )
    if not member_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be an active member of this buying group to request a dealer callback"
        )

    # 2. Verify quotation exists and is approved
    quote_res = await db.execute(
        select(Quotation)
        .options(
            selectinload(Quotation.dealer),
            selectinload(Quotation.group)
        )
        .where(
            Quotation.id == payload.quotation_id,
            Quotation.group_id == payload.group_id,
            Quotation.status == "APPROVED"
        )
    )
    quote = quote_res.scalar_one_or_none()
    if not quote:
        raise HTTPException(
            status_code=404,
            detail="Quotation not found or not approved for this group"
        )

    # 3. Check for existing lead for this quotation and buyer
    existing_res = await db.execute(
        select(BuyerLead).where(
            BuyerLead.buyer_id == current_user.id,
            BuyerLead.quotation_id == payload.quotation_id
        )
    )
    existing_lead = existing_res.scalar_one_or_none()
    if existing_lead:
        return BuyerLeadResponse(
            id=existing_lead.id,
            group_id=existing_lead.group_id,
            buyer_id=existing_lead.buyer_id,
            dealer_id=existing_lead.dealer_id,
            quotation_id=existing_lead.quotation_id,
            status=existing_lead.status,
            buyer_consent_given=existing_lead.buyer_consent_given,
            notes=existing_lead.notes,
            created_at=existing_lead.created_at,
            dealership_name=quote.dealer.dealership_name
        )

    # 4. Create new lead with buyer consent
    new_lead = BuyerLead(
        group_id=payload.group_id,
        buyer_id=current_user.id,
        dealer_id=quote.dealer_id,
        quotation_id=payload.quotation_id,
        status="PENDING_CALLBACK",
        buyer_consent_given=True, # Consent requirement 13
        notes=payload.notes
    )
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)

    # 5. Notify dealership user
    dealer_user_id = quote.dealer.user_id
    buyer_name = current_user.profile.full_name if current_user.profile else "A Buyer"
    await NotificationService.notify(
        db=db,
        user_id=dealer_user_id,
        title="New Buyer Callback Request!",
        message=f"{buyer_name} has accepted your quotation for group {quote.group.group_code} and requested a callback.",
        event_type="NEW_LEAD",
        link_url="/dealer/leads"
    )

    # 6. Notify buyer confirmation
    await NotificationService.notify(
        db=db,
        user_id=current_user.id,
        title="Callback Requested",
        message=f"Your contact details have been securely shared with {quote.dealer.dealership_name}. An authorized representative will contact you shortly.",
        event_type="CALLBACK_CONFIRMED"
    )

    return BuyerLeadResponse(
        id=new_lead.id,
        group_id=new_lead.group_id,
        buyer_id=new_lead.buyer_id,
        dealer_id=new_lead.dealer_id,
        quotation_id=new_lead.quotation_id,
        status=new_lead.status,
        buyer_consent_given=new_lead.buyer_consent_given,
        notes=new_lead.notes,
        created_at=new_lead.created_at,
        dealership_name=quote.dealer.dealership_name
    )
