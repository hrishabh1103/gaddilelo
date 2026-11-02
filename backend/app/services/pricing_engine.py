from decimal import Decimal
from typing import Dict, Any, Tuple
from backend.app.schemas.schemas import PricingCalculationRequest, PricingCalculationResponse

class PricingEngine:
    """
    Vehicle-Agnostic Pricing Engine for GaadiLelo.com
    Supports 2-wheelers, 3-wheelers, passenger cars, commercial vehicles, and EVs.
    Validates components, handles statutory TCS thresholds (India > 10 Lakhs INR),
    and strictly validates discounts to prevent negative margins or double-counting.
    """
    
    TCS_THRESHOLD = Decimal("1000000.00")  # 10 Lakh INR
    TCS_RATE = Decimal("0.01")             # 1% standard Indian statutory TCS

    @classmethod
    def calculate_pricing(cls, payload: PricingCalculationRequest) -> PricingCalculationResponse:
        base = payload.base_ex_showroom
        rto = payload.rto_road_tax
        ins = payload.insurance_amount
        acc = payload.accessories_amount
        log = payload.logistics_handling
        oth = payload.other_statutory_charges
        
        # Calculate auto TCS if base exceeds statutory threshold and user didn't specify or wants verification
        tcs_applicable = base > cls.TCS_THRESHOLD
        suggested_tcs = (base * cls.TCS_RATE).quantize(Decimal("0.01")) if tcs_applicable else Decimal("0.00")
        actual_tcs = payload.tcs_amount if payload.tcs_amount > Decimal("0") else suggested_tcs

        # Total Additions (Gross Price)
        gross_price = (base + rto + ins + actual_tcs + acc + log + oth).quantize(Decimal("0.01"))

        # Total Deductions (Discounts & Incentives)
        mfg_disc = payload.mfg_discount
        dealer_disc = payload.dealer_discount
        exch = payload.exchange_bonus
        corp = payload.corporate_discount
        
        total_discounts = (mfg_disc + dealer_disc + exch + corp).quantize(Decimal("0.01"))

        # Safety check: discounts cannot exceed base vehicle price
        if total_discounts > base:
            raise ValueError(f"Total discounts (₹{total_discounts}) cannot exceed ex-showroom price (₹{base})")

        final_on_road = (gross_price - total_discounts).quantize(Decimal("0.01"))

        breakdown = {
            "base_ex_showroom": base,
            "rto_road_tax": rto,
            "insurance_amount": ins,
            "tcs_amount": actual_tcs,
            "accessories_amount": acc,
            "logistics_handling": log,
            "other_statutory_charges": oth,
            "gross_price": gross_price,
            "mfg_discount": mfg_disc,
            "dealer_discount": dealer_disc,
            "exchange_bonus": exch,
            "corporate_discount": corp,
            "total_discounts": total_discounts,
            "final_on_road_price": final_on_road
        }

        return PricingCalculationResponse(
            gross_price=gross_price,
            total_discounts=total_discounts,
            calculated_on_road_price=final_on_road,
            tcs_applicable=tcs_applicable,
            calculated_tcs=actual_tcs,
            breakdown_summary=breakdown
        )

    @classmethod
    def validate_quotation_math(
        cls,
        base: Decimal,
        rto: Decimal,
        insurance: Decimal,
        tcs: Decimal,
        acc: Decimal,
        logistics: Decimal,
        other: Decimal,
        mfg_disc: Decimal,
        dealer_disc: Decimal,
        exchange: Decimal,
        corp_disc: Decimal,
        submitted_final_price: Decimal
    ) -> Tuple[bool, Decimal, str]:
        """
        Validates that submitted dealer quotation arithmetic exactly matches system formulas.
        Returns (is_valid, expected_price, error_message)
        """
        additions = base + rto + insurance + tcs + acc + logistics + other
        deductions = mfg_disc + dealer_disc + exchange + corp_disc
        
        if deductions > base:
            return False, Decimal(0), f"Discounts (₹{deductions}) cannot exceed base ex-showroom (₹{base})"

        expected_final = (additions - deductions).quantize(Decimal("0.01"))
        submitted = submitted_final_price.quantize(Decimal("0.01"))

        # Allow slight 1-rupee rounding tolerance for cent/paisa rounding
        if abs(expected_final - submitted) > Decimal("1.00"):
            return False, expected_final, f"Price mismatch: Submitted on-road price ₹{submitted} does not equal calculated total ₹{expected_final}"

        return True, expected_final, ""
