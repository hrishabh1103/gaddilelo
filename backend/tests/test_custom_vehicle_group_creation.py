import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal
from backend.app.models.models import User, City, BuyingGroup, VehicleModel, VehicleBrand
from sqlalchemy import select
from sqlalchemy.orm import selectinload

@pytest.mark.asyncio
async def test_custom_vehicle_group_creation_and_discovery():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login as buyer Rahul
        login_res = await client.post("/api/v1/auth/login", json={"email": "rahul.sharma@gmail.com", "password": "Buyer@123"})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Indore city ID
        cities_res = await client.get("/api/v1/catalog/cities")
        assert cities_res.status_code == 200
        cities = cities_res.json()
        indore = next(c for c in cities if c["name"].lower() == "indore")

        # 3. Submit custom vehicle group creation for Mahindra XEV 9e
        custom_payload = {
            "vehicle_variant_id": "OTHER",
            "city_id": indore["id"],
            "target_members": 5,
            "target_purchase_timeline": "WITHIN_30_DAYS",
            "additional_notes": "Interested in 79kWh variant with glass roof",
            "custom_brand_name": "Mahindra",
            "custom_model_name": "Mahindra XEV 9e",
            "custom_variant_name": "Pack One (59 kWh)",
            "custom_fuel_type": "ELECTRIC",
            "estimated_price": 2190000.0
        }

        res = await client.post("/api/v1/groups", json=custom_payload, headers=headers)
        assert res.status_code == 200, res.text
        data = res.json()
        assert "id" in data
        assert "GL-" in data["group_code"]
        assert "Mahindra" in data["vehicle_name"]
        assert "XEV 9e" in data["vehicle_name"]
        assert data["current_members_count"] == 1
        assert data["is_current_user_member"] is True

        # 4. Verify in DB
        async with AsyncSessionLocal() as db:
            m_res = await db.execute(
                select(VehicleModel)
                .options(selectinload(VehicleModel.brand), selectinload(VehicleModel.variants))
                .where(VehicleModel.name == "Mahindra XEV 9e")
            )
            m = m_res.scalars().first()
            assert m is not None
            assert m.brand.name == "Mahindra"
            assert len(m.variants) >= 1

        # 5. Test completely novel unlisted brand & model (e.g. Tesla Model Y)
        novel_payload = {
            "vehicle_variant_id": "OTHER",
            "city_id": indore["id"],
            "target_members": 3,
            "target_purchase_timeline": "WITHIN_15_DAYS",
            "custom_brand_name": "Tesla",
            "custom_model_name": "Model Y Long Range",
            "custom_variant_name": "Dual Motor AWD",
            "custom_fuel_type": "ELECTRIC",
            "estimated_price": 5990000.0
        }
        novel_res = await client.post("/api/v1/groups", json=novel_payload, headers=headers)
        assert novel_res.status_code == 200, novel_res.text
        n_data = novel_res.json()
        assert "Tesla" in n_data["vehicle_name"]
        assert "Model Y" in n_data["vehicle_name"]
