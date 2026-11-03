import urllib.parse
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.models import VehicleImage, VehicleModel

class WikimediaImageService:
    """
    Wikimedia Commons Free Vehicle Image Pipeline.
    Website: https://commons.wikimedia.org/
    
    Responsibilities:
    - Queries Wikimedia Commons Search API with compliant User-Agent.
    - Validates open commercial licenses (CC BY, CC BY-SA, Public Domain, CC0).
    - Rejects restricted, non-commercial (NC), or unverified licenses.
    - Extracts author, source page URL, original image URL, and thumbnail URL.
    - Selects primary image and prevents duplicates.
    - Provides high-contrast SVG automotive fallback placeholders.
    """

    COMMONS_API = "https://commons.wikimedia.org/w/api.php"
    USER_AGENT = "GaadiLeloBot/1.0 (+https://gaadilelo.com/bot; bot@gaadilelo.com)"

    PERMITTED_LICENSES = [
        "public domain", "cc0", "cc0 1.0",
        "cc by 2.0", "cc by 2.5", "cc by 3.0", "cc by 4.0",
        "cc by-sa 2.0", "cc by-sa 2.5", "cc by-sa 3.0", "cc by-sa 4.0",
        "gfdl"
    ]

    REJECTED_KEYWORDS = ["noncommercial", "non-commercial", "-nc", "no derivatives", "-nd", "fair use"]

    @classmethod
    def is_license_permitted(cls, license_short_name: Optional[str]) -> bool:
        """Strictly validates whether an image has verified commercial reuse rights."""
        if not license_short_name:
            return False

        clean = license_short_name.lower().strip()
        # Immediately reject restrictive licenses
        if any(bad in clean for bad in cls.REJECTED_KEYWORDS):
            return False

        return any(ok in clean for ok in cls.PERMITTED_LICENSES)

    @classmethod
    async def search_vehicle_images(
        cls,
        brand_name: str,
        model_name: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Searches Wikimedia Commons for candidate images matching manufacturer and model.
        Returns validated images with author, license, and attribution metadata.
        """
        clean_model = model_name.replace(brand_name, "").strip()
        query = f"{brand_name} {clean_model}".strip()

        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": "6", # File namespace
            "gsrsearch": f"{query} filetype:bitmap",
            "gsrlimit": str(limit * 2), # Fetch extra to account for rejected licenses
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata|mime",
            "iiurlwidth": "800", # Request 800px thumbnail
            "format": "json"
        }

        headers = {"User-Agent": cls.USER_AGENT}
        candidates = []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(cls.COMMONS_API, params=params, headers=headers)
                if resp.status_code != 200:
                    return []

                data = resp.json()
                pages = data.get("query", {}).get("pages", {})

                for pid, p in pages.items():
                    info_list = p.get("imageinfo", [])
                    if not info_list:
                        continue
                    info = info_list[0]
                    meta = info.get("extmetadata", {})

                    # Extract metadata
                    title = p.get("title", "")
                    width = info.get("width", 0)
                    height = info.get("height", 0)
                    mime = info.get("mime", "")
                    raw_url = info.get("url", "")
                    thumb_url = info.get("thumburl", raw_url)

                    # Only accept standard web formats
                    if mime not in ["image/jpeg", "image/png", "image/webp"]:
                        continue

                    # Filter low quality thumbnails / icons
                    if width < 500 or height < 300:
                        continue

                    # License Extraction
                    license_name = meta.get("LicenseShortName", {}).get("value")
                    license_url = meta.get("LicenseUrl", {}).get("value")
                    artist_raw = meta.get("Artist", {}).get("value", "Wikimedia Commons Contributor")
                    # Clean HTML tags from artist string
                    artist_clean = re.sub(r"<[^>]+>", "", artist_raw).strip() or "Wikimedia Commons Contributor"

                    # Source Page on Commons
                    clean_title = title.replace("File:", "").replace(" ", "_")
                    source_page = f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(clean_title)}"

                    # License Permission Check
                    if not cls.is_license_permitted(license_name):
                        continue

                    attribution_html = f'<a href="{source_page}" target="_blank" rel="noopener">Photo</a> by {artist_clean} / <a href="{license_url or "https://creativecommons.org/"}" target="_blank" rel="noopener">{license_name}</a>'

                    candidates.append({
                        "title": title,
                        "image_url": raw_url,
                        "thumbnail_url": thumb_url,
                        "source_url": raw_url,
                        "source_page_url": source_page,
                        "author_name": artist_clean,
                        "license_name": license_name,
                        "license_url": license_url,
                        "attribution_html": attribution_html,
                        "width": width,
                        "height": height,
                        "usage_rights_status": "PUBLIC_COMMONS",
                        "verification_status": "VERIFIED"
                    })

                    if len(candidates) >= limit:
                        break

        except Exception as e:
            print(f"[WikimediaImageService] Wikimedia search failed: {e}")

        return candidates

    @classmethod
    async def attach_images_to_model(
        cls,
        model_id: str,
        db: AsyncSession
    ) -> List[VehicleImage]:
        """
        Discovers, validates, and persists Wikimedia images for a given vehicle model.
        Sets primary image and prevents duplicates.
        """
        from sqlalchemy.orm import selectinload
        model = (await db.execute(
            select(VehicleModel).options(selectinload(VehicleModel.brand)).where(VehicleModel.id == model_id)
        )).scalar_one_or_none()
        if not model:
            return []

        brand_name = getattr(model, "canonical_brand_name", None) or (model.brand.name if model.brand else "")
        candidates = await cls.search_vehicle_images(brand_name=brand_name, model_name=model.name, limit=3)

        attached = []
        is_first = True

        for c in candidates:
            # Duplicate check by image_url
            dup = (await db.execute(
                select(VehicleImage).where(VehicleImage.image_url == c["image_url"]).limit(1)
            )).scalars().first()
            if dup:
                continue

            img = VehicleImage(
                vehicle_model_id=model.id,
                image_url=c["image_url"],
                thumbnail_url=c["thumbnail_url"],
                source_url=c["source_url"],
                source_page_url=c["source_page_url"],
                author_name=c["author_name"],
                license_name=c["license_name"],
                license_url=c["license_url"],
                attribution_html=c["attribution_html"],
                usage_rights_status="PUBLIC_COMMONS",
                verification_status="VERIFIED",
                width=c["width"],
                height=c["height"],
                is_primary=is_first
            )
            db.add(img)
            attached.append(img)

            # Update primary model image_url
            if is_first and not model.image_url:
                model.image_url = c["thumbnail_url"] or c["image_url"]

            is_first = False

        if attached:
            await db.commit()

        return attached

    @classmethod
    def get_fallback_placeholder(cls, vehicle_name: str) -> str:
        """Returns a stable, self-contained SVG automotive placeholder."""
        clean_name = urllib.parse.quote(vehicle_name)
        return f"https://placehold.co/800x500/1e293b/ffffff?text={clean_name}+%28GaadiLelo%29"

