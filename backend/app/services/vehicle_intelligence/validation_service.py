from typing import Dict, Any, List, Tuple
from decimal import Decimal

class ValidationResult:
    def __init__(self, is_valid: bool, confidence_score: float, issues: List[str], conflicts: List[str]):
        self.is_valid = is_valid
        self.confidence_score = confidence_score
        self.issues = issues
        self.conflicts = conflicts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "confidence_score": self.confidence_score,
            "issues": self.issues,
            "conflicts": self.conflicts
        }


class ValidationService:
    """
    Validates physical plausibility, completeness, and source consistency of extracted vehicle data.
    """

    @classmethod
    def validate_vehicle(cls, data: Dict[str, Any]) -> ValidationResult:
        issues: List[str] = []
        conflicts: List[str] = []
        confidence = 1.0

        brand = data.get("brand") or data.get("brand_name")
        model = data.get("model") or data.get("model_name")
        variants = data.get("variants") or []

        if not brand or len(str(brand).strip()) < 2:
            issues.append("Missing or invalid manufacturer brand name.")
            confidence -= 0.3
        
        if not model or len(str(model).strip()) < 2:
            issues.append("Missing or invalid vehicle model name.")
            confidence -= 0.3

        if not variants:
            issues.append("Vehicle has no identified variants.")
            confidence -= 0.25

        # Check Prices
        min_p = data.get("min_price") or data.get("reference_ex_showroom_min") or 0
        max_p = data.get("max_price") or data.get("reference_ex_showroom_max") or 0
        
        try:
            min_dec = Decimal(str(min_p))
            max_dec = Decimal(str(max_p))
            if min_dec <= 0:
                issues.append("Reference price cannot be zero or negative.")
                confidence -= 0.2
            if max_dec > Decimal("150000000"):
                issues.append("Reference price exceeds standard Indian automotive ceiling.")
                confidence -= 0.1
            if min_dec > max_dec and max_dec > 0:
                issues.append("Minimum price cannot exceed maximum price.")
                confidence -= 0.15
        except Exception:
            issues.append("Malformed price format.")
            confidence -= 0.2

        # Validate Variants
        for idx, v in enumerate(variants):
            v_name = v.get("name") or v.get("variant_name")
            if not v_name:
                issues.append(f"Variant #{idx+1} lacks a distinct name.")
                confidence -= 0.05
            
            # Fuel type and transmission check
            fuel = (v.get("fuel_type") or "").upper()
            if fuel not in ["PETROL", "DIESEL", "CNG", "ELECTRIC", "HYBRID"]:
                issues.append(f"Variant '{v_name}' has unknown fuel type '{fuel}'.")
                confidence -= 0.05

            specs = v.get("specs") or v.get("specifications") or {}

            # Plausibility checks
            if fuel == "ELECTRIC":
                # Battery check
                batt_str = str(v.get("engine_or_battery") or specs.get("battery") or "")
                if batt_str and "kwh" in batt_str.lower():
                    try:
                        import re
                        m = re.search(r"(\d+(\.\d+)?)", batt_str)
                        if m:
                            kwh = float(m.group(1))
                            if kwh < 1.0 or kwh > 250.0:
                                issues.append(f"Plausibility warning: Battery capacity {kwh} kWh is out of standard range.")
                                confidence -= 0.1
                    except Exception:
                        pass

        # Check for cross-source conflicts if provided in raw payload
        raw_conflicts = data.get("conflicts") or []
        for c in raw_conflicts:
            conflicts.append(str(c))
            confidence -= 0.1

        confidence = max(0.1, min(1.0, round(confidence, 2)))
        is_valid = len(issues) == 0 or confidence >= 0.6

        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            issues=issues,
            conflicts=conflicts
        )

