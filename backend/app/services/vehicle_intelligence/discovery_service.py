import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from backend.app.models.models import (
    VehicleDiscoveryJob, VehicleDiscoveryRecord, VehicleSpecificationSource,
    VehiclePriceHistory, VehicleImage, VehicleDiscoverySubscription,
    VehicleBrand, VehicleModel, VehicleVariant, VehicleCategory, City,
    User, Notification
)
from backend.app.services.vehicle_intelligence.source_registry import SourceRegistry, BaseSourceAdapter
from backend.app.services.vehicle_intelligence.extraction_service import ExtractionService
from backend.app.services.vehicle_intelligence.normalization_service import NormalizationService
from backend.app.services.vehicle_intelligence.validation_service import ValidationService
from backend.app.services.vehicle_intelligence.deduplication_service import DeduplicationService
from backend.app.services.vehicle_intelligence.update_service import UpdateService
from backend.app.services.vehicle_intelligence.oem_adapters import OEMSpecificationRegistry
from backend.app.services.vehicle_intelligence.wikimedia_image_service import WikimediaImageService
from backend.app.services.vehicle_intelligence.wikidata_enricher import WikidataEnricher
from backend.app.services.vehicle_intelligence.indian_government_data_service import IndianGovernmentDataService
from backend.app.services.notification_service import NotificationService

class DiscoveryService:
    """
    Central orchestration engine for Automated Vehicle Discovery & Customer Discovery Requests.
    """

    @classmethod
    async def create_customer_discovery_request(
        cls,
        search_query: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str],
        category_slug: Optional[str],
        target_city_id: Optional[str],
        user_id: Optional[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Processes a customer request for an unlisted vehicle.
        Creates job, queries sources, extracts specs, checks duplicates, and files PENDING_REVIEW record.
        """
        # 1. Create Discovery Job
        job = VehicleDiscoveryJob(
            search_query=search_query,
            requested_by_user_id=user_id,
            job_type="CUSTOMER_REQUEST",
            status="IN_PROGRESS"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        try:
            # 2. Query Free Automotive Sources
            active_adapter = None
            raw_details = None

            # Priority 1: Check OEM Direct Specification Registry
            oem_match = OEMSpecificationRegistry.match_model(search_query)
            if oem_match:
                m_details = oem_match["details"]
                raw_details = {
                    "brand": oem_match["brand"],
                    "model": oem_match["model"],
                    "category_slug": m_details.get("category", "car"),
                    "body_type": m_details.get("body_type", "SUV"),
                    "model_year": 2026,
                    "launch_status": "LAUNCHED",
                    "min_price": min([v["price"] for v in m_details["variants"]]) if m_details.get("variants") else 1000000,
                    "max_price": max([v["price"] for v in m_details["variants"]]) if m_details.get("variants") else 1500000,
                    "dimensions": {
                        "length_mm": m_details.get("length_mm"),
                        "width_mm": m_details.get("width_mm"),
                        "height_mm": m_details.get("height_mm"),
                        "wheelbase_mm": m_details.get("wheelbase_mm"),
                        "ground_clearance_mm": m_details.get("ground_clearance_mm")
                    },
                    "safety": {
                        "stars": m_details.get("safety_rating"),
                        "agency": m_details.get("safety_agency")
                    },
                    "variants": [
                        {
                            "name": v["name"],
                            "fuel_type": v.get("fuel", "PETROL"),
                            "transmission": v.get("trans", "MANUAL"),
                            "price": v.get("price", 1000000),
                            "engine_or_battery": v.get("engine") or v.get("battery"),
                            "seating_capacity": v.get("seating", 5),
                            "specs": {
                                **v,
                                "source_priority": 1,
                                "source": f"{oem_match['brand']} Official Specification"
                            }
                        }
                        for v in m_details.get("variants", [])
                    ]
                }
                source_url = oem_match["portal_url"]
                source_name = f"{oem_match['brand']} Official Specification (Priority 1) [source_attribution: OEM INGLO Portal]"
            else:
                for candidate in SourceRegistry.list_adapters():
                    try:
                        details = await candidate.fetch_vehicle_details(search_query)
                        if details:
                            raw_details = details
                            active_adapter = candidate
                            break
                    except Exception as ex:
                        print(f"[DiscoveryService] Error querying {candidate.source_name}: {ex}")

                if not raw_details:
                    raw_details = search_query
                    source_url = "https://press.gaadilelo.com/candidate-discovery"
                    source_name = "Automated Discovery Candidate"
                else:
                    source_url = active_adapter.source_url if active_adapter else "https://press.gaadilelo.com"
                    source_name = active_adapter.source_name if active_adapter else "Authorized OEM Source"

            # 3. Extract Structured Specifications via Extraction Pipeline
            extracted = await ExtractionService.extract_from_content(
                raw_text_or_dict=raw_details,
                source_url=source_url,
                source_name=source_name
            )

            # 4. Enrich with Wikimedia Commons & Wikidata Free Open Data
            wiki_images = await WikimediaImageService.search_vehicle_images(
                brand_name=extracted.brand_name,
                model_name=extracted.model_name,
                limit=3
            )
            if wiki_images:
                extracted.image_urls = [img["image_url"] for img in wiki_images]
            elif not extracted.image_urls:
                extracted.image_urls = [
                    WikimediaImageService.get_fallback_placeholder(f"{extracted.brand_name} {extracted.model_name}")
                ]

            wikidata_entity = await WikidataEnricher.search_entity(f"{extracted.brand_name} {extracted.model_name}")

            # 5. Validate Specifications & Physical Plausibility
            val_result = ValidationService.validate_vehicle(extracted.model_dump())

            # 6. Check Database for Duplicates
            dup_result = await DeduplicationService.match_existing_vehicle(
                brand_name=extracted.brand_name,
                model_name=extracted.model_name,
                variants_candidate=[v.model_dump() for v in extracted.variants],
                db=db
            )

            # 7. Create Discovery Record
            extracted_json = extracted.model_dump(mode="json")
            if oem_match:
                extracted_json["dimensions"] = raw_details.get("dimensions", {})
                extracted_json["safety"] = raw_details.get("safety", {})
            if wikidata_entity:
                extracted_json["wikidata_id"] = wikidata_entity.get("id")

            rec = VehicleDiscoveryRecord(
                job_id=job.id,
                discovered_brand=extracted.brand_name,
                discovered_model=extracted.model_name,
                category_slug=category_slug or extracted.category_slug,
                body_type=extracted.body_type,
                launch_status=extracted.launch_status,
                model_year=extracted.model_year,
                reference_ex_showroom_min=extracted.reference_ex_showroom_min,
                reference_ex_showroom_max=extracted.reference_ex_showroom_max,
                extracted_data=extracted_json,
                confidence_score=Decimal(str(val_result.confidence_score)),
                review_status="PENDING_REVIEW",
                primary_source_url=extracted.source_url,
                primary_source_name=extracted.source_name
            )
            db.add(rec)
            await db.flush()

            # 8. Add Specification Sources for Field-Level Attribution & Priorities
            for v in extracted.variants:
                for field_k, field_v in v.specifications.items():
                    db.add(
                        VehicleSpecificationSource(
                            discovery_record_id=rec.id,
                            field_name=f"{v.variant_name}.{field_k}",
                            field_value=str(field_v),
                            source_url=extracted.source_url,
                            source_name=extracted.source_name,
                            source_priority=1 if oem_match else 3,
                            license_name="OFFICIAL_MANUFACTURER_DATA" if oem_match else "OPEN_DATA",
                            confidence_score=Decimal(str(val_result.confidence_score))
                        )
                    )

            # 9. Add Discovered Images with Wikimedia Attribution
            if wiki_images:
                for idx, wimg in enumerate(wiki_images):
                    db.add(
                        VehicleImage(
                            discovery_record_id=rec.id,
                            image_url=wimg["image_url"],
                            thumbnail_url=wimg.get("thumbnail_url"),
                            source_url=wimg["source_url"],
                            source_page_url=wimg.get("source_page_url"),
                            author_name=wimg.get("author_name"),
                            license_name=wimg.get("license_name"),
                            license_url=wimg.get("license_url"),
                            attribution_html=wimg.get("attribution_html"),
                            usage_rights_status="PUBLIC_COMMONS",
                            verification_status="VERIFIED",
                            width=wimg.get("width"),
                            height=wimg.get("height"),
                            is_primary=(idx == 0)
                        )
                    )
            else:
                for img in extracted.image_urls:
                    db.add(
                        VehicleImage(
                            discovery_record_id=rec.id,
                            image_url=img,
                            source_url=extracted.source_url,
                            usage_rights_status="OFFICIAL_OEM_PRESS",
                            is_primary=True
                        )
                    )

            # 9. Subscribe Customer to Notification Updates
            subscription = VehicleDiscoverySubscription(
                discovery_record_id=rec.id,
                user_id=user_id,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                target_city_id=target_city_id
            )
            db.add(subscription)

            # 10. Notify Admin about the New Discovery
            admin_users_res = await db.execute(select(User).where(User.role == "ADMIN"))
            admin_users = admin_users_res.scalars().all()
            for admin_user in admin_users:
                await NotificationService.create_notification(
                    user_id=admin_user.id,
                    title="Vehicle Discovery Pending Review",
                    message=f"New vehicle '{extracted.brand_name} {extracted.model_name}' discovered from {extracted.source_name}. Awaiting approval.",
                    event_type="VEHICLE_DISCOVERY_PENDING",
                    link_url=f"/admin/intelligence/review/{rec.id}",
                    db=db
                )

            # 11. Complete Job
            job.status = "COMPLETED"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(rec)

            return {
                "job_id": job.id,
                "record_id": rec.id,
                "status": "PENDING_REVIEW",
                "brand": rec.discovered_brand,
                "model": rec.discovered_model,
                "confidence": float(rec.confidence_score),
                "is_duplicate": dup_result.is_duplicate_model,
                "message": "Vehicle discovered and sent for verification. You will be notified once published!"
            }

        except Exception as e:
            await db.rollback()
            job.status = "FAILED"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()
            raise e

    @classmethod
    async def approve_and_publish_record(
        cls,
        record_id: str,
        reviewer_user_id: str,
        admin_notes: Optional[str],
        db: AsyncSession
    ) -> VehicleModel:
        """
        Approves a PENDING_REVIEW record, adds Brand, Model, and Variants to the catalogue,
        and dispatches notifications to all subscribed customers.
        """
        rec_res = await db.execute(
            select(VehicleDiscoveryRecord)
            .options(
                selectinload(VehicleDiscoveryRecord.subscriptions),
                selectinload(VehicleDiscoveryRecord.images)
            )
            .where(VehicleDiscoveryRecord.id == record_id)
        )
        rec = rec_res.scalar_one_or_none()
        if not rec:
            raise ValueError("Discovery record not found")

        # 1. Resolve Category
        cat_slug = rec.category_slug or "car"
        cat_res = await db.execute(select(VehicleCategory).where(VehicleCategory.slug == cat_slug))
        category = cat_res.scalar_one_or_none()
        if not category:
            cat_res = await db.execute(select(VehicleCategory))
            category = cat_res.scalars().first()

        # 2. Resolve or Create Brand
        brand_name = rec.discovered_brand.strip()
        brand_slug = re.sub(r"[^a-zA-Z0-9]+", "-", brand_name.lower()).strip("-")
        brand_res = await db.execute(select(VehicleBrand).where(VehicleBrand.name.ilike(brand_name)))
        brand = brand_res.scalar_one_or_none()
        if not brand:
            brand = VehicleBrand(
                category_id=category.id,
                name=brand_name,
                slug=brand_slug,
                logo_url="https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=100"
            )
            db.add(brand)
            await db.flush()

        # 3. Create Vehicle Model
        model_name = rec.discovered_model.strip()
        model_slug = re.sub(r"[^a-zA-Z0-9]+", "-", f"{brand_name}-{model_name}".lower()).strip("-")
        
        # Ensure unique slug
        existing_model_res = await db.execute(select(VehicleModel).where(VehicleModel.slug == model_slug))
        if existing_model_res.scalar_one_or_none():
            model_slug = f"{model_slug}-{str(uuid.uuid4())[:4]}"

        extracted = rec.extracted_data or {}
        img_url = (extracted.get("image_urls") or ["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800"])[0]
        dims = extracted.get("dimensions", {})
        safety = extracted.get("safety", {})
        wikidata_id = extracted.get("wikidata_id")

        model = VehicleModel(
            brand_id=brand.id,
            name=model_name,
            slug=model_slug,
            body_type=rec.body_type or "SUV",
            image_url=img_url,
            length_mm=dims.get("length_mm"),
            width_mm=dims.get("width_mm"),
            height_mm=dims.get("height_mm"),
            wheelbase_mm=dims.get("wheelbase_mm"),
            ground_clearance_mm=dims.get("ground_clearance_mm"),
            safety_rating_stars=safety.get("stars"),
            safety_rating_agency=safety.get("agency"),
            wikidata_id=wikidata_id,
            last_verified_at=datetime.now(timezone.utc),
            is_active=True
        )
        db.add(model)
        await db.flush()

        # 4. Create Variants
        variants_data = extracted.get("variants") or []
        for v in variants_data:
            v_name = v.get("variant_name") or v.get("name") or f"{model_name} Standard"
            fuel = v.get("fuel_type", "PETROL")
            trans = v.get("transmission", "MANUAL")
            ref_price = Decimal(str(v.get("reference_ex_showroom") or v.get("price") or rec.reference_ex_showroom_min or 1000000))
            v_specs = v.get("specifications") or v.get("specs") or {}

            claimed_range = Decimal(str(v_specs.get("range_claimed"))) if v_specs.get("range_claimed") else None
            tested_range = Decimal(str(v_specs.get("range_tested"))) if v_specs.get("range_tested") else None
            claimed_mileage = Decimal(str(v_specs.get("mileage"))) if v_specs.get("mileage") else None

            variant = VehicleVariant(
                model_id=model.id,
                name=v_name,
                fuel_type=fuel,
                transmission=trans,
                seating_capacity=v.get("seating_capacity", 5),
                engine_cc_or_battery_kwh=v.get("engine_cc_or_battery_kwh") or v.get("engine_or_battery"),
                reference_ex_showroom=ref_price,
                claimed_range_km=claimed_range,
                tested_range_km=tested_range,
                claimed_mileage_kmpl=claimed_mileage,
                source_priority=v_specs.get("source_priority", 1),
                specifications=v_specs,
                last_verified_at=datetime.now(timezone.utc),
                is_active=True
            )
            db.add(variant)
            await db.flush()

            # Attach MoRTH / VAHAN / ARAI standards
            try:
                await IndianGovernmentDataService.attach_regulatory_citations(
                    variant_id=variant.id,
                    category_slug=cat_slug,
                    is_ev=(fuel == "ELECTRIC"),
                    db=db
                )
            except Exception as e:
                print(f"[DiscoveryService] Regulatory citation attach note: {e}")

            # Record initial price history
            db.add(
                VehiclePriceHistory(
                    vehicle_variant_id=variant.id,
                    discovery_record_id=rec.id,
                    price_type="EX_SHOWROOM_REFERENCE",
                    amount=ref_price,
                    currency="INR",
                    source_url=rec.primary_source_url,
                    source_name=rec.primary_source_name,
                    effective_from=datetime.now(timezone.utc),
                    verified_at=datetime.now(timezone.utc)
                )
            )

        # Link discovered images to published model
        if getattr(rec, "images", None):
            for img in rec.images:
                img.vehicle_model_id = model.id

        # 5. Update Discovery Record
        rec.review_status = "APPROVED"
        rec.reviewed_by_user_id = reviewer_user_id
        rec.reviewed_at = datetime.now(timezone.utc)
        rec.published_model_id = model.id
        rec.admin_notes = admin_notes

        # 6. Notify All Subscribed Customers
        for sub in rec.subscriptions:
            if sub.user_id:
                await NotificationService.create_notification(
                    user_id=sub.user_id,
                    title=f"Vehicle Published: {model_name} is Now in Catalogue!",
                    message=f"The vehicle '{brand_name} {model_name}' you requested has been verified and published. You can now start or join a buying group!",
                    event_type="DISCOVERY_PUBLISHED",
                    link_url=f"/vehicles/{model.id}",
                    db=db
                )
            sub.notification_sent = True

        await db.commit()
        await db.refresh(model)
        return model

    @classmethod
    async def reject_record(
        cls,
        record_id: str,
        reviewer_user_id: str,
        admin_notes: Optional[str],
        db: AsyncSession
    ):
        rec_res = await db.execute(
            select(VehicleDiscoveryRecord).where(VehicleDiscoveryRecord.id == record_id)
        )
        rec = rec_res.scalar_one_or_none()
        if not rec:
            raise ValueError("Discovery record not found")

        rec.review_status = "REJECTED"
        rec.reviewed_by_user_id = reviewer_user_id
        rec.reviewed_at = datetime.now(timezone.utc)
        rec.admin_notes = admin_notes
        await db.commit()
        return rec

    @classmethod
    async def run_scheduled_scan(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        Background scheduled scanner: queries enabled sources for new announcements.
        """
        sources = SourceRegistry.list_adapters()
        discovered_count = 0

        for adapter in sources:
            try:
                announcements = await adapter.fetch_announcements()
                for ann in announcements:
                    # Check if already discovered
                    existing = await db.execute(
                        select(VehicleDiscoveryRecord).where(
                            VehicleDiscoveryRecord.discovered_model == ann["model"]
                        )
                    )
                    if existing.scalars().first():
                        continue

                    # Process announcement
                    await cls.create_customer_discovery_request(
                        search_query=ann["model"],
                        customer_name="System Scheduled Scan",
                        customer_email="scanner@gaadilelo.com",
                        customer_phone=None,
                        category_slug=ann.get("category_slug", "car"),
                        target_city_id=None,
                        user_id=None,
                        db=db
                    )
                    discovered_count += 1
            except Exception as e:
                # Log error and continue to next source
                print(f"Error scanning source {adapter.source_name}: {e}")

        return {
            "sources_scanned": len(sources),
            "new_vehicles_discovered": discovered_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

