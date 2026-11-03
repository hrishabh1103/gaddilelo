import pytest
import pytest_asyncio
import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import (
    User, Dealer, City, VehicleModel, VehicleVariant, BuyingGroup, GroupMember,
    BuyerIntentConfirmation, DealerGroupInvitation, Quotation, AuthToken
)

@pytest.mark.asyncio
async def test_complete_12_step_production_flow():
    """
    Executes the complete 12-step buyer and dealer lifecycle end-to-end:
    1. Register a buyer.
    2. Verify the email.
    3. Log in.
    4. Create a vehicle group.
    5. Confirm buyer intent.
    6. Register a dealer.
    7. Verify the dealer through the admin flow.
    8. Submit an itemized dealer quotation.
    9. Revise the quotation.
    10. Log in as the buyer.
    11. Compare quotations.
    12. Verify that buyer and dealer private information is not exposed.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_id = uuid.uuid4().hex[:8]

        # ---------------------------------------------------------
        # Step 1: Register a Buyer
        # ---------------------------------------------------------
        buyer_email = f"buyer.prod.{unique_id}@example.com"
        buyer_password = "SecurePassword@2026"
        buyer_phone = f"9826{uuid.uuid4().hex[:6]}"
        buyer_name = f"Aarav Sharma {unique_id}"

        reg_res = await ac.post("/api/v1/auth/register", json={
            "email": buyer_email,
            "password": buyer_password,
            "phone": buyer_phone,
            "full_name": buyer_name,
            "role": "BUYER"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        buyer_auth_data = reg_res.json()
        buyer_user_id = buyer_auth_data["user"]["id"]
        buyer_token = buyer_auth_data["access_token"]
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

        # ---------------------------------------------------------
        # Step 2: Verify Buyer Email
        # ---------------------------------------------------------
        req_v = await ac.post("/api/v1/auth/request-verification-email", json={"email": buyer_email})
        assert req_v.status_code == 200
        v_token = req_v.json()["verification_token"]

        verify_res = await ac.post("/api/v1/auth/verify-email", json={"token": v_token})
        assert verify_res.status_code == 200
        assert verify_res.json()["status"] == "VERIFIED"

        # Replay attempt must fail (Single-use enforcement)
        replay_v = await ac.post("/api/v1/auth/verify-email", json={"token": v_token})
        assert replay_v.status_code == 400

        # ---------------------------------------------------------
        # Step 3: Log in as Buyer
        # ---------------------------------------------------------
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": buyer_email,
            "password": buyer_password
        })
        assert login_res.status_code == 200
        buyer_token = login_res.json()["access_token"]
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

        # ---------------------------------------------------------
        # Step 4 & 5: Create Vehicle Group with Buyer Intent Confirmation
        # ---------------------------------------------------------
        async with AsyncSessionLocal() as db:
            city = (await db.execute(select(City))).scalars().first()
            variant = (await db.execute(select(VehicleVariant))).scalars().first()
            assert city is not None, "Seed city required for test"
            assert variant is not None, "Seed variant required for test"
            test_city_id = city.id
            test_variant_id = variant.id

        group_payload = {
            "vehicle_variant_id": test_variant_id,
            "city_id": test_city_id,
            "target_members": 5,
            "target_purchase_timeline": "WITHIN_30_DAYS",
            "additional_notes": "Test cohort for production audit",
            "buyer_intent": {
                "purchase_timeline": "WITHIN_30_DAYS",
                "is_genuine_intent": True,
                "is_non_binding_acknowledged": True,
                "agreed_to_contact": True
            }
        }

        grp_res = await ac.post("/api/v1/groups", json=group_payload, headers=buyer_headers)
        assert grp_res.status_code == 200, f"Group creation failed: {grp_res.text}"
        group_data = grp_res.json()
        group_id = group_data["id"]

        # Verify Buyer Intent audit record is persisted in DB
        async with AsyncSessionLocal() as db:
            intent_res = await db.execute(
                select(BuyerIntentConfirmation).where(
                    BuyerIntentConfirmation.group_id == group_id,
                    BuyerIntentConfirmation.user_id == buyer_user_id
                )
            )
            intent_record = intent_res.scalar_one_or_none()
            assert intent_record is not None
            assert intent_record.is_genuine_intent is True
            assert intent_record.is_non_binding_acknowledged is True
            assert intent_record.purchase_timeline == "WITHIN_30_DAYS"

        # ---------------------------------------------------------
        # Step 6: Register Dealer (Starts as PENDING)
        # ---------------------------------------------------------
        dealer_email = f"dealer.prod.{unique_id}@example.com"
        dealer_password = "DealerPassword@2026"
        dealer_phone = f"9827{uuid.uuid4().hex[:6]}"
        dealer_gstin = f"23AABC{uuid.uuid4().hex[:5].upper()}1Z5"

        dealer_reg_res = await ac.post("/api/v1/auth/register", json={
            "email": dealer_email,
            "password": dealer_password,
            "phone": dealer_phone,
            "full_name": f"Sanghi Prime {unique_id}",
            "role": "DEALER",
            "dealership_name": f"Sanghi Prime Motors {unique_id}",
            "legal_entity_name": f"Sanghi Prime Pvt Ltd {unique_id}",
            "gstin": dealer_gstin,
            "city_id": test_city_id,
            "address": "Ring Road, Indore"
        })
        assert dealer_reg_res.status_code == 200
        dealer_auth = dealer_reg_res.json()
        dealer_token = dealer_auth["access_token"]
        dealer_headers = {"Authorization": f"Bearer {dealer_token}"}

        # Retrieve dealer ID
        async with AsyncSessionLocal() as db:
            d_res = await db.execute(select(Dealer).where(Dealer.gstin == dealer_gstin))
            dealer_obj = d_res.scalar_one()
            dealer_id = dealer_obj.id
            assert dealer_obj.verification_status == "PENDING"

        # Step 7a: Unverified dealer CANNOT bid
        # Set group status to BIDDING_OPEN and invite dealer
        async with AsyncSessionLocal() as db:
            grp_db = (await db.execute(select(BuyingGroup).where(BuyingGroup.id == group_id))).scalar_one()
            grp_db.status = "BIDDING_OPEN"
            db.add(DealerGroupInvitation(group_id=group_id, dealer_id=dealer_id, status="INVITED"))
            await db.commit()

        quote_payload = {
            "group_id": group_id,
            "base_ex_showroom": 1000000.0,
            "rto_road_tax": 80000.0,
            "insurance_amount": 35000.0,
            "tcs_amount": 10000.0,
            "mfg_discount": 20000.0,
            "dealer_discount": 40000.0,
            "exchange_bonus": 10000.0,
            "corporate_discount": 5000.0,
            "accessories_amount": 15000.0,
            "logistics_handling": 5000.0,
            "other_statutory_charges": 2000.0,
            "delivery_timeline_days": 15,
            "offer_valid_until": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        }

        # Unverified bid attempt must fail with 403
        unverified_bid_res = await ac.post("/api/v1/dealers/quotations", json=quote_payload, headers=dealer_headers)
        assert unverified_bid_res.status_code == 403

        # ---------------------------------------------------------
        # Step 7b: Admin Verifies Dealer
        # ---------------------------------------------------------
        admin_login = await ac.post("/api/v1/auth/login", json={
            "email": "admin@gaadilelo.com",
            "password": "Admin@123"
        })
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        verify_dealer_res = await ac.put(f"/api/v1/admin/dealers/{dealer_id}/verify", json={
            "verification_status": "VERIFIED",
            "verification_notes": "All dealership GST and OEM certificates verified."
        }, headers=admin_headers)
        assert verify_dealer_res.status_code == 200
        assert "VERIFIED" in verify_dealer_res.json()["message"]

        # ---------------------------------------------------------
        # Step 8: Verified Dealer Submits Itemized Quotation
        # ---------------------------------------------------------
        bid_res = await ac.post("/api/v1/dealers/quotations", json=quote_payload, headers=dealer_headers)
        assert bid_res.status_code == 200, f"Bid failed: {bid_res.text}"
        quote_data = bid_res.json()
        quote_id = quote_data["id"]

        # Expected On-Road Price:
        # 1,000,000 (Base) + 80,000 (RTO) + 35,000 (Ins) + 10,000 (TCS) + 15,000 (Acc) + 5,000 (Logistics) + 2,000 (Other)
        # = 1,147,000
        # Discounts: 20,000 (Mfg) + 40,000 (Dealer) + 10,000 (Exchange) + 5,000 (Corp) = 75,000
        # Final on road: 1,147,000 - 75,000 = 1,072,000
        assert Decimal(str(quote_data["final_on_road_price"])) == Decimal("1072000.00")

        # ---------------------------------------------------------
        # Step 9: Dealer Revises Quotation
        # ---------------------------------------------------------
        revised_payload = dict(quote_payload)
        revised_payload["dealer_discount"] = 50000.0 # Increase discount by 10,000

        revise_res = await ac.put(f"/api/v1/dealers/quotations/{quote_id}", json=revised_payload, headers=dealer_headers)
        assert revise_res.status_code == 200
        revised_data = revise_res.json()
        assert Decimal(str(revised_data["final_on_road_price"])) == Decimal("1062000.00")
        assert revised_data["revision_number"] == 2

        # ---------------------------------------------------------
        # Step 10 & 11: Admin Approves Quotation & Buyer Compares Offers
        # ---------------------------------------------------------
        appr_res = await ac.put(f"/api/v1/admin/quotations/{quote_id}/approve", headers=admin_headers)
        assert appr_res.status_code == 200

        # Buyer compares offers
        offers_res = await ac.get(f"/api/v1/groups/{group_id}/offers", headers=buyer_headers)
        assert offers_res.status_code == 200
        offers_list = offers_res.json()
        assert len(offers_list) >= 1
        top_offer = offers_list[0]
        assert top_offer["id"] == quote_id
        assert Decimal(str(top_offer["final_on_road_price"])) == Decimal("1062000.00")
        assert top_offer["dealership_name"] == f"Sanghi Prime Motors {unique_id}"

        # ---------------------------------------------------------
        # Step 12: Verify Privacy & Data Isolation
        # ---------------------------------------------------------
        group_public_res = await ac.get(f"/api/v1/groups/{group_id}")
        assert group_public_res.status_code == 200
        group_public_data = group_public_res.json()

        # Public details MUST NOT expose buyer phone or email
        assert "email" not in group_public_data
        assert "phone" not in group_public_data
        assert "members" not in group_public_data # Individual member list hidden

        # Competitor dealer cannot revise this quote
        other_dealer_res = await ac.post("/api/v1/auth/register", json={
            "email": f"other.dealer.{unique_id}@test.com",
            "password": "Password123!",
            "phone": f"9777{uuid.uuid4().hex[:6]}",
            "full_name": f"Other Dealer {unique_id}",
            "role": "DEALER",
            "dealership_name": "Competitor Dealer",
            "gstin": f"23AXYZ{uuid.uuid4().hex[:5].upper()}1Z8",
            "city_id": test_city_id
        })
        other_token = other_dealer_res.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Attempt to tamper with first dealer's quote must fail
        tamper_res = await ac.put(f"/api/v1/dealers/quotations/{quote_id}", json=quote_payload, headers=other_headers)
        assert tamper_res.status_code in [403, 404]

        # Cleanup test group to maintain seed fixture isolation
        async with AsyncSessionLocal() as db:
            grp_db = (await db.execute(select(BuyingGroup).where(BuyingGroup.id == group_id))).scalar_one_or_none()
            if grp_db:
                await db.delete(grp_db)
                await db.commit()
