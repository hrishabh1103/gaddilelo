-- ====================================================================
-- GAADILELO.COM — Vehicle Intelligence & Automated Discovery Migration
-- Migration: 002_vehicle_intelligence.sql
-- Description: Sources, discovery jobs, records, specifications, price history, and updates
-- ====================================================================

-- 1. VEHICLE DATA SOURCES
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

CREATE INDEX IF NOT EXISTS idx_vds_enabled ON vehicle_data_sources(enabled);
CREATE INDEX IF NOT EXISTS idx_vds_type ON vehicle_data_sources(source_type);

-- 2. VEHICLE DISCOVERY JOBS
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

CREATE INDEX IF NOT EXISTS idx_vdj_status ON vehicle_discovery_jobs(status);
CREATE INDEX IF NOT EXISTS idx_vdj_query ON vehicle_discovery_jobs(search_query);

-- 3. VEHICLE DISCOVERY RECORDS
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

CREATE INDEX IF NOT EXISTS idx_vdr_status ON vehicle_discovery_records(review_status);
CREATE INDEX IF NOT EXISTS idx_vdr_brand_model ON vehicle_discovery_records(discovered_brand, discovered_model);

-- 4. VEHICLE SPECIFICATION SOURCES
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

CREATE INDEX IF NOT EXISTS idx_vss_field ON vehicle_specification_sources(field_name);
CREATE INDEX IF NOT EXISTS idx_vss_variant ON vehicle_specification_sources(vehicle_variant_id);

-- 5. VEHICLE PRICE HISTORY
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

CREATE INDEX IF NOT EXISTS idx_vph_variant_city ON vehicle_price_history(vehicle_variant_id, city_id);

-- 6. VEHICLE IMAGES
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

CREATE INDEX IF NOT EXISTS idx_vi_model ON vehicle_images(vehicle_model_id);

-- 7. VEHICLE UPDATE HISTORY
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

CREATE INDEX IF NOT EXISTS idx_vuh_model ON vehicle_update_history(vehicle_model_id);

-- 8. VEHICLE DISCOVERY SUBSCRIPTIONS
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

CREATE INDEX IF NOT EXISTS idx_vds_rec_sub ON vehicle_discovery_subscriptions(discovery_record_id, customer_email);

