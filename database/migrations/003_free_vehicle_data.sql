-- =====================================================================
-- GaadiLelo Migration 003: Free Vehicle Data Infrastructure
-- Supports VehiclesDB, Wikimedia Commons, Wikidata, and data.gov.in
-- =====================================================================

-- 1. Extend vehicle_models with dimensions, generation, safety ratings
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS generation VARCHAR(50);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS model_year INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS wikidata_id VARCHAR(50);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS length_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS width_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS height_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS wheelbase_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS ground_clearance_mm INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS safety_rating_stars INTEGER;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS safety_rating_agency VARCHAR(50);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMP WITH TIME ZONE;

-- 2. Extend vehicle_variants with range distinction and source hierarchy
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS engine_displacement_cc INTEGER;
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS battery_capacity_kwh NUMERIC(5, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS claimed_range_km NUMERIC(6, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS tested_range_km NUMERIC(6, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS real_world_range_km NUMERIC(6, 1);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS claimed_mileage_kmpl NUMERIC(5, 2);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS source_priority INTEGER DEFAULT 1;
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS data_source_id UUID REFERENCES vehicle_data_sources(id) ON DELETE SET NULL;
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMP WITH TIME ZONE;

-- 3. Extend vehicle_images with Wikimedia licensing, attribution and thumbnails
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS source_page_url TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS author_name VARCHAR(200);
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS license_name VARCHAR(100);
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS license_url TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS attribution_html TEXT;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'VERIFIED';
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS width INTEGER;
ALTER TABLE vehicle_images ADD COLUMN IF NOT EXISTS height INTEGER;

-- 4. Extend vehicle_specification_sources with priority and licensing
ALTER TABLE vehicle_specification_sources ADD COLUMN IF NOT EXISTS source_priority INTEGER DEFAULT 1;
ALTER TABLE vehicle_specification_sources ADD COLUMN IF NOT EXISTS license_name VARCHAR(100);
ALTER TABLE vehicle_specification_sources ADD COLUMN IF NOT EXISTS license_url TEXT;

-- 5. Create vehicle_dataset_syncs for incremental imports tracking
CREATE TABLE IF NOT EXISTS vehicle_dataset_syncs (
    id VARCHAR(36) PRIMARY KEY,
    dataset_name VARCHAR(100) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    records_imported INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'COMPLETED',
    error_message TEXT,
    sync_metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_dataset_syncs_name ON vehicle_dataset_syncs(dataset_name);

