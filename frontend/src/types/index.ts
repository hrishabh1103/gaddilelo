export type UserRole = 'BUYER' | 'DEALER' | 'ADMIN';

export interface User {
  id: string;
  email: string;
  phone: string;
  role: UserRole;
  full_name: string;
  is_verified: boolean;
  city_id?: string;
  dealer?: {
    id: string;
    dealership_name: string;
    verification_status: 'PENDING' | 'VERIFIED' | 'REJECTED';
  };
}

export interface City {
  id: string;
  name: string;
  state: string;
  pincode_prefix?: string;
  is_active: boolean;
}

export interface VehicleCategory {
  id: string;
  slug: string;
  name: string;
  description?: string;
  icon_name?: string;
  display_order: number;
}

export interface VehicleBrand {
  id: string;
  category_id: string;
  name: string;
  slug: string;
  logo_url?: string;
}

export interface VehicleVariant {
  id: string;
  model_id: string;
  name: string;
  fuel_type: string;
  transmission: string;
  seating_capacity?: number;
  engine_cc_or_battery_kwh?: string;
  reference_ex_showroom: number;
  specifications?: Record<string, any>;
  is_active: boolean;
}

export interface VehicleModel {
  id: string;
  brand_id: string;
  brand_name: string;
  category_slug: string;
  name: string;
  slug: string;
  body_type: string;
  image_url?: string;
  is_active: boolean;
  min_price: number;
  max_price: number;
  variants_count: number;
  active_groups_count: number;
  variants: VehicleVariant[];
}

export type GroupStatus = 
  | 'DRAFT' 
  | 'OPEN' 
  | 'QUALIFYING' 
  | 'READY_FOR_BIDDING' 
  | 'BIDDING_OPEN' 
  | 'OFFERS_AVAILABLE' 
  | 'COMPLETED' 
  | 'CANCELLED';

export interface BuyingGroup {
  id: string;
  group_code: string;
  vehicle_variant_id: string;
  city_id: string;
  city_name: string;
  created_by_user_id: string;
  status: GroupStatus;
  target_members: number;
  current_members_count: number;
  target_purchase_timeline: string;
  bidding_start_time?: string;
  bidding_end_time?: string;
  additional_notes?: string;
  created_at: string;
  updated_at: string;
  vehicle_name?: string;
  brand_name?: string;
  variant_name?: string;
  vehicle_image_url?: string;
  fuel_type?: string;
  transmission?: string;
  reference_ex_showroom?: number;
  is_current_user_member?: boolean;
  approved_quotations_count?: number;
}

export interface Quotation {
  id: string;
  group_id: string;
  dealer_id: string;
  dealership_name: string;
  dealer_city?: string;
  revision_number: number;
  status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED' | 'SUPERSEDED';
  admin_review_notes?: string;
  base_ex_showroom: number;
  rto_road_tax: number;
  insurance_amount: number;
  tcs_amount: number;
  mfg_discount: number;
  dealer_discount: number;
  exchange_bonus: number;
  corporate_discount: number;
  accessories_amount: number;
  logistics_handling: number;
  other_statutory_charges: number;
  final_on_road_price: number;
  delivery_timeline_days: number;
  offer_valid_until: string;
  remarks?: string;
  created_at: string;
  updated_at: string;
  revisions_count?: number;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  event_type: string;
  link_url?: string;
  is_read: boolean;
  created_at: string;
}

export interface DealerDashboardStats {
  invitations_count: number;
  active_bidding_count: number;
  quotations_submitted_count: number;
  leads_count: number;
  conversions_count: number;
}

export interface BuyerLead {
  id: string;
  group_id: string;
  buyer_id: string;
  dealer_id: string;
  quotation_id: string;
  status: string;
  buyer_consent_given: boolean;
  notes?: string;
  created_at: string;
  buyer_name?: string;
  buyer_phone?: string;
  buyer_email?: string;
  dealership_name?: string;
  vehicle_name?: string;
  quoted_price?: number;
}
