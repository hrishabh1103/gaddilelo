import sys
from pathlib import Path

# Ensure project root and backend directory are in sys.path regardless of where script is invoked
_file_path = Path(__file__).resolve()
_project_root = _file_path.parents[3] # e.g. /Users/hrishabh/Car_Buy_Group
_backend_dir = _file_path.parents[2]  # e.g. /Users/hrishabh/Car_Buy_Group/backend

for _p in [str(_project_root), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models.models import (
    City, User, UserProfile, Dealer, DealerDocument,
    VehicleCategory, VehicleBrand, VehicleModel, VehicleVariant,
    BuyingGroup, GroupMember, DealerGroupInvitation, Quotation,
    QuotationLineItem, BuyerLead, Notification
)

async def seed_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        check = await db.execute(select(City))
        if check.scalars().first():
            print("[INFO] Database already contains seed data. Skipping duplicate seed.")
            return

        print("[SEED] Starting realistic Indore pilot seed data generation...")

        # 1. CITIES (Indore pilot + MP expansion hubs)
        indore = City(
            name="Indore",
            state="Madhya Pradesh",
            pincode_prefix="452",
            is_active=True
        )
        bhopal = City(
            name="Bhopal",
            state="Madhya Pradesh",
            pincode_prefix="462",
            is_active=True
        )
        db.add_all([indore, bhopal])
        await db.flush()

        # 2. VEHICLE CATEGORIES
        cat_cars = VehicleCategory(
            slug="car",
            name="Passenger Cars",
            description="Hatchbacks, Sedans, Compact & Mid-size SUVs, and MUVs",
            icon_name="Car",
            display_order=1
        )
        cat_ev = VehicleCategory(
            slug="electric-vehicle",
            name="Electric Vehicles",
            description="Electric Scooters, Electric Cars & Commercial EVs",
            icon_name="Zap",
            display_order=2
        )
        cat_2w = VehicleCategory(
            slug="two-wheeler",
            name="Two-Wheelers",
            description="Commuter & Premium Motorcycles and Scooters",
            icon_name="Bike",
            display_order=3
        )
        cat_cv = VehicleCategory(
            slug="commercial-vehicle",
            name="Commercial Vehicles",
            description="Pickups, Cargo 3-Wheelers, Small Commercial Vehicles & Trucks",
            icon_name="Truck",
            display_order=4
        )
        cat_3w = VehicleCategory(
            slug="three-wheeler",
            name="Three-Wheelers",
            description="Passenger & Cargo Auto-rickshaws",
            icon_name="Boxes",
            display_order=5
        )
        db.add_all([cat_cars, cat_ev, cat_2w, cat_cv, cat_3w])
        await db.flush()

        # 3. VEHICLE BRANDS (Indian OEMs)
        brand_tata = VehicleBrand(category_id=cat_cars.id, name="Tata Motors", slug="tata-motors", logo_url="https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=100")
        brand_maruti = VehicleBrand(category_id=cat_cars.id, name="Maruti Suzuki", slug="maruti-suzuki", logo_url="https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=100")
        brand_mahindra = VehicleBrand(category_id=cat_cars.id, name="Mahindra", slug="mahindra", logo_url="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=100")
        brand_hyundai = VehicleBrand(category_id=cat_cars.id, name="Hyundai", slug="hyundai", logo_url="https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=100")
        brand_ather = VehicleBrand(category_id=cat_ev.id, name="Ather Energy", slug="ather-energy", logo_url="https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=100")
        brand_ola = VehicleBrand(category_id=cat_ev.id, name="Ola Electric", slug="ola-electric", logo_url="https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=100")
        brand_tvs = VehicleBrand(category_id=cat_2w.id, name="TVS Motor", slug="tvs-motor", logo_url="https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=100")
        brand_leyland = VehicleBrand(category_id=cat_cv.id, name="Ashok Leyland", slug="ashok-leyland", logo_url="https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=100")

        db.add_all([brand_tata, brand_maruti, brand_mahindra, brand_hyundai, brand_ather, brand_ola, brand_tvs, brand_leyland])
        await db.flush()

        # 4. VEHICLE MODELS & VARIANTS
        # Tata Nexon
        model_nexon = VehicleModel(
            brand_id=brand_tata.id,
            name="Tata Nexon",
            slug="tata-nexon",
            body_type="Compact SUV",
            image_url="https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=600&auto=format&fit=crop&q=80",
            is_active=True
        )
        # Maruti Brezza
        model_brezza = VehicleModel(
            brand_id=brand_maruti.id,
            name="Maruti Suzuki Brezza",
            slug="maruti-brezza",
            body_type="Compact SUV",
            image_url="https://images.unsplash.com/photo-1590362891991-f776e747a588?w=600&auto=format&fit=crop&q=80",
            is_active=True
        )
        # Mahindra Scorpio-N
        model_scorpio = VehicleModel(
            brand_id=brand_mahindra.id,
            name="Mahindra Scorpio-N",
            slug="mahindra-scorpio-n",
            body_type="Mid-size SUV",
            image_url="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600&auto=format&fit=crop&q=80",
            is_active=True
        )
        # Ather 450X
        model_ather = VehicleModel(
            brand_id=brand_ather.id,
            name="Ather 450X Gen 3",
            slug="ather-450x",
            body_type="Electric Scooter",
            image_url="https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=600&auto=format&fit=crop&q=80",
            is_active=True
        )
        # Ashok Leyland Bada Dost
        model_leyland = VehicleModel(
            brand_id=brand_leyland.id,
            name="Ashok Leyland Bada Dost i4",
            slug="ashok-leyland-bada-dost",
            body_type="Small Commercial Vehicle",
            image_url="https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=600&auto=format&fit=crop&q=80",
            is_active=True
        )

        db.add_all([model_nexon, model_brezza, model_scorpio, model_ather, model_leyland])
        await db.flush()

        # VARIANTS
        var_nexon_cre_petrol = VehicleVariant(
            model_id=model_nexon.id,
            name="Creative Plus 1.2L Turbo Petrol",
            fuel_type="PETROL",
            transmission="MANUAL",
            seating_capacity=5,
            engine_cc_or_battery_kwh="1199 cc",
            reference_ex_showroom=Decimal("1169000.00"),
            specifications={"mileage": "17.4 kmpl", "power": "120 PS", "airbags": 6, "touchscreen": "10.25 inch"}
        )
        var_nexon_ev = VehicleVariant(
            model_id=model_nexon.id,
            name="Empowered Plus Long Range EV",
            fuel_type="ELECTRIC",
            transmission="SINGLE_SPEED_EV",
            seating_capacity=5,
            engine_cc_or_battery_kwh="40.5 kWh",
            reference_ex_showroom=Decimal("1719000.00"),
            specifications={"range": "465 km ARAI", "fast_charging": "56 mins (10-80%)", "v2v_charging": True}
        )
        var_brezza_vxi = VehicleVariant(
            model_id=model_brezza.id,
            name="VXi 1.5L Smart Hybrid",
            fuel_type="PETROL",
            transmission="MANUAL",
            seating_capacity=5,
            engine_cc_or_battery_kwh="1462 cc",
            reference_ex_showroom=Decimal("969000.00"),
            specifications={"mileage": "19.89 kmpl", "power": "103 PS", "esp": True, "hill_hold": True}
        )
        var_scorpio_z8 = VehicleVariant(
            model_id=model_scorpio.id,
            name="Z8L 2.2L mHawk Diesel 4x4",
            fuel_type="DIESEL",
            transmission="AUTOMATIC",
            seating_capacity=7,
            engine_cc_or_battery_kwh="2198 cc",
            reference_ex_showroom=Decimal("2454000.00"),
            specifications={"power": "175 PS", "torque": "400 Nm", "sony_audio": "12 speakers", "sunroof": True}
        )
        var_ather_37 = VehicleVariant(
            model_id=model_ather.id,
            name="450X 3.7 kWh Pro Pack",
            fuel_type="ELECTRIC",
            transmission="SINGLE_SPEED_EV",
            seating_capacity=2,
            engine_cc_or_battery_kwh="3.7 kWh",
            reference_ex_showroom=Decimal("154999.00"),
            specifications={"true_range": "110 km", "top_speed": "90 kmph", "warp_mode": "0-40 in 3.3s", "google_maps": True}
        )
        var_leyland_pickup = VehicleVariant(
            model_id=model_leyland.id,
            name="Bada Dost i4 High Deck 1.5L Diesel",
            fuel_type="DIESEL",
            transmission="MANUAL",
            seating_capacity=3,
            engine_cc_or_battery_kwh="1476 cc",
            reference_ex_showroom=Decimal("872000.00"),
            specifications={"payload": "1825 kg", "power": "80 HP", "deck_length": "9.8 ft"}
        )

        db.add_all([var_nexon_cre_petrol, var_nexon_ev, var_brezza_vxi, var_scorpio_z8, var_ather_37, var_leyland_pickup])
        await db.flush()

        # 5. SEED USERS & PROFILES
        # A. Admin
        u_admin = User(
            email="admin@gaadilelo.com",
            phone="9826011111",
            password_hash=get_password_hash("Admin@123"),
            role="ADMIN",
            is_active=True,
            is_verified=True
        )
        db.add(u_admin)
        await db.flush()
        p_admin = UserProfile(user_id=u_admin.id, full_name="Admin Ops Indore", city_id=indore.id)
        db.add(p_admin)

        # B. Buyers
        u_buyer1 = User(
            email="rahul.sharma@gmail.com",
            phone="9826022222",
            password_hash=get_password_hash("Buyer@123"),
            role="BUYER",
            is_active=True,
            is_verified=True
        )
        db.add(u_buyer1)
        await db.flush()
        p_buyer1 = UserProfile(user_id=u_buyer1.id, full_name="Rahul Sharma", city_id=indore.id)
        db.add(p_buyer1)

        u_buyer2 = User(
            email="priya.verma@gmail.com",
            phone="9826033333",
            password_hash=get_password_hash("Buyer@123"),
            role="BUYER",
            is_active=True,
            is_verified=True
        )
        db.add(u_buyer2)
        await db.flush()
        p_buyer2 = UserProfile(user_id=u_buyer2.id, full_name="Priya Verma", city_id=indore.id)
        db.add(p_buyer2)

        # C. Authorized Dealerships in Indore
        # Dealer 1: Sanghi Motors (Tata Motors Authorized, AB Road)
        u_dealer1 = User(
            email="sales@sanghimotors.com",
            phone="9826044444",
            password_hash=get_password_hash("Dealer@123"),
            role="DEALER",
            is_active=True,
            is_verified=True
        )
        db.add(u_dealer1)
        await db.flush()
        p_dealer1 = UserProfile(user_id=u_dealer1.id, full_name="Sanghi Sales Team", city_id=indore.id)
        db.add(p_dealer1)

        d_sanghi = Dealer(
            user_id=u_dealer1.id,
            dealership_name="Sanghi Brothers Tata Motors",
            legal_entity_name="Sanghi Brothers (Indore) Pvt Ltd",
            gstin="23AABCS1234F1Z1",
            city_id=indore.id,
            address="Plot 6, A.B. Road, Near Industry House, Indore, MP - 452001",
            authorized_brands=["Tata Motors"],
            verification_status="VERIFIED",
            verification_notes="Verified against MP Transport OEM Franchised dealer records.",
            verified_at=datetime.now(timezone.utc)
        )
        db.add(d_sanghi)

        # Dealer 2: Patel Motors (Maruti Suzuki Arena, Vijay Nagar)
        u_dealer2 = User(
            email="bids@patelmotors.com",
            phone="9826055555",
            password_hash=get_password_hash("Dealer@123"),
            role="DEALER",
            is_active=True,
            is_verified=True
        )
        db.add(u_dealer2)
        await db.flush()
        p_dealer2 = UserProfile(user_id=u_dealer2.id, full_name="Patel Motors Enterprise", city_id=indore.id)
        db.add(p_dealer2)

        d_patel = Dealer(
            user_id=u_dealer2.id,
            dealership_name="Patel Motors Maruti Suzuki Arena",
            legal_entity_name="Patel Automotive MP Private Limited",
            gstin="23AABCP5678G2Z2",
            city_id=indore.id,
            address="Scheme No. 54, Vijay Nagar, AB Road, Indore, MP - 452010",
            authorized_brands=["Maruti Suzuki"],
            verification_status="VERIFIED",
            verification_notes="Authorized Arena dealer certificate verified.",
            verified_at=datetime.now(timezone.utc)
        )
        db.add(d_patel)

        # Dealer 3: Shreeji Auto (Mahindra Authorized, Dewas Naka)
        u_dealer3 = User(
            email="corporate@shreejiauto.com",
            phone="9826066666",
            password_hash=get_password_hash("Dealer@123"),
            role="DEALER",
            is_active=True,
            is_verified=True
        )
        db.add(u_dealer3)
        await db.flush()
        p_dealer3 = UserProfile(user_id=u_dealer3.id, full_name="Shreeji Corporate Desk", city_id=indore.id)
        db.add(p_dealer3)

        d_shreeji = Dealer(
            user_id=u_dealer3.id,
            dealership_name="Shreeji Mahindra Indore",
            legal_entity_name="Shreeji Automotives Central India Pvt Ltd",
            gstin="23AABCS9988H3Z3",
            city_id=indore.id,
            address="Dewas Naka, Lasudia Mori, Indore, MP - 452010",
            authorized_brands=["Mahindra"],
            verification_status="VERIFIED",
            verification_notes="Verified OEM Franchise.",
            verified_at=datetime.now(timezone.utc)
        )
        db.add(d_shreeji)

        await db.flush()

        # 6. SAMPLE BUYING GROUPS (Different lifecycles)
        # Group 1: Tata Nexon Petrol (OFFERS_AVAILABLE - Active quotations ready for side-by-side comparison!)
        g_nexon = BuyingGroup(
            group_code="GL-IND-NEXON-001",
            vehicle_variant_id=var_nexon_cre_petrol.id,
            city_id=indore.id,
            created_by_user_id=u_buyer1.id,
            status="OFFERS_AVAILABLE",
            target_members=5,
            current_members_count=5,
            target_purchase_timeline="WITHIN_30_DAYS",
            bidding_start_time=datetime.now(timezone.utc) - timedelta(days=2),
            bidding_end_time=datetime.now(timezone.utc) + timedelta(days=5),
            additional_notes="Prefers White or Daytona Grey colours. PDI inspection prior to registration."
        )
        db.add(g_nexon)
        await db.flush()

        # Members for Group 1
        m1 = GroupMember(group_id=g_nexon.id, user_id=u_buyer1.id, status="ACTIVE", buyer_notes="White color preferred")
        m2 = GroupMember(group_id=g_nexon.id, user_id=u_buyer2.id, status="ACTIVE", buyer_notes="Ready for immediate delivery")
        db.add_all([m1, m2])

        # Group 2: Maruti Brezza VXi (BIDDING_OPEN - Currently accepting dealer quotations)
        g_brezza = BuyingGroup(
            group_code="GL-IND-BREZZA-002",
            vehicle_variant_id=var_brezza_vxi.id,
            city_id=indore.id,
            created_by_user_id=u_buyer2.id,
            status="BIDDING_OPEN",
            target_members=4,
            current_members_count=4,
            target_purchase_timeline="WITHIN_15_DAYS",
            bidding_start_time=datetime.now(timezone.utc) - timedelta(hours=12),
            bidding_end_time=datetime.now(timezone.utc) + timedelta(days=3),
            additional_notes="Looking for Magma Grey & Pearl Arctic White."
        )
        db.add(g_brezza)
        await db.flush()
        db.add(GroupMember(group_id=g_brezza.id, user_id=u_buyer2.id, status="ACTIVE"))

        # Group 3: Ather 450X EV (OPEN - Gathering members)
        g_ather = BuyingGroup(
            group_code="GL-IND-ATHER-003",
            vehicle_variant_id=var_ather_37.id,
            city_id=indore.id,
            created_by_user_id=u_buyer1.id,
            status="OPEN",
            target_members=10,
            current_members_count=6,
            target_purchase_timeline="WITHIN_30_DAYS",
            additional_notes="Looking for Space Grey & Lunar Grey with portable charger."
        )
        db.add(g_ather)
        await db.flush()
        db.add(GroupMember(group_id=g_ather.id, user_id=u_buyer1.id, status="ACTIVE"))

        # Group 4: Scorpio-N (QUALIFYING - Reached target, validating buyer purchase readiness)
        g_scorpio = BuyingGroup(
            group_code="GL-IND-SCORP-004",
            vehicle_variant_id=var_scorpio_z8.id,
            city_id=indore.id,
            created_by_user_id=u_buyer1.id,
            status="QUALIFYING",
            target_members=3,
            current_members_count=3,
            target_purchase_timeline="WITHIN_60_DAYS",
            additional_notes="Corporate finance options needed."
        )
        db.add(g_scorpio)
        await db.flush()
        db.add(GroupMember(group_id=g_scorpio.id, user_id=u_buyer1.id, status="ACTIVE"))

        # 7. DEALER INVITATIONS
        inv_sanghi = DealerGroupInvitation(
            group_id=g_nexon.id,
            dealer_id=d_sanghi.id,
            status="SUBMITTED"
        )
        inv_patel = DealerGroupInvitation(
            group_id=g_brezza.id,
            dealer_id=d_patel.id,
            status="INVITED"
        )
        db.add_all([inv_sanghi, inv_patel])
        await db.flush()

        # 8. REALISTIC VEHICLE-AGNOSTIC QUOTATION FOR GROUP 1 (Tata Nexon)
        # Sanghi Brothers Quote:
        # Base Ex-Showroom: ₹11,69,000.00
        # RTO MP (8%): ₹93,520.00
        # Insurance (1 yr OD + 3 yr TP): ₹42,100.00
        # Statutory TCS (1% > 10L): ₹11,690.00
        # Fastag & Logistics: ₹1,500.00
        # Basic Essential Kit: ₹8,500.00
        # Gross: ₹13,26,310.00
        # Group Discounts:
        # OEM Group Consumer Scheme: -₹25,000.00
        # Sanghi Dealership Group Volume Benefit: -₹35,000.00
        # Exchange Bonus: -₹15,000.00
        # Corporate Perk: -₹5,000.00
        # Total Discounts: -₹80,000.00
        # Final On-Road Price: ₹12,46,310.00 (Savings of ₹80,000 per buyer in group!)
        quote_sanghi = Quotation(
            group_id=g_nexon.id,
            dealer_id=d_sanghi.id,
            revision_number=1,
            status="APPROVED", # Approved by admin, visible to buyers
            admin_review_notes="Verified by admin. Complies with MP RTO tax brackets and OEM guidelines.",
            base_ex_showroom=Decimal("1169000.00"),
            rto_road_tax=Decimal("93520.00"),
            insurance_amount=Decimal("42100.00"),
            tcs_amount=Decimal("11690.00"),
            mfg_discount=Decimal("25000.00"),
            dealer_discount=Decimal("35000.00"),
            exchange_bonus=Decimal("15000.00"),
            corporate_discount=Decimal("5000.00"),
            accessories_amount=Decimal("8500.00"),
            logistics_handling=Decimal("1500.00"),
            other_statutory_charges=Decimal("0.00"),
            final_on_road_price=Decimal("1246310.00"),
            delivery_timeline_days=14,
            offer_valid_until=datetime.now(timezone.utc) + timedelta(days=7),
            remarks="Exclusive cohort pricing for Indore buyers. Free Teflon coating and 3-year RSA included."
        )
        db.add(quote_sanghi)
        await db.flush()

        # Quotation Line Items
        li1 = QuotationLineItem(quotation_id=quote_sanghi.id, item_name="3D All-Weather Floor Mats", item_type="COMPLIMENTARY", amount=Decimal("3500.00"))
        li2 = QuotationLineItem(quotation_id=quote_sanghi.id, item_name="Mud Flaps & Body Cover", item_type="COMPLIMENTARY", amount=Decimal("2800.00"))
        li3 = QuotationLineItem(quotation_id=quote_sanghi.id, item_name="Ceramic Gloss Protection", item_type="OPTIONAL", amount=Decimal("14500.00"))
        db.add_all([li1, li2, li3])

        # 9. BUYER LEAD (Rahul Sharma requested callback from Sanghi Motors)
        lead1 = BuyerLead(
            group_id=g_nexon.id,
            buyer_id=u_buyer1.id,
            dealer_id=d_sanghi.id,
            quotation_id=quote_sanghi.id,
            status="CONTACTED",
            buyer_consent_given=True,
            notes="Buyer requested test drive at Vijay Nagar residence on Saturday morning."
        )
        db.add(lead1)

        # 10. NOTIFICATIONS
        notif1 = Notification(
            user_id=u_buyer1.id,
            title="Quotation Approved for Your Group!",
            message="Sanghi Brothers Tata Motors submitted an approved offer of ₹12,46,310 (₹80,000 group discount) for GL-IND-NEXON-001.",
            event_type="OFFER_AVAILABLE",
            link_url=f"/groups/{g_nexon.id}"
        )
        db.add(notif1)

        await db.commit()
        print("[SUCCESS] Realistic Indore pilot seed data initialized successfully!")

if __name__ == "__main__":
    asyncio.run(seed_all())

