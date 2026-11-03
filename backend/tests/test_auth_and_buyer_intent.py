import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import select

from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import (
    User, UserProfile, Dealer, City, VehicleCategory, VehicleBrand,
    VehicleModel, VehicleVariant, BuyingGroup, GroupMember,
    BuyerIntentConfirmation, DealerGroupInvitation
)
from backend.app.core.security import (
    get_password_hash, create_access_token,
    create_password_reset_token, create_email_verification_token
)

@pytest.mark.asyncio
async def test_auth_full_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_suffix = uuid.uuid4().hex[:6]
        email = f"buyer.{unique_suffix}@testmail.com"
        password = "SecurePassword123!"

        # 1. Register buyer
        reg_payload = {
            "email": email,
            "password": password,
            "phone": f"9826{uuid.uuid4().hex[:6]}",
            "full_name": f"Test Buyer {unique_suffix}",
            "role": "BUYER"
        }
        reg_res = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 200, f"Register failed: {reg_res.text}"
        reg_data = reg_res.json()
        assert "access_token" in reg_data
        assert reg_data["user"]["email"] == email
        assert reg_data["user"]["role"] == "BUYER"

        token = reg_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 2. Get profile /auth/me
        me_res = await ac.get("/api/v1/auth/me", headers=auth_headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == email

        # 3. Login with wrong password
        bad_login = await ac.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword"})
        assert bad_login.status_code == 401

        # 4. Login with correct password
        good_login = await ac.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert good_login.status_code == 200
        assert "access_token" in good_login.json()

        # 5. Forgot password
        forgot_res = await ac.post("/api/v1/auth/forgot-password", json={"email": email})
        assert forgot_res.status_code == 200
        forgot_data = forgot_res.json()
        assert forgot_data["status"] == "SENT"
        reset_token = forgot_data.get("reset_token")
        assert reset_token is not None

        # 6. Reset password with valid token
        new_password = "NewSuperPassword456!"
        reset_res = await ac.post("/api/v1/auth/reset-password", json={
            "token": reset_token,
            "new_password": new_password
        })
        assert reset_res.status_code == 200
        assert reset_res.json()["status"] == "SUCCESS"

        # 6b. Verify reset token CANNOT BE REUSED
        reuse_res = await ac.post("/api/v1/auth/reset-password", json={
            "token": reset_token,
            "new_password": "YetAnotherPassword789!"
        })
        assert reuse_res.status_code == 400
        assert "already been used" in reuse_res.json()["detail"].lower()

        # 7. Old password no longer works
        old_login = await ac.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert old_login.status_code == 401

        # 8. New password logs in successfully
        new_login = await ac.post("/api/v1/auth/login", json={"email": email, "password": new_password})
        assert new_login.status_code == 200

        # 9. Request email verification token
        v_req_res = await ac.post("/api/v1/auth/request-verification-email", json={"email": email})
        assert v_req_res.status_code == 200
        v_token = v_req_res.json()["verification_token"]

        # 10. Verify email with valid token
        verify_res = await ac.post("/api/v1/auth/verify-email", json={"token": v_token})
        assert verify_res.status_code == 200
        assert verify_res.json()["status"] == "VERIFIED"

        # 10b. Verify verification token CANNOT BE REUSED
        reuse_v_res = await ac.post("/api/v1/auth/verify-email", json={"token": v_token})
        assert reuse_v_res.status_code == 400
        assert "already been used" in reuse_v_res.json()["detail"].lower()

        # 11. Expired token rejection
        import jwt
        from backend.app.core.config import settings
        expired_token = jwt.encode(
            {"sub": str(reg_data["user"]["id"]), "type": "password_reset", "exp": datetime.now(timezone.utc) - timedelta(hours=2)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        expired_res = await ac.post("/api/v1/auth/reset-password", json={
            "token": expired_token,
            "new_password": "SomePassword123"
        })
        assert expired_res.status_code == 400
        assert "invalid or has expired" in expired_res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_buyer_intent_confirmation_audit_trail():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_suffix = uuid.uuid4().hex[:6]
        buyer_email = f"intent.buyer.{unique_suffix}@testmail.com"
        password = "Password123!"

        # Create buyer
        reg_res = await ac.post("/api/v1/auth/register", json={
            "email": buyer_email,
            "password": password,
            "phone": f"9111{uuid.uuid4().hex[:6]}",
            "full_name": f"Intent Buyer {unique_suffix}",
            "role": "BUYER"
        })
        token = reg_res.json()["access_token"]
        buyer_id = reg_res.json()["user"]["id"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Find or create a city and variant
        async with AsyncSessionLocal() as db:
            city = (await db.execute(select(City))).scalars().first()
            variant = (await db.execute(select(VehicleVariant))).scalars().first()
            assert city is not None
            assert variant is not None
            city_id = city.id
            variant_id = variant.id

        # 1. Create group with explicit BuyerIntentConfirmation
        create_payload = {
            "vehicle_variant_id": variant_id,
            "city_id": city_id,
            "target_members": 5,
            "target_purchase_timeline": "WITHIN_30_DAYS",
            "additional_notes": "Immediate delivery preferred",
            "buyer_intent": {
                "purchase_timeline": "WITHIN_30_DAYS",
                "is_genuine_intent": True,
                "is_non_binding_acknowledged": True,
                "agreed_to_contact": True
            }
        }
        create_res = await ac.post("/api/v1/groups", json=create_payload, headers=auth_headers)
        assert create_res.status_code == 200, f"Group creation failed: {create_res.text}"
        group_id = create_res.json()["id"]

        # Verify BuyerIntentConfirmation record exists in DB
        async with AsyncSessionLocal() as db:
            intent_res = await db.execute(
                select(BuyerIntentConfirmation).where(
                    BuyerIntentConfirmation.group_id == group_id,
                    BuyerIntentConfirmation.user_id == buyer_id
                )
            )
            intent_record = intent_res.scalar_one_or_none()
            assert intent_record is not None, "BuyerIntentConfirmation was not recorded!"
            assert intent_record.is_genuine_intent is True
            assert intent_record.is_non_binding_acknowledged is True
            assert intent_record.agreed_to_contact is True
            assert intent_record.purchase_timeline == "WITHIN_30_DAYS"

        # 2. Test another buyer joining with intent affirmation
        buyer2_email = f"buyer2.{unique_suffix}@testmail.com"
        reg2 = await ac.post("/api/v1/auth/register", json={
            "email": buyer2_email,
            "password": password,
            "phone": f"9222{uuid.uuid4().hex[:6]}",
            "full_name": f"Joining Buyer {unique_suffix}",
            "role": "BUYER"
        })
        token2 = reg2.json()["access_token"]
        buyer2_id = reg2.json()["user"]["id"]
        auth2_headers = {"Authorization": f"Bearer {token2}"}

        join_payload = {
            "notes": "Joining group",
            "buyer_intent": {
                "purchase_timeline": "WITHIN_30_DAYS",
                "is_genuine_intent": True,
                "is_non_binding_acknowledged": True,
                "agreed_to_contact": True
            }
        }
        join_res = await ac.post(f"/api/v1/groups/{group_id}/join", json=join_payload, headers=auth2_headers)
        assert join_res.status_code == 200

        # Verify BuyerIntentConfirmation record for buyer2 exists in DB
        async with AsyncSessionLocal() as db:
            intent2_res = await db.execute(
                select(BuyerIntentConfirmation).where(
                    BuyerIntentConfirmation.group_id == group_id,
                    BuyerIntentConfirmation.user_id == buyer2_id
                )
            )
            intent2_record = intent2_res.scalar_one_or_none()
            assert intent2_record is not None, "BuyerIntentConfirmation for joining buyer was not recorded!"
            assert intent2_record.is_genuine_intent is True

@pytest.mark.asyncio
async def test_dealer_verification_guard():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_suffix = uuid.uuid4().hex[:6]
        dealer_email = f"dealer.{unique_suffix}@testdealership.com"
        password = "DealerPassword123!"

        async with AsyncSessionLocal() as db:
            city = (await db.execute(select(City))).scalars().first()
            assert city is not None
            city_id = city.id

        # 1. Register Dealer (Initial status: PENDING)
        reg_payload = {
            "email": dealer_email,
            "password": password,
            "phone": f"9333{uuid.uuid4().hex[:6]}",
            "full_name": f"Dealer Agent {unique_suffix}",
            "role": "DEALER",
            "dealership_name": f"Test Dealership {unique_suffix}",
            "gstin": f"23AAAAA{unique_suffix.upper()}1Z5",
            "city_id": city_id,
            "address": "Indore, MP"
        }
        reg_res = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert reg_res.status_code == 200
        token = reg_res.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 2. Check dealer status is PENDING
        me_res = await ac.get("/api/v1/auth/me", headers=auth_headers)
        assert me_res.status_code == 200
        dealer_info = me_res.json()["dealer"]
        assert dealer_info["verification_status"] == "PENDING"
        dealer_id = dealer_info["id"]

        # 3. Create a BIDDING_OPEN group and invite dealer
        async with AsyncSessionLocal() as db:
            variant = (await db.execute(select(VehicleVariant))).scalars().first()
            group = BuyingGroup(
                group_code=f"IND-TEST-{unique_suffix}",
                vehicle_variant_id=variant.id,
                city_id=city_id,
                created_by_user_id=me_res.json()["id"],
                status="BIDDING_OPEN",
                target_members=3,
                current_members_count=3,
                target_purchase_timeline="WITHIN_30_DAYS"
            )
            db.add(group)
            await db.flush()

            invitation = DealerGroupInvitation(
                group_id=group.id,
                dealer_id=dealer_id,
                status="INVITED"
            )
            db.add(invitation)
            await db.commit()
            test_group_id = group.id

        # 4. Attempt to submit quotation while PENDING -> MUST BE 403 FORBIDDEN
        quote_payload = {
            "group_id": test_group_id,
            "base_ex_showroom": 1200000,
            "rto_road_tax": 100000,
            "insurance_amount": 40000,
            "dealer_discount": 50000,
            "delivery_timeline_days": 14,
            "offer_valid_until": datetime.now(timezone.utc).isoformat()
        }
        blocked_res = await ac.post("/api/v1/dealers/quotations", json=quote_payload, headers=auth_headers)
        assert blocked_res.status_code == 403
        assert "verification is pending" in blocked_res.json()["detail"].lower()

        # 5. Admin verifies dealer
        async with AsyncSessionLocal() as db:
            d_res = await db.execute(select(Dealer).where(Dealer.id == dealer_id))
            d_obj = d_res.scalar_one()
            d_obj.verification_status = "VERIFIED"
            await db.commit()

        # 6. Verify dealer can now bid successfully
        allowed_res = await ac.post("/api/v1/dealers/quotations", json=quote_payload, headers=auth_headers)
        assert allowed_res.status_code == 200, f"Verified dealer bid failed: {allowed_res.text}"
        assert allowed_res.json()["status"] in ["PENDING_REVIEW", "SUBMITTED"]

@pytest.mark.asyncio
async def test_authorization_role_enforcement():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_suffix = uuid.uuid4().hex[:6]

        # 1. Register a buyer
        buyer_res = await ac.post("/api/v1/auth/register", json={
            "email": f"buyer.auth.{unique_suffix}@testmail.com",
            "password": "Password123!",
            "phone": f"9222{uuid.uuid4().hex[:6]}",
            "full_name": f"Auth Buyer {unique_suffix}",
            "role": "BUYER"
        })
        buyer_token = buyer_res.json()["access_token"]
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

        # 2. Register a dealer
        dealer_res = await ac.post("/api/v1/auth/register", json={
            "email": f"dealer.auth.{unique_suffix}@testmail.com",
            "password": "Password123!",
            "phone": f"9333{uuid.uuid4().hex[:6]}",
            "full_name": f"Auth Dealer {unique_suffix}",
            "role": "DEALER",
            "dealership_name": f"Dealer {unique_suffix}",
            "gstin": f"23AABC{uuid.uuid4().hex[:5].upper()}1Z5",
            "city_id": "test-city"
        })
        dealer_token = dealer_res.json()["access_token"]
        dealer_headers = {"Authorization": f"Bearer {dealer_token}"}

        # TEST A: Unauthenticated access to protected endpoints must fail with 401
        unauth_admin = await ac.get("/api/v1/admin/overview")
        assert unauth_admin.status_code == 401

        unauth_dealer = await ac.get("/api/v1/dealers/dashboard")
        assert unauth_dealer.status_code == 401

        # TEST B: Buyer attempting dealer-only endpoint must fail with 403
        buyer_on_dealer = await ac.get("/api/v1/dealers/dashboard", headers=buyer_headers)
        assert buyer_on_dealer.status_code == 403

        # TEST C: Buyer attempting admin-only endpoint must fail with 403
        buyer_on_admin = await ac.get("/api/v1/admin/overview", headers=buyer_headers)
        assert buyer_on_admin.status_code == 403

        # TEST D: Dealer attempting admin-only endpoint must fail with 403
        dealer_on_admin = await ac.get("/api/v1/admin/overview", headers=dealer_headers)
        assert dealer_on_admin.status_code == 403

        # TEST E: Non-member buyer attempting callback request fails with 403
        callback_res = await ac.post("/api/v1/leads/request-callback", json={
            "group_id": "fake-group-id",
            "quotation_id": "fake-quote-id"
        }, headers=buyer_headers)
        assert callback_res.status_code == 403

