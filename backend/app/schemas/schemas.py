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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)

class VerifyEmailRequest(BaseModel):
    token: str

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
class BuyerIntentPayload(BaseModel):
    purchase_timeline: str = Field(default="WITHIN_30_DAYS")
    is_genuine_intent: bool = Field(default=True)
    is_non_binding_acknowledged: bool = Field(default=True)
    agreed_to_contact: bool = Field(default=True)

class JoinGroupRequest(BaseModel):
    notes: Optional[str] = None
    buyer_intent: Optional[BuyerIntentPayload] = None

class BuyingGroupCreate(BaseModel):
    vehicle_variant_id: Optional[str] = None
    city_id: str
    target_members: int = Field(default=5, ge=2, le=50)
    target_purchase_timeline: str = Field(pattern="^(WITHIN_15_DAYS|WITHIN_30_DAYS|WITHIN_60_DAYS)$")
    additional_notes: Optional[str] = None

    # Buyer Intent Affirmation (Requirement 6)
    buyer_intent: Optional[BuyerIntentPayload] = None

    # Custom Vehicle parameters for automated internet discovery
    custom_brand_name: Optional[str] = None
    custom_model_name: Optional[str] = None
    custom_variant_name: Optional[str] = None
    custom_fuel_type: Optional[str] = None
    custom_body_type: Optional[str] = None
    category_id: Optional[str] = None
    estimated_price: Optional[float] = None

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


# -----------------
# 8. VEHICLE INTELLIGENCE & DISCOVERY ENGINE
# -----------------

class VehicleFieldCitation(BaseModel):
    value: Any
    unit: Optional[str] = None
    source_url: str
    source_name: str
    confidence: float = 1.0
    is_verified: bool = False

class ExtractedVariantSchema(BaseModel):
    variant_name: str
    fuel_type: str
    transmission: str
    reference_ex_showroom: Decimal
    seating_capacity: Optional[int] = 5
    engine_cc_or_battery_kwh: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = {}

class ExtractedVehicleData(BaseModel):
    brand_name: str
    model_name: str
    category_slug: str = "car"
    body_type: str = "SUV"
    model_year: Optional[int] = 2026
    launch_status: str = "LAUNCHED" # ANNOUNCED, LAUNCHED, UPCOMING, FACELIFT
    reference_ex_showroom_min: Decimal
    reference_ex_showroom_max: Decimal
    variants: List[ExtractedVariantSchema]
    image_urls: List[str] = []
    source_url: str
    source_name: str
    confidence_score: float = 0.95
    conflicts: Optional[List[str]] = []

class CustomerDiscoveryRequest(BaseModel):
    search_query: str = Field(min_length=2, max_length=200)
    category_slug: Optional[str] = "car"
    customer_name: str = Field(min_length=2)
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    target_city_id: Optional[str] = None

class VehicleDiscoveryJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    search_query: str
    job_type: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    records_count: Optional[int] = 0

class VehicleDiscoveryRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_id: Optional[str] = None
    discovered_brand: str
    discovered_model: str
    category_slug: str
    body_type: str
    launch_status: str
    model_year: Optional[int] = None
    reference_ex_showroom_min: Optional[Decimal] = None
    reference_ex_showroom_max: Optional[Decimal] = None
    confidence_score: Decimal
    review_status: str
    primary_source_url: Optional[str] = None
    primary_source_name: Optional[str] = None
    published_model_id: Optional[str] = None
    created_at: datetime

class VehicleDiscoveryRecordDetail(VehicleDiscoveryRecordResponse):
    extracted_data: Dict[str, Any]
    admin_notes: Optional[str] = None
    subscribers_count: Optional[int] = 0
    spec_sources: Optional[List[Dict[str, Any]]] = []
    price_histories: Optional[List[Dict[str, Any]]] = []
    images: Optional[List[Dict[str, Any]]] = []

class VehicleDiscoveryApprovalRequest(BaseModel):
    admin_notes: Optional[str] = None
    brand_id: Optional[str] = None # existing or auto-create if empty
    modified_brand: Optional[str] = None
    modified_model: Optional[str] = None
    modified_body_type: Optional[str] = None
    category_slug: Optional[str] = None
    approved_variants: Optional[List[Dict[str, Any]]] = None

class VehicleDataSourceCreate(BaseModel):
    source_name: str
    source_url: str
    source_type: str # MANUFACTURER_WEBSITE, PRESS_RELEASE, LICENSED_API, PUBLIC_PORTAL
    access_method: str = "RSS_FEED" # RSS_FEED, REST_API, SITEMAP, MANUAL
    licensing_status: str = "OFFICIAL_PUBLIC"
    enabled: bool = True
    update_frequency: str = "DAILY"

class VehicleDataSourceUpdate(BaseModel):
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    access_method: Optional[str] = None
    licensing_status: Optional[str] = None
    enabled: Optional[bool] = None
    update_frequency: Optional[str] = None

class VehicleDataSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    source_name: str
    source_url: str
    source_type: str
    access_method: str
    licensing_status: str
    enabled: bool
    update_frequency: str
    last_synced_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime

class VehicleIntelligenceOverviewStats(BaseModel):
    total_discovered_vehicles: int
    pending_review_count: int
    approved_count: int
    rejected_count: int
    active_sources_count: int
    failed_jobs_count: int
    total_customer_discovery_requests: int

class VehiclePriceHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vehicle_variant_id: Optional[str] = None
    city_name: Optional[str] = None
    price_type: str
    amount: Decimal
    currency: str
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    effective_from: datetime
    created_at: datetime

class VehicleUpdateHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vehicle_model_id: Optional[str] = None
    model_name: Optional[str] = None
    change_type: str
    previous_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    changed_at: datetime


