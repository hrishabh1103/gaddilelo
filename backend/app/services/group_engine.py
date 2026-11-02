import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException, status
from backend.app.models.models import BuyingGroup, GroupMember, User, VehicleVariant, City

class GroupEngine:
    """
    Core Group Buying Engine enforcing business rules, state machine transitions,
    and member cohort integrity.
    """

    VALID_TRANSITIONS = {
        "DRAFT": ["OPEN", "CANCELLED"],
        "OPEN": ["QUALIFYING", "CANCELLED"],
        "QUALIFYING": ["READY_FOR_BIDDING", "OPEN", "CANCELLED"],
        "READY_FOR_BIDDING": ["BIDDING_OPEN", "CANCELLED"],
        "BIDDING_OPEN": ["OFFERS_AVAILABLE", "CANCELLED"],
        "OFFERS_AVAILABLE": ["COMPLETED", "CANCELLED"],
        "COMPLETED": [],
        "CANCELLED": []
    }

    @staticmethod
    def generate_group_code(variant_name: str, city_name: str) -> str:
        # e.g. GL-IND-NEXON-A7B2
        clean_city = "".join(filter(str.isalnum, city_name))[:3].upper()
        clean_variant = "".join(filter(str.isalnum, variant_name))[:5].upper()
        random_suffix = uuid.uuid4().hex[:4].upper()
        return f"GL-{clean_city}-{clean_variant}-{random_suffix}"

    @classmethod
    async def create_group(
        cls,
        db: AsyncSession,
        creator_user_id: str,
        variant_id: str,
        city_id: str,
        target_members: int,
        timeline: str,
        notes: str = None
    ) -> BuyingGroup:
        # Validate variant exists
        variant_res = await db.execute(select(VehicleVariant).where(VehicleVariant.id == variant_id))
        variant = variant_res.scalar_one_or_none()
        if not variant:
            raise HTTPException(status_code=404, detail="Vehicle variant not found")

        # Validate city exists
        city_res = await db.execute(select(City).where(City.id == city_id))
        city = city_res.scalar_one_or_none()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")

        group_code = cls.generate_group_code(variant.name, city.name)

        new_group = BuyingGroup(
            group_code=group_code,
            vehicle_variant_id=variant_id,
            city_id=city_id,
            created_by_user_id=creator_user_id,
            status="OPEN",
            target_members=target_members,
            current_members_count=1,
            target_purchase_timeline=timeline,
            additional_notes=notes
        )
        db.add(new_group)
        await db.flush()

        # Add creator as initial member
        initial_member = GroupMember(
            group_id=new_group.id,
            user_id=creator_user_id,
            status="ACTIVE",
            buyer_notes="Group Founder"
        )
        db.add(initial_member)
        await db.commit()
        await db.refresh(new_group)
        return new_group

    @classmethod
    async def join_group(cls, db: AsyncSession, group_id: str, user_id: str, notes: str = None) -> BuyingGroup:
        # Check group status
        res = await db.execute(select(BuyingGroup).where(BuyingGroup.id == group_id))
        group = res.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Buying group not found")

        if group.status not in ["OPEN", "QUALIFYING"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot join group in '{group.status}' status. Joining is only permitted when OPEN or QUALIFYING."
            )

        # Check existing membership (Duplicate prevention)
        existing_res = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            )
        )
        existing = existing_res.scalar_one_or_none()
        if existing:
            if existing.status == "ACTIVE":
                raise HTTPException(status_code=400, detail="You are already an active member of this buying group")
            else:
                # Reactivate withdrawn member
                existing.status = "ACTIVE"
                existing.buyer_notes = notes
                group.current_members_count += 1
        else:
            new_member = GroupMember(
                group_id=group_id,
                user_id=user_id,
                status="ACTIVE",
                buyer_notes=notes
            )
            db.add(new_member)
            group.current_members_count += 1

        # Check if target milestone reached -> advance to QUALIFYING
        if group.current_members_count >= group.target_members and group.status == "OPEN":
            group.status = "QUALIFYING"

        group.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(group)
        return group

    @classmethod
    async def leave_group(cls, db: AsyncSession, group_id: str, user_id: str) -> BuyingGroup:
        res = await db.execute(select(BuyingGroup).where(BuyingGroup.id == group_id))
        group = res.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Buying group not found")

        # Business rule: Buyers can leave a group before bidding begins
        if group.status in ["BIDDING_OPEN", "OFFERS_AVAILABLE", "COMPLETED"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot leave group once bidding has commenced or offers are published."
            )

        member_res = await db.execute(
            select(GroupMember).where(
                and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id, GroupMember.status == "ACTIVE")
            )
        )
        member = member_res.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=400, detail="You are not an active member of this group")

        member.status = "WITHDRAWN"
        group.current_members_count = max(0, group.current_members_count - 1)
        
        # If was QUALIFYING and dropped below target, return to OPEN
        if group.status == "QUALIFYING" and group.current_members_count < group.target_members:
            group.status = "OPEN"

        group.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(group)
        return group

    @classmethod
    async def update_status(cls, db: AsyncSession, group_id: str, new_status: str, bidding_end_time = None) -> BuyingGroup:
        res = await db.execute(select(BuyingGroup).where(BuyingGroup.id == group_id))
        group = res.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Buying group not found")

        allowed = cls.VALID_TRANSITIONS.get(group.status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Illegal transition from '{group.status}' to '{new_status}'. Allowed: {allowed}"
            )

        group.status = new_status
        if new_status == "BIDDING_OPEN":
            group.bidding_start_time = datetime.now(timezone.utc)
            if bidding_end_time:
                group.bidding_end_time = bidding_end_time

        group.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(group)
        return group
