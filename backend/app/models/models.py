import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's native UUID type (with automatic $::UUID casting),
    and CHAR(36) on SQLite. Transparently serializes and deserializes as str.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=False))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

# 1. CITIES
class City(Base):
    __tablename__ = "cities"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode_prefix = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    dealers = relationship("Dealer", back_populates="city")
    buying_groups = relationship("BuyingGroup", back_populates="city")
    user_profiles = relationship("UserProfile", back_populates="city")


# 2. USERS & PROFILES
class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="BUYER", nullable=False) # BUYER, DEALER, ADMIN
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    dealer = relationship("Dealer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    created_groups = relationship("BuyingGroup", back_populates="creator")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    buyer_leads = relationship("BuyerLead", back_populates="buyer")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    city_id = Column(GUID, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    preferred_language = Column(String(10), default="en")
    communication_consent = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="profile")
    city = relationship("City", back_populates="user_profiles")


# 3. DEALERS & VERIFICATION
class Dealer(Base):
    __tablename__ = "dealers"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    dealership_name = Column(String(255), nullable=False)
    legal_entity_name = Column(String(255), nullable=False)
    gstin = Column(String(15), unique=True, index=True, nullable=False)
    city_id = Column(GUID, ForeignKey("cities.id"), nullable=False)
    address = Column(Text, nullable=False)
    authorized_brands = Column(JSON, default=list) # e.g. ["Tata Motors", "Maruti Suzuki"]
    verification_status = Column(String(20), default="PENDING") # PENDING, VERIFIED, REJECTED
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="dealer")
    city = relationship("City", back_populates="dealers")
    documents = relationship("DealerDocument", back_populates="dealer", cascade="all, delete-orphan")
    invitations = relationship("DealerGroupInvitation", back_populates="dealer", cascade="all, delete-orphan")
    quotations = relationship("Quotation", back_populates="dealer", cascade="all, delete-orphan")
    leads = relationship("BuyerLead", back_populates="dealer")


class DealerDocument(Base):
    __tablename__ = "dealer_documents"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    dealer_id = Column(GUID, ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False) # GST_CERTIFICATE, OEM_AGREEMENT, etc.
    file_url = Column(Text, nullable=False)
    verification_status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=utc_now)

    dealer = relationship("Dealer", back_populates="documents")


# 4. VEHICLE CATALOG
class VehicleCategory(Base):
    __tablename__ = "vehicle_categories"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    brands = relationship("VehicleBrand", back_populates="category")


class VehicleBrand(Base):
    __tablename__ = "vehicle_brands"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    category_id = Column(GUID, ForeignKey("vehicle_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    canonical_name = Column(String(100), nullable=True)
    external_source_id = Column(String(100), nullable=True)
    source_name = Column(String(50), default="meterapp", nullable=True)
    source_license = Column(String(50), default="ISC", nullable=True)
    country = Column(String(50), default="India", nullable=True)
    logo_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    category = relationship("VehicleCategory", back_populates="brands")
    models = relationship("VehicleModel", back_populates="brand", cascade="all, delete-orphan")


class VehicleModel(Base):
    __tablename__ = "vehicle_models"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    brand_id = Column(GUID, ForeignKey("vehicle_brands.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False)
    canonical_brand_name = Column(String(100), nullable=True)
    canonical_model_name = Column(String(150), nullable=True)
    vehicle_category_slug = Column(String(50), nullable=True)
    external_source_id = Column(String(100), nullable=True)
    source_name = Column(String(50), default="meterapp", nullable=True)
    source_license = Column(String(50), default="ISC", nullable=True)
    source_provenance = Column(JSON, default=dict, nullable=True)
    imported_at = Column(DateTime, nullable=True)
    body_type = Column(String(50), nullable=False)
    generation = Column(String(50), nullable=True) # e.g. "Gen 2", "Facelift"
    model_year = Column(Integer, nullable=True)
    wikidata_id = Column(String(50), nullable=True) # e.g. "Q44954468"
    length_mm = Column(Integer, nullable=True)
    width_mm = Column(Integer, nullable=True)
    height_mm = Column(Integer, nullable=True)
    wheelbase_mm = Column(Integer, nullable=True)
    ground_clearance_mm = Column(Integer, nullable=True)
    safety_rating_stars = Column(Integer, nullable=True) # 0-5
    safety_rating_agency = Column(String(50), nullable=True) # BHARAT_NCAP, GLOBAL_NCAP
    image_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    brand = relationship("VehicleBrand", back_populates="models")
    variants = relationship("VehicleVariant", back_populates="model", cascade="all, delete-orphan")
    images = relationship("VehicleImage", back_populates="model", cascade="all, delete-orphan")


class VehicleVariant(Base):
    __tablename__ = "vehicle_variants"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    model_id = Column(GUID, ForeignKey("vehicle_models.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    fuel_type = Column(String(30), nullable=False) # PETROL, DIESEL, CNG, ELECTRIC, HYBRID
    transmission = Column(String(30), nullable=False) # MANUAL, AUTOMATIC, AMT, CVT, DCT, SINGLE_SPEED_EV
    seating_capacity = Column(Integer, default=5)
    engine_cc_or_battery_kwh = Column(String(50), nullable=True)
    engine_displacement_cc = Column(Integer, nullable=True)
    battery_capacity_kwh = Column(Numeric(5, 1), nullable=True)
    claimed_range_km = Column(Numeric(6, 1), nullable=True) # ARAI / MIDC / IDC claimed
    tested_range_km = Column(Numeric(6, 1), nullable=True) # Independently tested / TrueRange
    real_world_range_km = Column(Numeric(6, 1), nullable=True)
    claimed_mileage_kmpl = Column(Numeric(5, 2), nullable=True)
    reference_ex_showroom = Column(Numeric(12, 2), nullable=False)
    source_priority = Column(Integer, default=1) # 1: OEM Spec, 2: Brochure, 3: Gov Open Data, 4: Wikidata/Open
    data_source_id = Column(GUID, ForeignKey("vehicle_data_sources.id", ondelete="SET NULL"), nullable=True)
    source_url = Column(Text, nullable=True)
    source_document = Column(String(200), nullable=True)
    confidence_score = Column(Numeric(3, 2), default=1.0, nullable=True)
    review_status = Column(String(30), default="VERIFIED", nullable=True) # VERIFIED, PENDING_REVIEW, ADMIN_REVIEW
    specifications = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    last_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    model = relationship("VehicleModel", back_populates="variants")
    buying_groups = relationship("BuyingGroup", back_populates="variant")
    data_source = relationship("VehicleDataSource")


# 5. BUYING GROUPS & MEMBERS
class BuyingGroup(Base):
    __tablename__ = "buying_groups"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    group_code = Column(String(30), unique=True, index=True, nullable=False)
    vehicle_variant_id = Column(GUID, ForeignKey("vehicle_variants.id"), nullable=False)
    city_id = Column(GUID, ForeignKey("cities.id"), nullable=False)
    created_by_user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="OPEN", nullable=False) # DRAFT, OPEN, QUALIFYING, READY_FOR_BIDDING, BIDDING_OPEN, OFFERS_AVAILABLE, COMPLETED, CANCELLED
    target_members = Column(Integer, default=5, nullable=False)
    current_members_count = Column(Integer, default=1, nullable=False)
    target_purchase_timeline = Column(String(50), nullable=False) # WITHIN_15_DAYS, WITHIN_30_DAYS, WITHIN_60_DAYS
    bidding_start_time = Column(DateTime, nullable=True)
    bidding_end_time = Column(DateTime, nullable=True)
    additional_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    variant = relationship("VehicleVariant", back_populates="buying_groups")
    city = relationship("City", back_populates="buying_groups")
    creator = relationship("User", back_populates="created_groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    invitations = relationship("DealerGroupInvitation", back_populates="group", cascade="all, delete-orphan")
    quotations = relationship("Quotation", back_populates="group", cascade="all, delete-orphan")
    leads = relationship("BuyerLead", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    group_id = Column(GUID, ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    buyer_notes = Column(Text, nullable=True)
    status = Column(String(30), default="ACTIVE") # ACTIVE, QUALIFIED, WITHDRAWN, PURCHASED
    intent_confirmed = Column(Boolean, default=True)
    intent_confirmed_at = Column(DateTime, default=utc_now)
    joined_at = Column(DateTime, default=utc_now)

    group = relationship("BuyingGroup", back_populates="members")
    user = relationship("User", back_populates="group_memberships")


class BuyerIntentConfirmation(Base):
    __tablename__ = "buyer_intent_confirmations"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    group_id = Column(GUID, ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    purchase_timeline = Column(String(50), nullable=False) # IMMEDIATELY, WITHIN_15_DAYS, WITHIN_30_DAYS, WITHIN_60_DAYS, FLEXIBLE
    is_genuine_intent = Column(Boolean, default=True, nullable=False)
    is_non_binding_acknowledged = Column(Boolean, default=True, nullable=False)
    agreed_to_contact = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    confirmed_at = Column(DateTime, default=utc_now)

    group = relationship("BuyingGroup")
    user = relationship("User")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_type = Column(String(50), nullable=False) # PASSWORD_RESET, EMAIL_VERIFICATION
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    jti = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    revoked_at = Column(DateTime, default=utc_now, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User")


# 6. INVITATIONS & QUOTATIONS
class DealerGroupInvitation(Base):
    __tablename__ = "dealer_group_invitations"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    group_id = Column(GUID, ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    dealer_id = Column(GUID, ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="INVITED") # INVITED, ACCEPTED, DECLINED, SUBMITTED
    invited_at = Column(DateTime, default=utc_now)

    group = relationship("BuyingGroup", back_populates="invitations")
    dealer = relationship("Dealer", back_populates="invitations")


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    group_id = Column(GUID, ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    dealer_id = Column(GUID, ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
    revision_number = Column(Integer, default=1)
    status = Column(String(30), default="SUBMITTED") # DRAFT, SUBMITTED, APPROVED, REJECTED, SUPERSEDED
    admin_review_notes = Column(Text, nullable=True)
    
    # Vehicle-Agnostic Pricing Engine Components
    base_ex_showroom = Column(Numeric(12, 2), nullable=False)
    rto_road_tax = Column(Numeric(12, 2), default=0)
    insurance_amount = Column(Numeric(12, 2), default=0)
    tcs_amount = Column(Numeric(12, 2), default=0)
    mfg_discount = Column(Numeric(12, 2), default=0)
    dealer_discount = Column(Numeric(12, 2), default=0)
    exchange_bonus = Column(Numeric(12, 2), default=0)
    corporate_discount = Column(Numeric(12, 2), default=0)
    accessories_amount = Column(Numeric(12, 2), default=0)
    logistics_handling = Column(Numeric(12, 2), default=0)
    other_statutory_charges = Column(Numeric(12, 2), default=0)
    final_on_road_price = Column(Numeric(12, 2), nullable=False)
    
    delivery_timeline_days = Column(Integer, nullable=False)
    offer_valid_until = Column(DateTime, nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    group = relationship("BuyingGroup", back_populates="quotations")
    dealer = relationship("Dealer", back_populates="quotations")
    revisions = relationship("QuotationRevision", back_populates="quotation", cascade="all, delete-orphan")
    line_items = relationship("QuotationLineItem", back_populates="quotation", cascade="all, delete-orphan")
    leads = relationship("BuyerLead", back_populates="quotation")


class QuotationRevision(Base):
    __tablename__ = "quotation_revisions"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    quotation_id = Column(GUID, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    snapshot = Column(JSON, nullable=False)
    revised_at = Column(DateTime, default=utc_now)
    revised_by_user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    quotation = relationship("Quotation", back_populates="revisions")


class QuotationLineItem(Base):
    __tablename__ = "quotation_line_items"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    quotation_id = Column(GUID, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String(150), nullable=False)
    item_type = Column(String(30), nullable=False) # MANDATORY, OPTIONAL, COMPLIMENTARY, DISCOUNT
    amount = Column(Numeric(12, 2), nullable=False)

    quotation = relationship("Quotation", back_populates="line_items")


# 7. BUYER LEADS, NOTIFICATIONS, AUDIT
class BuyerLead(Base):
    __tablename__ = "buyer_leads"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    group_id = Column(GUID, ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    buyer_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dealer_id = Column(GUID, ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
    quotation_id = Column(GUID, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="PENDING_CALLBACK") # PENDING_CALLBACK, CONTACTED, TEST_DRIVE_SCHEDULED, BOOKING_IN_PROGRESS, PURCHASE_COMPLETED, LOST
    buyer_consent_given = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    group = relationship("BuyingGroup", back_populates="leads")
    buyer = relationship("User", back_populates="buyer_leads")
    dealer = relationship("Dealer", back_populates="leads")
    quotation = relationship("Quotation", back_populates="leads")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    event_type = Column(String(100), nullable=False)
    link_url = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="notifications")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    submitted_by_user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_dealer_id = Column(GUID, ForeignKey("dealers.id", ondelete="SET NULL"), nullable=True)
    group_id = Column(GUID, ForeignKey("buying_groups.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(30), default="OPEN") # OPEN, INVESTIGATING, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    actor_user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(GUID, nullable=False)
    payload = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=utc_now)


# ====================================================================
# 8. VEHICLE INTELLIGENCE & AUTOMATED DISCOVERY MODELS
# ====================================================================

class VehicleDataSource(Base):
    __tablename__ = "vehicle_data_sources"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    source_name = Column(String(150), nullable=False)
    source_url = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False) # MANUFACTURER_WEBSITE, PRESS_RELEASE, LICENSED_API, PUBLIC_PORTAL
    access_method = Column(String(50), default="RSS_FEED") # RSS_FEED, REST_API, SITEMAP, MANUAL
    licensing_status = Column(String(50), default="OFFICIAL_PUBLIC") # OFFICIAL_PUBLIC, LICENSED, PERMITTED_RSS, INTERNAL
    enabled = Column(Boolean, default=True)
    update_frequency = Column(String(50), default="DAILY") # DAILY, WEEKLY, MANUAL
    last_synced_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    jobs = relationship("VehicleDiscoveryJob", back_populates="data_source")


class VehicleDiscoveryJob(Base):
    __tablename__ = "vehicle_discovery_jobs"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    search_query = Column(String(255), nullable=False)
    requested_by_user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    source_id = Column(GUID, ForeignKey("vehicle_data_sources.id", ondelete="SET NULL"), nullable=True)
    job_type = Column(String(50), default="CUSTOMER_REQUEST") # CUSTOMER_REQUEST, SCHEDULED_SCAN, ADMIN_MANUAL
    status = Column(String(50), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    data_source = relationship("VehicleDataSource", back_populates="jobs")
    requester = relationship("User")
    records = relationship("VehicleDiscoveryRecord", back_populates="job", cascade="all, delete-orphan")


class VehicleDiscoveryRecord(Base):
    __tablename__ = "vehicle_discovery_records"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    job_id = Column(GUID, ForeignKey("vehicle_discovery_jobs.id", ondelete="SET NULL"), nullable=True)
    discovered_brand = Column(String(100), nullable=False)
    discovered_model = Column(String(150), nullable=False)
    category_slug = Column(String(50), default="car")
    body_type = Column(String(50), default="SUV")
    launch_status = Column(String(50), default="LAUNCHED") # ANNOUNCED, LAUNCHED, UPCOMING, FACELIFT
    model_year = Column(Integer, nullable=True)
    reference_ex_showroom_min = Column(Numeric(12, 2), nullable=True)
    reference_ex_showroom_max = Column(Numeric(12, 2), nullable=True)
    extracted_data = Column(JSON, default=dict)
    confidence_score = Column(Numeric(5, 2), default=0.95)
    review_status = Column(String(50), default="PENDING_REVIEW") # PENDING_REVIEW, APPROVED, REJECTED, REPROCESSING
    admin_notes = Column(Text, nullable=True)
    reviewed_by_user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    published_model_id = Column(GUID, ForeignKey("vehicle_models.id", ondelete="SET NULL"), nullable=True)
    primary_source_url = Column(Text, nullable=True)
    primary_source_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    job = relationship("VehicleDiscoveryJob", back_populates="records")
    reviewer = relationship("User", foreign_keys=[reviewed_by_user_id])
    published_model = relationship("VehicleModel")
    spec_sources = relationship("VehicleSpecificationSource", back_populates="discovery_record", cascade="all, delete-orphan")
    price_histories = relationship("VehiclePriceHistory", back_populates="discovery_record", cascade="all, delete-orphan")
    images = relationship("VehicleImage", back_populates="discovery_record", cascade="all, delete-orphan")
    subscriptions = relationship("VehicleDiscoverySubscription", back_populates="discovery_record", cascade="all, delete-orphan")


class VehicleSpecificationSource(Base):
    __tablename__ = "vehicle_specification_sources"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    vehicle_variant_id = Column(GUID, ForeignKey("vehicle_variants.id", ondelete="CASCADE"), nullable=True)
    discovery_record_id = Column(GUID, ForeignKey("vehicle_discovery_records.id", ondelete="CASCADE"), nullable=True)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=False)
    unit = Column(String(30), nullable=True)
    source_url = Column(Text, nullable=False)
    source_name = Column(String(150), nullable=False)
    source_priority = Column(Integer, default=1) # 1: OEM Spec, 2: Brochure, 3: Gov Open Data, 4: Wikidata/Open
    license_name = Column(String(100), nullable=True) # e.g. CC BY 4.0, GODL-India, Public Domain
    license_url = Column(Text, nullable=True)
    confidence_score = Column(Numeric(5, 2), default=1.0)
    is_conflict = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    variant = relationship("VehicleVariant")
    discovery_record = relationship("VehicleDiscoveryRecord", back_populates="spec_sources")


class VehiclePriceHistory(Base):
    __tablename__ = "vehicle_price_history"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    vehicle_variant_id = Column(GUID, ForeignKey("vehicle_variants.id", ondelete="CASCADE"), nullable=True)
    discovery_record_id = Column(GUID, ForeignKey("vehicle_discovery_records.id", ondelete="CASCADE"), nullable=True)
    city_id = Column(GUID, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    price_type = Column(String(50), default="EX_SHOWROOM_REFERENCE") # EX_SHOWROOM_REFERENCE, INDICATIVE_ON_ROAD
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="INR")
    source_url = Column(Text, nullable=True)
    source_name = Column(String(150), nullable=True)
    effective_from = Column(DateTime, default=utc_now)
    effective_until = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    variant = relationship("VehicleVariant")
    discovery_record = relationship("VehicleDiscoveryRecord", back_populates="price_histories")
    city = relationship("City")


class VehicleImage(Base):
    __tablename__ = "vehicle_images"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    vehicle_model_id = Column(GUID, ForeignKey("vehicle_models.id", ondelete="CASCADE"), nullable=True)
    discovery_record_id = Column(GUID, ForeignKey("vehicle_discovery_records.id", ondelete="CASCADE"), nullable=True)
    image_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    source_page_url = Column(Text, nullable=True)
    author_name = Column(String(200), nullable=True)
    license_name = Column(String(100), nullable=True) # Public domain, CC BY-SA 4.0, CC0, etc.
    license_url = Column(Text, nullable=True)
    attribution_html = Column(Text, nullable=True)
    usage_rights_status = Column(String(50), default="PUBLIC_COMMONS") # OFFICIAL_OEM_PRESS, PUBLIC_COMMONS, LICENSED
    verification_status = Column(String(50), default="VERIFIED") # VERIFIED, REJECTED, PENDING_REVIEW
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    image_type = Column(String(50), default="EXTERIOR_FRONT") # EXTERIOR_FRONT, EXTERIOR_SIDE, INTERIOR, COLOR_VARIANT
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    model = relationship("VehicleModel", back_populates="images")
    discovery_record = relationship("VehicleDiscoveryRecord", back_populates="images")


class VehicleDatasetSync(Base):
    __tablename__ = "vehicle_dataset_syncs"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    dataset_name = Column(String(100), nullable=False) # VEHICLES_DB, WIKIDATA, DATA_GOV_IN, WIKIMEDIA
    records_processed = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    status = Column(String(50), default="COMPLETED")
    error_message = Column(Text, nullable=True)
    sync_metadata = Column(JSON, default=dict)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)


class VehicleUpdateHistory(Base):
    __tablename__ = "vehicle_update_history"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    vehicle_model_id = Column(GUID, ForeignKey("vehicle_models.id", ondelete="CASCADE"), nullable=True)
    vehicle_variant_id = Column(GUID, ForeignKey("vehicle_variants.id", ondelete="CASCADE"), nullable=True)
    change_type = Column(String(50), nullable=False) # PRICE_REVISION, NEW_VARIANT, SPECIFICATION_UPDATE, FACELIFT
    previous_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    source_url = Column(Text, nullable=True)
    source_name = Column(String(150), nullable=True)
    changed_at = Column(DateTime, default=utc_now)

    model = relationship("VehicleModel")
    variant = relationship("VehicleVariant")


class VehicleDiscoverySubscription(Base):
    __tablename__ = "vehicle_discovery_subscriptions"

    id = Column(GUID, primary_key=True, default=generate_uuid)
    discovery_record_id = Column(GUID, ForeignKey("vehicle_discovery_records.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    customer_name = Column(String(150), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    target_city_id = Column(GUID, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    discovery_record = relationship("VehicleDiscoveryRecord", back_populates="subscriptions")
    user = relationship("User")
    city = relationship("City")


