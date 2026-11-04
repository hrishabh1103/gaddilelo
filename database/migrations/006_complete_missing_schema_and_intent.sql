-- ====================================================================
-- GAADILELO.COM — Complete Missing Schema & Intent Affirmations
-- Migration: 006_complete_missing_schema_and_intent.sql
-- Description: Adds intent_confirmed columns to group_members, creates buyer_intent_confirmations,
--              auth_tokens, vehicle intelligence tables and adds missing columns idempotently.
-- ====================================================================

-- 1. Extend group_members with buyer intent affirmation fields
ALTER TABLE group_members ADD COLUMN IF NOT EXISTS intent_confirmed BOOLEAN DEFAULT TRUE;
ALTER TABLE group_members ADD COLUMN IF NOT EXISTS intent_confirmed_at TIMESTAMPTZ DEFAULT NOW();

-- 2. Buyer Intent Confirmations (Requirement 6)
CREATE TABLE IF NOT EXISTS buyer_intent_confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID NOT NULL REFERENCES buying_groups(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purchase_timeline VARCHAR(50) NOT NULL,
    is_genuine_intent BOOLEAN NOT NULL DEFAULT TRUE,
    is_non_binding_acknowledged BOOLEAN NOT NULL DEFAULT TRUE,
    agreed_to_contact BOOLEAN NOT NULL DEFAULT TRUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    confirmed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_buyer_intent_group ON buyer_intent_confirmations(group_id);
CREATE INDEX IF NOT EXISTS idx_buyer_intent_user ON buyer_intent_confirmations(user_id);

-- 3. Auth Tokens & Revoked Tokens (for password reset and JWT revocation)
CREATE TABLE IF NOT EXISTS auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_type VARCHAR(50) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_tokens_user ON auth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_type ON auth_tokens(token_type);

CREATE TABLE IF NOT EXISTS revoked_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jti VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    revoked_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_revoked_tokens_jti ON revoked_tokens(jti);
CREATE INDEX IF NOT EXISTS idx_revoked_tokens_user ON revoked_tokens(user_id);

-- 4. Vehicle Intelligence & Discovery Tables (safe IF NOT EXISTS)
CREATE TABLE IF NOT EXISTS vehicle_data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(150) NOT NULL,
    source_url TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    access_method VARCHAR(50) DEFAULT 'RSS_FEED',
    licensing_status VARCHAR(50) DEFAULT 'OFFICIAL_PUBLIC',
    enabled BOOLEAN DEFAULT TRUE,
    update_frequency VARCHAR(50) DEFAULT 'DAILY',
    last_synced_at TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_discovery_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    search_query VARCHAR(255) NOT NULL,
    requested_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    source_id UUID REFERENCES vehicle_data_sources(id) ON DELETE SET NULL,
    job_type VARCHAR(50) DEFAULT 'CUSTOMER_REQUEST',
    status VARCHAR(50) DEFAULT 'PENDING',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS vehicle_discovery_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES vehicle_discovery_jobs(id) ON DELETE SET NULL,
    discovered_brand VARCHAR(100) NOT NULL,
    discovered_model VARCHAR(150) NOT NULL,
    category_slug VARCHAR(50) DEFAULT 'car',
    body_type VARCHAR(50) DEFAULT 'SUV',
    launch_status VARCHAR(50) DEFAULT 'LAUNCHED',
    model_year INT,
    reference_ex_showroom_min NUMERIC(12, 2),
    reference_ex_showroom_max NUMERIC(12, 2),
    extracted_data JSONB DEFAULT '{}'::jsonb,
    confidence_score NUMERIC(5, 2) DEFAULT 0.95,
    review_status VARCHAR(50) DEFAULT 'PENDING_REVIEW',
    admin_notes TEXT,
    reviewed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    published_model_id UUID REFERENCES vehicle_models(id) ON DELETE SET NULL,
    primary_source_url TEXT,
    primary_source_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_specification_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_variant_id UUID REFERENCES vehicle_variants(id) ON DELETE CASCADE,
    discovery_record_id UUID REFERENCES vehicle_discovery_records(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT NOT NULL,
    unit VARCHAR(30),
    source_url TEXT NOT NULL,
    source_name VARCHAR(150) NOT NULL,
    confidence_score NUMERIC(5, 2) DEFAULT 1.0,
    is_conflict BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_variant_id UUID REFERENCES vehicle_variants(id) ON DELETE CASCADE,
    discovery_record_id UUID REFERENCES vehicle_discovery_records(id) ON DELETE CASCADE,
    city_id UUID REFERENCES cities(id) ON DELETE SET NULL,
    price_type VARCHAR(50) DEFAULT 'EX_SHOWROOM_REFERENCE',
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    source_url TEXT,
    source_name VARCHAR(150),
    effective_from TIMESTAMPTZ DEFAULT NOW(),
    effective_until TIMESTAMPTZ,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_model_id UUID REFERENCES vehicle_models(id) ON DELETE CASCADE,
    discovery_record_id UUID REFERENCES vehicle_discovery_records(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    source_url TEXT,
    usage_rights_status VARCHAR(50) DEFAULT 'OFFICIAL_OEM_PRESS',
    image_type VARCHAR(50) DEFAULT 'EXTERIOR_FRONT',
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_update_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_model_id UUID REFERENCES vehicle_models(id) ON DELETE CASCADE,
    vehicle_variant_id UUID REFERENCES vehicle_variants(id) ON DELETE CASCADE,
    change_type VARCHAR(50) NOT NULL,
    previous_data JSONB,
    new_data JSONB,
    source_url TEXT,
    source_name VARCHAR(150),
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_discovery_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discovery_record_id UUID REFERENCES vehicle_discovery_records(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    customer_name VARCHAR(150) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20),
    target_city_id UUID REFERENCES cities(id) ON DELETE SET NULL,
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicle_dataset_syncs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name VARCHAR(100) NOT NULL,
    records_synced INT DEFAULT 0,
    sync_status VARCHAR(50) DEFAULT 'SUCCESS',
    notes TEXT,
    synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Extend vehicle_models and vehicle_variants with specifications and media attributes
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS generation VARCHAR(50);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS model_year INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS wikidata_id VARCHAR(50);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS length_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS width_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS height_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS wheelbase_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS ground_clearance_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS boot_space_litres INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS safety_rating_stars INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS safety_rating_agency VARCHAR(50);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS wikimedia_title VARCHAR(255);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ;

ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS engine_displacement_cc INTEGER;
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS battery_capacity_kwh NUMERIC(5, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS claimed_range_km NUMERIC(6, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS tested_range_km NUMERIC(6, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS real_world_range_km NUMERIC(6, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS claimed_mileage_kmpl NUMERIC(5, 2);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS source_priority INTEGER DEFAULT 1;
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ;

ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS source_page_url TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS author_name VARCHAR(200);
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS license_name VARCHAR(100);
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS license_url TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS attribution_html TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'VERIFIED';
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS width INTEGER;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS height INTEGER;

