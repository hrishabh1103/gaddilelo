import urllib.parse
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.models import VehicleModel

class WikidataEnricher:
    """
    Wikidata Structured Knowledge Graph Integration (https://www.wikidata.org/).
    Enriches vehicle catalog models with structured manufacturer metadata, physical dimensions,
    inception dates, and Wikimedia primary file references.
    
    100% Free, Public Domain (CC0 1.0 Universal).
    """

    WIKIDATA_API = "https://www.wikidata.org/w/api.php"
    USER_AGENT = "GaadiLeloBot/1.0 (+https://gaadilelo.com/bot; bot@gaadilelo.com)"

    # Wikidata Property Identifiers
    P_INSTANCE_OF = "P31"
    P_MANUFACTURER = "P176"
    P_IMAGE = "P18"
    P_LENGTH = "P2043"
    P_WIDTH = "P2049"
    P_HEIGHT = "P2048"
    P_COUNTRY_OF_ORIGIN = "P495"
    P_INCEPTION = "P571"

    @classmethod
    async def search_entity(cls, query: str) -> Optional[Dict[str, Any]]:
        """Searches Wikidata for candidate entity identifier (QID)."""
        headers = {"User-Agent": cls.USER_AGENT}
        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "limit": "3",
            "format": "json"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(cls.WIKIDATA_API, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("search", [])
                    if results:
                        # Prefer automotive / transport description
                        for r in results:
                            desc = (r.get("description") or "").lower()
                            if any(k in desc for k in ["car", "vehicle", "automobile", "motorcycle", "scooter", "suv", "truck"]):
                                return r
                        return results[0]
        except Exception as e:
            print(f"[WikidataEnricher] Entity search failed: {e}")
        return None

    @classmethod
    async def get_entity_claims(cls, entity_id: str) -> Optional[Dict[str, Any]]:
        """Fetches structured properties/claims for a given Wikidata entity."""
        headers = {"User-Agent": cls.USER_AGENT}
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "props": "claims|labels|descriptions",
            "format": "json"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(cls.WIKIDATA_API, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("entities", {}).get(entity_id)
        except Exception as e:
            print(f"[WikidataEnricher] Property retrieval failed: {e}")
        return None

    @classmethod
    def _parse_dimension(cls, claim_list: Optional[list]) -> Optional[int]:
        """Extracts numerical millimeter value from Wikidata dimension claim."""
        if not claim_list:
            return None
        try:
            val_dict = claim_list[0]["mainsnak"]["datavalue"]["value"]
            amt = float(val_dict["amount"])
            unit = val_dict.get("unit", "")
            # Q174789 = millimetre, Q11573 = metre
            if "Q11573" in unit:
                return int(amt * 1000)
            return int(amt)
        except Exception:
            return None

    @classmethod
    async def enrich_model(cls, model_id: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Enriches a VehicleModel with Wikidata properties (dimensions, wikidata_id, etc.).
        """
        model = (await db.execute(select(VehicleModel).where(VehicleModel.id == model_id))).scalar_one_or_none()
        if not model:
            return {"status": "FAILED", "error": "Model not found"}

        brand_name = model.brand.name if model.brand else ""
        query = f"{brand_name} {model.name}".strip()

        entity_match = await cls.search_entity(query)
        if not entity_match:
            return {"status": "NOT_FOUND", "message": f"No Wikidata entity found for '{query}'"}

        qid = entity_match["id"]
        entity = await cls.get_entity_claims(qid)
        if not entity:
            return {"status": "FAILED", "error": f"Failed to retrieve properties for {qid}"}

        claims = entity.get("claims", {})

        length_mm = cls._parse_dimension(claims.get(cls.P_LENGTH))
        width_mm = cls._parse_dimension(claims.get(cls.P_WIDTH))
        height_mm = cls._parse_dimension(claims.get(cls.P_HEIGHT))

        # Update model
        model.wikidata_id = qid
        if length_mm and not model.length_mm:
            model.length_mm = length_mm
        if width_mm and not model.width_mm:
            model.width_mm = width_mm
        if height_mm and not model.height_mm:
            model.height_mm = height_mm

        model.last_verified_at = datetime.now(timezone.utc)
        await db.commit()

        return {
            "status": "ENRICHED",
            "wikidata_id": qid,
            "label": entity.get("labels", {}).get("en", {}).get("value"),
            "description": entity.get("descriptions", {}).get("en", {}).get("value"),
            "length_mm": length_mm,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "wikidata_url": f"https://www.wikidata.org/wiki/{qid}"
        }

