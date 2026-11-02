import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

# 1. CITIES
class City(Base):
    __tablename__ = "cities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
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

    id = Column(String(36), primary_key=True, default=generate_uuid)
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

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    city_id = Column(String(36), ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    preferred_language = Column(String(10), default="en")
    communication_consent = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="profile")
    city = relationship("City", back_populates="user_profiles")


# 3. DEALERS & VERIFICATION
class Dealer(Base):
    __tablename__ = "dealers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    dealership_name = Column(String(255), nullable=False)
    legal_entity_name = Column(String(255), nullable=False)
    gstin = Column(String(15), unique=True, index=True, nullable=False)
    city_id = Column(String(36), ForeignKey("cities.id"), nullable=False)
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

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dealer_id = Column(String(36), ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False) # GST_CERTIFICATE, OEM_AGREEMENT, etc.
    file_url = Column(Text, nullable=False)
    verification_status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, default=utc_now)

    dealer = relationship("Dealer", back_populates="documents")


# 4. VEHICLE CATALOG
class VehicleCategory(Base):
    __tablename__ = "vehicle_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    brands = relationship("VehicleBrand", back_populates="category")


class VehicleBrand(Base):
    __tablename__ = "vehicle_brands"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("vehicle_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    logo_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    category = relationship("VehicleCategory", back_populates="brands")
    models = relationship("VehicleModel", back_populates="brand", cascade="all, delete-orphan")


class VehicleModel(Base):
    __tablename__ = "vehicle_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand_id = Column(String(36), ForeignKey("vehicle_brands.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False)
    body_type = Column(String(50), nullable=False)
    image_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    brand = relationship("VehicleBrand", back_populates="models")
    variants = relationship("VehicleVariant", back_populates="model", cascade="all, delete-orphan")


class VehicleVariant(Base):
    __tablename__ = "vehicle_variants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_id = Column(String(36), ForeignKey("vehicle_models.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    fuel_type = Column(String(30), nullable=False) # PETROL, DIESEL, CNG, ELECTRIC, HYBRID
    transmission = Column(String(30), nullable=False) # MANUAL, AUTOMATIC, AMT, CVT, DCT, SINGLE_SPEED_EV
    seating_capacity = Column(Integer, default=5)
    engine_cc_or_battery_kwh = Column(String(50), nullable=True)
    reference_ex_showroom = Column(Numeric(12, 2), nullable=False)
    specifications = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    model = relationship("VehicleModel", back_populates="variants")
    buying_groups = relationship("BuyingGroup", back_populates="variant")


# 5. BUYING GROUPS & MEMBERS
class BuyingGroup(Base):
    __tablename__ = "buying_groups"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_code = Column(String(30), unique=True, index=True, nullable=False)
    vehicle_variant_id = Column(String(36), ForeignKey("vehicle_variants.id"), nullable=False)
    city_id = Column(String(36), ForeignKey("cities.id"), nullable=False)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
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

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    buyer_notes = Column(Text, nullable=True)
    status = Column(String(30), default="ACTIVE") # ACTIVE, QUALIFIED, WITHDRAWN, PURCHASED
    joined_at = Column(DateTime, default=utc_now)

    group = relationship("BuyingGroup", back_populates="members")
    user = relationship("User", back_populates="group_memberships")


# 6. INVITATIONS & QUOTATIONS
class DealerGroupInvitation(Base):
    __tablename__ = "dealer_group_invitations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    dealer_id = Column(String(36), ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="INVITED") # INVITED, ACCEPTED, DECLINED, SUBMITTED
    invited_at = Column(DateTime, default=utc_now)

    group = relationship("BuyingGroup", back_populates="invitations")
    dealer = relationship("Dealer", back_populates="invitations")


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    dealer_id = Column(String(36), ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
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

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    snapshot = Column(JSON, nullable=False)
    revised_at = Column(DateTime, default=utc_now)
    revised_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    quotation = relationship("Quotation", back_populates="revisions")


class QuotationLineItem(Base):
    __tablename__ = "quotation_line_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(String(150), nullable=False)
    item_type = Column(String(30), nullable=False) # MANDATORY, OPTIONAL, COMPLIMENTARY, DISCOUNT
    amount = Column(Numeric(12, 2), nullable=False)

    quotation = relationship("Quotation", back_populates="line_items")


# 7. BUYER LEADS, NOTIFICATIONS, AUDIT
class BuyerLead(Base):
    __tablename__ = "buyer_leads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("buying_groups.id", ondelete="CASCADE"), nullable=False)
    buyer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dealer_id = Column(String(36), ForeignKey("dealers.id", ondelete="CASCADE"), nullable=False)
    quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
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

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    event_type = Column(String(100), nullable=False)
    link_url = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="notifications")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submitted_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_dealer_id = Column(String(36), ForeignKey("dealers.id", ondelete="SET NULL"), nullable=True)
    group_id = Column(String(36), ForeignKey("buying_groups.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(30), default="OPEN") # OPEN, INVESTIGATING, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False)
    payload = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=utc_now)
