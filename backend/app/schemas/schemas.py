from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# -----------------
# 1. AUTH & USERS
# -----------------
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    phone: str = Field(min_length=10, max_length=15)
    full_name: str
    role: str = Field(default="BUYER", pattern="^(BUYER|DEALER|ADMIN)$")
    city_id: Optional[str] = None
    
    # Dealer-specific optional fields if role == DEALER
    dealership_name: Optional[str] = None
    legal_entity_name: Optional[str] = None
    gstin: Optional[str] = None
    address: Optional[str] = None
    authorized_brands: Optional[List[str]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    city_id: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    communication_consent: Optional[bool] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    profile: Optional[Dict[str, Any]] = None
    dealer: Optional[Dict[str, Any]] = None

# -----------------
# 2. DEALER & VERIFICATION
# -----------------
class DealerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    dealership_name: str
    legal_entity_name: str
    gstin: str
    city_id: str
    address: str
    authorized_brands: List[str]
    verification_status: str
    verification_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    user_email: Optional[str] = None
    city_name: Optional[str] = None

class DealerVerificationUpdate(BaseModel):
    verification_status: str = Field(pattern="^(VERIFIED|REJECTED|PENDING)$")
    verification_notes: Optional[str] = None

class DealerDashboardStats(BaseModel):
    invitations_count: int
    active_bidding_count: int
    quotations_submitted_count: int
    leads_count: int
    conversions_count: int

# -----------------
# 3. CATALOG & GEOGRAPHY
# -----------------
class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    state: str
    pincode_prefix: Optional[str] = None
    is_active: bool

class VehicleVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    model_id: str
    name: str
    fuel_type: str
    transmission: str
    seating_capacity: Optional[int] = 5
    engine_cc_or_battery_kwh: Optional[str] = None
    reference_ex_showroom: Decimal
    specifications: Optional[Dict[str, Any]] = {}
    is_active: bool

class VehicleModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    brand_id: str
    name: str
    slug: str
    body_type: str
    image_url: Optional[str] = None
    is_active: bool
    brand_name: Optional[str] = None
    category_slug: Optional[str] = None
    variants: Optional[List[VehicleVariantResponse]] = []
    active_groups_count: Optional[int] = 0

class VehicleBrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    category_id: str
    name: str
    slug: str
    logo_url: Optional[str] = None

class VehicleCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    slug: str
    name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None
    display_order: int

# -----------------
# 4. BUYING GROUPS
# -----------------
class BuyingGroupCreate(BaseModel):
    vehicle_variant_id: str
    city_id: str
    target_members: int = Field(default=5, ge=2, le=50)
    target_purchase_timeline: str = Field(pattern="^(WITHIN_15_DAYS|WITHIN_30_DAYS|WITHIN_60_DAYS)$")
    additional_notes: Optional[str] = None

class BuyingGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    group_code: str
    vehicle_variant_id: str
    city_id: str
    created_by_user_id: str
    status: str
    target_members: int
    current_members_count: int
    target_purchase_timeline: str
    bidding_start_time: Optional[datetime] = None
    bidding_end_time: Optional[datetime] = None
    additional_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Nested hydrated details for rich UI
    vehicle_name: Optional[str] = None
    brand_name: Optional[str] = None
    variant_name: Optional[str] = None
    vehicle_image_url: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    reference_ex_showroom: Optional[Decimal] = None
    city_name: Optional[str] = None
    is_current_user_member: Optional[bool] = False
    approved_quotations_count: Optional[int] = 0

class BuyingGroupStatusUpdate(BaseModel):
    status: str = Field(pattern="^(DRAFT|OPEN|QUALIFYING|READY_FOR_BIDDING|BIDDING_OPEN|OFFERS_AVAILABLE|COMPLETED|CANCELLED)$")
    bidding_end_time: Optional[datetime] = None

class InviteDealersRequest(BaseModel):
    dealer_ids: List[str]

# -----------------
# 5. PRICING & QUOTATIONS
# -----------------
class QuotationLineItemSchema(BaseModel):
    item_name: str
    item_type: str = Field(pattern="^(MANDATORY|OPTIONAL|COMPLIMENTARY|DISCOUNT)$")
    amount: Decimal

class PricingCalculationRequest(BaseModel):
    base_ex_showroom: Decimal
    rto_road_tax: Decimal = Decimal(0)
    insurance_amount: Decimal = Decimal(0)
    tcs_amount: Decimal = Decimal(0)
    mfg_discount: Decimal = Decimal(0)
    dealer_discount: Decimal = Decimal(0)
    exchange_bonus: Decimal = Decimal(0)
    corporate_discount: Decimal = Decimal(0)
    accessories_amount: Decimal = Decimal(0)
    logistics_handling: Decimal = Decimal(0)
    other_statutory_charges: Decimal = Decimal(0)

class PricingCalculationResponse(BaseModel):
    gross_price: Decimal
    total_discounts: Decimal
    calculated_on_road_price: Decimal
    tcs_applicable: bool
    calculated_tcs: Decimal
    breakdown_summary: Dict[str, Decimal]

class QuotationCreate(BaseModel):
    group_id: str
    base_ex_showroom: Decimal
    rto_road_tax: Decimal = Decimal(0)
    insurance_amount: Decimal = Decimal(0)
    tcs_amount: Decimal = Decimal(0)
    mfg_discount: Decimal = Decimal(0)
    dealer_discount: Decimal = Decimal(0)
    exchange_bonus: Decimal = Decimal(0)
    corporate_discount: Decimal = Decimal(0)
    accessories_amount: Decimal = Decimal(0)
    logistics_handling: Decimal = Decimal(0)
    other_statutory_charges: Decimal = Decimal(0)
    delivery_timeline_days: int = Field(ge=1, le=180)
    offer_valid_until: datetime
    remarks: Optional[str] = None
    line_items: Optional[List[QuotationLineItemSchema]] = []

class QuotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    group_id: str
    dealer_id: str
    revision_number: int
    status: str
    admin_review_notes: Optional[str] = None
    base_ex_showroom: Decimal
    rto_road_tax: Decimal
    insurance_amount: Decimal
    tcs_amount: Decimal
    mfg_discount: Decimal
    dealer_discount: Decimal
    exchange_bonus: Decimal
    corporate_discount: Decimal
    accessories_amount: Decimal
    logistics_handling: Decimal
    other_statutory_charges: Decimal
    final_on_road_price: Decimal
    delivery_timeline_days: int
    offer_valid_until: datetime
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    dealership_name: Optional[str] = None
    dealer_city: Optional[str] = None
    revisions_count: Optional[int] = 1

# -----------------
# 6. LEADS & CALLBACKS
# -----------------
class BuyerLeadRequest(BaseModel):
    group_id: str
    quotation_id: str
    notes: Optional[str] = None

class BuyerLeadStatusUpdate(BaseModel):
    status: str = Field(pattern="^(PENDING_CALLBACK|CONTACTED|TEST_DRIVE_SCHEDULED|BOOKING_IN_PROGRESS|PURCHASE_COMPLETED|LOST)$")
    notes: Optional[str] = None

class BuyerLeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    group_id: str
    buyer_id: str
    dealer_id: str
    quotation_id: str
    status: str
    buyer_consent_given: bool
    notes: Optional[str] = None
    created_at: datetime
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_email: Optional[str] = None
    dealership_name: Optional[str] = None
    vehicle_name: Optional[str] = None
    quoted_price: Optional[Decimal] = None

# -----------------
# 7. ADMIN, NOTIFICATIONS, AUDIT
# -----------------
class AdminOverviewStats(BaseModel):
    total_buyers: int
    verified_dealerships: int
    pending_dealerships: int
    active_groups: int
    bidding_open_groups: int
    quotations_submitted: int
    approved_quotations: int
    total_leads: int
    successful_conversions: int

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    message: str
    event_type: str
    link_url: Optional[str] = None
    is_read: bool
    created_at: datetime

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    actor_user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    payload: Dict[str, Any]
    created_at: datetime

