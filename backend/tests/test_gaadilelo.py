import pytest
import pytest_asyncio
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.pricing_engine import PricingEngine
from backend.app.schemas.schemas import PricingCalculationRequest

@pytest.mark.asyncio
async def test_pricing_engine_calculations():
    # 1. Test calculation below TCS threshold (< 10 Lakhs)
    req_sub_10l = PricingCalculationRequest(
        base_ex_showroom=Decimal("800000.00"),
        rto_road_tax=Decimal("64000.00"),
        insurance_amount=Decimal("30000.00"),
        mfg_discount=Decimal("20000.00"),
        dealer_discount=Decimal("15000.00")
    )
    res_sub_10l = PricingEngine.calculate_pricing(req_sub_10l)
    assert res_sub_10l.tcs_applicable is False
    assert res_sub_10l.calculated_tcs == Decimal("0.00")
    # Gross: 800000 + 64000 + 30000 = 894000. Discounts: 35000. On-road: 859000
    assert res_sub_10l.calculated_on_road_price == Decimal("859000.00")

    # 2. Test calculation above TCS threshold (> 10 Lakhs, e.g. 15 Lakhs)
    req_above_10l = PricingCalculationRequest(
        base_ex_showroom=Decimal("1500000.00"),
        rto_road_tax=Decimal("120000.00"),
        insurance_amount=Decimal("50000.00"),
        dealer_discount=Decimal("50000.00")
    )
    res_above_10l = PricingEngine.calculate_pricing(req_above_10l)
    assert res_above_10l.tcs_applicable is True
    # 1% of 15,00,000 = 15,000
    assert res_above_10l.calculated_tcs == Decimal("15000.00")
    # Gross: 1500000 + 120000 + 50000 + 15000 = 1685000. Discount: 50000. Final: 1635000
    assert res_above_10l.calculated_on_road_price == Decimal("1635000.00")

@pytest.mark.asyncio
async def test_pricing_engine_discount_validation():
    # Discounts exceeding ex-showroom must be rejected
    invalid_req = PricingCalculationRequest(
        base_ex_showroom=Decimal("500000.00"),
        dealer_discount=Decimal("600000.00")
    )
    with pytest.raises(ValueError, match="cannot exceed ex-showroom"):
        PricingEngine.calculate_pricing(invalid_req)

@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["pilot_city"] == "Indore"

@pytest.mark.asyncio
async def test_auth_login_admin():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/auth/login", json={
            "email": "admin@gaadilelo.com",
            "password": "Admin@123"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "ADMIN"

@pytest.mark.asyncio
async def test_catalog_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Cities
        res_cities = await ac.get("/api/v1/catalog/cities")
        assert res_cities.status_code == 200
        cities = res_cities.json()
        assert any(c["name"] == "Indore" for c in cities)

        # Categories
        res_cats = await ac.get("/api/v1/catalog/categories")
        assert res_cats.status_code == 200
        cats = res_cats.json()
        assert len(cats) >= 5

        # Brands
        res_brands = await ac.get("/api/v1/catalog/brands")
        assert res_brands.status_code == 200
        brands = res_brands.json()
        assert len(brands) >= 5
        assert any(b["name"] == "Tata Motors" for b in brands)

        # Brands by category
        res_car_brands = await ac.get("/api/v1/catalog/brands?category_id=car")
        assert res_car_brands.status_code == 200
        car_brands = res_car_brands.json()
        assert any(b["name"] == "Tata Motors" for b in car_brands)

        # Models
        res_models = await ac.get("/api/v1/catalog/models")
        assert res_models.status_code == 200
        models = res_models.json()
        assert any("Nexon" in m["name"] for m in models)

@pytest.mark.asyncio
async def test_groups_and_approved_offers():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get groups
        res_groups = await ac.get("/api/v1/groups")
        assert res_groups.status_code == 200
        groups = res_groups.json()
        assert len(groups) > 0

        # Find the group with OFFERS_AVAILABLE
        offer_group = next((g for g in groups if g["status"] == "OFFERS_AVAILABLE"), None)
        assert offer_group is not None

        # Check approved offers comparison
        res_offers = await ac.get(f"/api/v1/groups/{offer_group['id']}/offers")
        assert res_offers.status_code == 200
        offers = res_offers.json()
        assert len(offers) >= 1
        first_offer = offers[0]
        assert first_offer["status"] == "APPROVED"
        assert float(first_offer["final_on_road_price"]) > 0
        assert "Sanghi Brothers" in first_offer["dealership_name"]

@pytest.mark.asyncio
async def test_rbac_admin_protected_route():
    # Unauthorized request to admin overview without token
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/admin/overview")
        assert res.status_code in [401, 403]


@pytest.mark.asyncio
async def test_group_creation_and_duplicate_membership():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login as buyer
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "rahul.sharma@gmail.com",
            "password": "Buyer@123"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get variants and cities
        res_models = await ac.get("/api/v1/catalog/models")
        model = res_models.json()[0]
        variant_id = model["variants"][0]["id"]

        res_cities = await ac.get("/api/v1/catalog/cities")
        city_id = res_cities.json()[0]["id"]

        # Create a new group
        create_res = await ac.post("/api/v1/groups", json={
            "vehicle_variant_id": variant_id,
            "city_id": city_id,
            "target_members": 3,
            "target_purchase_timeline": "WITHIN_15_DAYS",
            "additional_notes": "Automated test group"
        }, headers=headers)
        assert create_res.status_code == 200
        new_group = create_res.json()
        assert new_group["status"] == "OPEN"
        assert new_group["current_members_count"] == 1

        # Attempt to join the same group again with the same buyer (Duplicate prevention)
        dup_join = await ac.post(f"/api/v1/groups/{new_group['id']}/join", headers=headers)
        assert dup_join.status_code == 400
        assert "already an active member" in dup_join.json()["detail"]

@pytest.mark.asyncio
async def test_dealer_quotation_and_revision_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login as dealer
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "sales@sanghimotors.com",
            "password": "Dealer@123"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get dealer dashboard stats
        dash_res = await ac.get("/api/v1/dealers/dashboard", headers=headers)
        assert dash_res.status_code == 200
        stats = dash_res.json()
        assert stats["quotations_submitted_count"] >= 1

        # Get dealer leads
        leads_res = await ac.get("/api/v1/dealers/leads", headers=headers)
        assert leads_res.status_code == 200
        leads = leads_res.json()
        assert len(leads) >= 1
        assert "Rahul Sharma" in leads[0]["buyer_name"]
