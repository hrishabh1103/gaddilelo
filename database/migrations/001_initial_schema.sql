-- ====================================================================
-- GAADILELO.COM — Production Supabase / PostgreSQL Migration
-- Migration: 001_initial_schema.sql
-- Description: Core schema, Enums, UUIDs, Indexes, and RLS Policies
-- ====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ENUMS
CREATE TYPE user_role_enum AS ENUM ('BUYER', 'DEALER', 'ADMIN');
CREATE TYPE dealer_verification_enum AS ENUM ('PENDING', 'VERIFIED', 'REJECTED');
CREATE TYPE document_type_enum AS ENUM ('GST_CERTIFICATE', 'OEM_DEALERSHIP_AGREEMENT', 'PAN_CARD', 'TRADE_LICENSE', 'BANK_PROOF');
CREATE TYPE fuel_type_enum AS ENUM ('PETROL', 'DIESEL', 'CNG', 'ELECTRIC', 'HYBRID');
CREATE TYPE transmission_enum AS ENUM ('MANUAL', 'AUTOMATIC', 'AMT', 'CVT', 'DCT', 'SINGLE_SPEED_EV');
CREATE TYPE group_status_enum AS ENUM ('DRAFT', 'OPEN', 'QUALIFYING', 'READY_FOR_BIDDING', 'BIDDING_OPEN', 'OFFERS_AVAILABLE', 'COMPLETED', 'CANCELLED');
CREATE TYPE member_status_enum AS ENUM ('ACTIVE', 'QUALIFIED', 'WITHDRAWN', 'PURCHASED');
CREATE TYPE invitation_status_enum AS ENUM ('INVITED', 'ACCEPTED', 'DECLINED', 'SUBMITTED');
CREATE TYPE quotation_status_enum AS ENUM ('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'SUPERSEDED');
CREATE TYPE line_item_type_enum AS ENUM ('MANDATORY', 'OPTIONAL', 'COMPLIMENTARY', 'DISCOUNT');
CREATE TYPE lead_status_enum AS ENUM ('PENDING_CALLBACK', 'CONTACTED', 'TEST_DRIVE_SCHEDULED', 'BOOKING_IN_PROGRESS', 'PURCHASE_COMPLETED', 'LOST');
CREATE TYPE complaint_status_enum AS ENUM ('OPEN', 'INVESTIGATING', 'RESOLVED', 'DISMISSED');

-- 1. CITIES TABLE
CREATE TABLE IF NOT EXISTS cities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode_prefix VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. USERS & PROFILES TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role_enum NOT NULL DEFAULT 'BUYER',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    city_id UUID REFERENCES cities(id) ON DELETE SET NULL,
    preferred_language VARCHAR(10) DEFAULT 'en',
    communication_consent BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. DEALERS TABLE
CREATE TABLE IF NOT EXISTS dealers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    dealership_name VARCHAR(255) NOT NULL,
    legal_entity_name VARCHAR(255) NOT NULL,
    gstin VARCHAR(15) UNIQUE NOT NULL,
    city_id UUID REFERENCES cities(id) ON DELETE RESTRICT NOT NULL,
    address TEXT NOT NULL,
    authorized_brands JSONB NOT NULL DEFAULT '[]'::jsonb,
    verification_status dealer_verification_enum NOT NULL DEFAULT 'PENDING',
    verification_notes TEXT,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dealer_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dealer_id UUID REFERENCES dealers(id) ON DELETE CASCADE NOT NULL,
    document_type document_type_enum NOT NULL,
    file_url TEXT NOT NULL,
    verification_status dealer_verification_enum NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. VEHICLE CATALOG TABLES
CREATE TABLE IF NOT EXISTS vehicle_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_name VARCHAR(50),
    display_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES vehicle_categories(id) ON DELETE RESTRICT NOT NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES vehicle_brands(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    body_type VARCHAR(50) NOT NULL,
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES vehicle_models(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(150) NOT NULL,
    fuel_type fuel_type_enum NOT NULL,
    transmission transmission_enum NOT NULL,
    seating_capacity INT DEFAULT 5,
    engine_cc_or_battery_kwh VARCHAR(50),
    reference_ex_showroom NUMERIC(12, 2) NOT NULL,
    specifications JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. BUYING GROUPS & MEMBERSHIP
CREATE TABLE IF NOT EXISTS buying_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_code VARCHAR(30) UNIQUE NOT NULL,
    vehicle_variant_id UUID REFERENCES vehicle_variants(id) ON DELETE RESTRICT NOT NULL,
    city_id UUID REFERENCES cities(id) ON DELETE RESTRICT NOT NULL,
    created_by_user_id UUID REFERENCES users(id) ON DELETE RESTRICT NOT NULL,
    status group_status_enum NOT NULL DEFAULT 'OPEN',
    target_members INT NOT NULL DEFAULT 5,
    current_members_count INT NOT NULL DEFAULT 1,
    target_purchase_timeline VARCHAR(50) NOT NULL,
    bidding_start_time TIMESTAMPTZ,
    bidding_end_time TIMESTAMPTZ,
    additional_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS group_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES buying_groups(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    buyer_notes TEXT,
    status member_status_enum NOT NULL DEFAULT 'ACTIVE',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_group_user UNIQUE(group_id, user_id)
);

-- 6. DEALER INVITATIONS, QUOTATIONS & LINE ITEMS
CREATE TABLE IF NOT EXISTS dealer_group_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES buying_groups(id) ON DELETE CASCADE NOT NULL,
    dealer_id UUID REFERENCES dealers(id) ON DELETE CASCADE NOT NULL,
    status invitation_status_enum NOT NULL DEFAULT 'INVITED',
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_group_dealer UNIQUE(group_id, dealer_id)
);

CREATE TABLE IF NOT EXISTS quotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES buying_groups(id) ON DELETE CASCADE NOT NULL,
    dealer_id UUID REFERENCES dealers(id) ON DELETE CASCADE NOT NULL,
    revision_number INT DEFAULT 1,
    status quotation_status_enum NOT NULL DEFAULT 'SUBMITTED',
    admin_review_notes TEXT,
    base_ex_showroom NUMERIC(12, 2) NOT NULL,
    rto_road_tax NUMERIC(12, 2) NOT NULL DEFAULT 0,
    insurance_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    tcs_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    mfg_discount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    dealer_discount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    exchange_bonus NUMERIC(12, 2) NOT NULL DEFAULT 0,
    corporate_discount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    accessories_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    logistics_handling NUMERIC(12, 2) NOT NULL DEFAULT 0,
    other_statutory_charges NUMERIC(12, 2) NOT NULL DEFAULT 0,
    final_on_road_price NUMERIC(12, 2) NOT NULL,
    delivery_timeline_days INT NOT NULL,
    offer_valid_until TIMESTAMPTZ NOT NULL,
    remarks TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quotation_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE NOT NULL,
    revision_number INT NOT NULL,
    snapshot JSONB NOT NULL,
    revised_at TIMESTAMPTZ DEFAULT NOW(),
    revised_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS quotation_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    item_type line_item_type_enum NOT NULL,
    amount NUMERIC(12, 2) NOT NULL
);

-- 7. BUYER LEADS & NOTIFICATIONS
CREATE TABLE IF NOT EXISTS buyer_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES buying_groups(id) ON DELETE CASCADE NOT NULL,
    buyer_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    dealer_id UUID REFERENCES dealers(id) ON DELETE CASCADE NOT NULL,
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE NOT NULL,
    status lead_status_enum NOT NULL DEFAULT 'PENDING_CALLBACK',
    buyer_consent_given BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    link_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS complaints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submitted_by_user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    target_dealer_id UUID REFERENCES dealers(id) ON DELETE SET NULL,
    group_id UUID REFERENCES buying_groups(id) ON DELETE SET NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status complaint_status_enum NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_dealers_city ON dealers(city_id);
CREATE INDEX IF NOT EXISTS idx_dealers_gstin ON dealers(gstin);
CREATE INDEX IF NOT EXISTS idx_models_brand ON vehicle_models(brand_id);
CREATE INDEX IF NOT EXISTS idx_variants_model ON vehicle_variants(model_id);
CREATE INDEX IF NOT EXISTS idx_groups_city_status ON buying_groups(city_id, status);
CREATE INDEX IF NOT EXISTS idx_groups_variant ON buying_groups(vehicle_variant_id);
CREATE INDEX IF NOT EXISTS idx_quotations_group ON quotations(group_id);
CREATE INDEX IF NOT EXISTS idx_quotations_dealer ON quotations(dealer_id);
CREATE INDEX IF NOT EXISTS idx_leads_dealer_status ON buyer_leads(dealer_id, status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

-- ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE dealers ENABLE ROW LEVEL SECURITY;
ALTER TABLE buying_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotations ENABLE ROW LEVEL SECURITY;
ALTER TABLE buyer_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- 1. Users can read and update their own record
CREATE POLICY users_self_access ON users 
    FOR ALL USING (id = auth.uid());

-- 2. User profiles self access, Admin full access
CREATE POLICY profiles_self_access ON user_profiles 
    FOR ALL USING (user_id = auth.uid());

-- 3. Dealers can read and update their own dealership profile
CREATE POLICY dealers_owner_access ON dealers 
    FOR ALL USING (user_id = auth.uid());

-- 4. Buying groups: Everyone can view OPEN / QUALIFYING / BIDDING / OFFERS groups
CREATE POLICY groups_public_read ON buying_groups 
    FOR SELECT USING (status != 'DRAFT' OR created_by_user_id = auth.uid());

-- 5. Quotations: Only approved quotations visible to buyers; dealers can see their own quotations
CREATE POLICY quotations_visibility ON quotations 
    FOR SELECT USING (
        status = 'APPROVED' 
        OR dealer_id IN (SELECT id FROM dealers WHERE user_id = auth.uid())
    );

-- 6. Notifications: Users can only see their own notifications
CREATE POLICY notifications_owner ON notifications 
    FOR ALL USING (user_id = auth.uid());
