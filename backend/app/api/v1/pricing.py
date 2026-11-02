from fastapi import APIRouter, HTTPException
from backend.app.schemas.schemas import PricingCalculationRequest, PricingCalculationResponse
from backend.app.services.pricing_engine import PricingEngine

router = APIRouter(prefix="/pricing", tags=["Pricing Engine"])

@router.post("/calculate", response_model=PricingCalculationResponse)
async def calculate_vehicle_pricing(payload: PricingCalculationRequest):
    try:
        return PricingEngine.calculate_pricing(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

