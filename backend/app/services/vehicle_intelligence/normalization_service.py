import re
from typing import Dict, Any, Tuple, Optional
from decimal import Decimal

class NormalizationService:
    """
    Standardizes units, currency representations, and automotive nomenclature.
    """

    @staticmethod
    def normalize_price(price_input: Any) -> Decimal:
        """Converts strings like '₹11.69 Lakh', '1.2 Cr', or numeric inputs to exact Decimal INR."""
        if price_input is None:
            return Decimal("0.00")
        
        if isinstance(price_input, (int, float, Decimal)):
            return Decimal(str(price_input))
        
        text = str(price_input).strip().lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("inr", "").strip()
        
        # Check Lakh / L
        if "lakh" in text or "lac" in text or text.endswith("l"):
            num_str = re.sub(r"[^\d.]", "", text)
            if num_str:
                return (Decimal(num_str) * Decimal("100000")).quantize(Decimal("1.00"))
        
        # Check Crore / Cr
        if "crore" in text or "cr" in text:
            num_str = re.sub(r"[^\d.]", "", text)
            if num_str:
                return (Decimal(num_str) * Decimal("10000000")).quantize(Decimal("1.00"))
        
        # Pure digits
        clean_num = re.sub(r"[^\d.]", "", text)
        if clean_num:
            return Decimal(clean_num).quantize(Decimal("1.00"))
        
        return Decimal("0.00")

    @staticmethod
    def normalize_power(power_str: str) -> Tuple[Optional[float], str]:
        """Normalizes power strings (BHP, kW, HP, PS) into metric PS."""
        if not power_str:
            return None, "PS"
        s = power_str.strip().lower()
        val_match = re.search(r"(\d+(\.\d+)?)", s)
        if not val_match:
            return None, "PS"
        val = float(val_match.group(1))

        if "kw" in s:
            return round(val * 1.35962, 1), "PS"
        elif "bhp" in s or "hp" in s:
            return round(val * 1.01387, 1), "PS"
        return round(val, 1), "PS"

    @staticmethod
    def normalize_torque(torque_str: str) -> Tuple[Optional[float], str]:
        """Normalizes torque strings (lb-ft, kgm, Nm) to Nm."""
        if not torque_str:
            return None, "Nm"
        s = torque_str.strip().lower()
        val_match = re.search(r"(\d+(\.\d+)?)", s)
        if not val_match:
            return None, "Nm"
        val = float(val_match.group(1))

        if "lb-ft" in s or "lbft" in s:
            return round(val * 1.3558, 1), "Nm"
        elif "kgm" in s:
            return round(val * 9.80665, 1), "Nm"
        return round(val, 1), "Nm"

    @staticmethod
    def normalize_fuel_type(fuel: str) -> str:
        f = (fuel or "").strip().upper()
        if "EV" in f or "ELEC" in f or "BATTERY" in f:
            return "ELECTRIC"
        if "DIESEL" in f:
            return "DIESEL"
        if "CNG" in f:
            return "CNG"
        if "HYBRID" in f:
            return "HYBRID"
        return "PETROL"

    @staticmethod
    def normalize_transmission(trans: str) -> str:
        t = (trans or "").strip().upper()
        if "SINGLE" in t or "EV" in t:
            return "SINGLE_SPEED_EV"
        if "DCT" in t or "DCA" in t or "DSG" in t:
            return "DCT"
        if "CVT" in t or "IVT" in t:
            return "CVT"
        if "AMT" in t or "AGS" in t:
            return "AMT"
        if "AUTO" in t or "AT" in t or "TORQUE" in t:
            return "AUTOMATIC"
        return "MANUAL"

    @staticmethod
    def clean_model_name(name: str) -> str:
        """Removes marketing prefixes like 'All-New', 'Facelift', '2026'."""
        cleaned = re.sub(r"(?i)\b(all[- ]new|facelift|refreshed|gen[- ]\d+|the new)\b", "", name)
        return " ".join(cleaned.split()).strip()

