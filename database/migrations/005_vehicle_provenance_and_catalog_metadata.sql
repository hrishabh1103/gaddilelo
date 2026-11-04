-- =====================================================================
-- GaadiLelo Migration 005: Vehicle Provenance & Catalog Metadata
-- Adds missing canonical identity, provenance, and data quality fields
-- to vehicle_brands, vehicle_models, and vehicle_variants tables.
--
-- Lock & Execution Characteristics:
-- - In PostgreSQL 11+, adding columns with constant defaults avoids a full
--   table rewrite by updating table catalog metadata.
-- - However, ALTER TABLE operations still acquire a brief ACCESS EXCLUSIVE
--   lock during metadata updates.
-- - Adding CHECK constraints without NOT VALID acquires a SHARE ROW EXCLUSIVE
--   lock and performs a sequential scan of vehicle_variants to validate
--   existing rows. Given catalog table sizes, this completes near-instantly.
-- =====================================================================

-- 1. Extend vehicle_brands with canonical metadata and data provenance
ALTER TABLE vehicle_brands ADD COLUMN IF NOT EXISTS canonical_name VARCHAR(100);
ALTER TABLE vehicle_brands ADD COLUMN IF NOT EXISTS external_source_id VARCHAR(100);
ALTER TABLE vehicle_brands ADD COLUMN IF NOT EXISTS source_name VARCHAR(50) DEFAULT 'meterapp';
ALTER TABLE vehicle_brands ADD COLUMN IF NOT EXISTS source_license VARCHAR(50) DEFAULT 'ISC';
ALTER TABLE vehicle_brands ADD COLUMN IF NOT EXISTS country VARCHAR(50) DEFAULT 'India';

-- 2. Extend vehicle_models with canonical naming, category slug, and provenance
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS canonical_brand_name VARCHAR(100);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS canonical_model_name VARCHAR(150);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS vehicle_category_slug VARCHAR(50);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS external_source_id VARCHAR(100);
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS source_name VARCHAR(50) DEFAULT 'meterapp';
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS source_license VARCHAR(50) DEFAULT 'ISC';
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS source_provenance JSONB DEFAULT '{}'::jsonb;
ALTER TABLE vehicle_models ADD COLUMN IF NOT EXISTS imported_at TIMESTAMPTZ;

-- 3. Extend vehicle_variants with source attribution, quality score, and review status
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS source_document VARCHAR(200);
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(3, 2) DEFAULT 1.0;
ALTER TABLE vehicle_variants ADD COLUMN IF NOT EXISTS review_status VARCHAR(30) DEFAULT 'VERIFIED';

-- 4. Idempotent CHECK Constraints for data integrity
DO $$
BEGIN
    -- Ensure confidence_score is between 0.00 and 1.00 when present
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_vehicle_variants_confidence_score'
          AND conrelid = 'vehicle_variants'::regclass
    ) THEN
        ALTER TABLE vehicle_variants
        ADD CONSTRAINT chk_vehicle_variants_confidence_score
        CHECK (confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0));
    END IF;

    -- Ensure review_status conforms to allowed lifecycle states
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_vehicle_variants_review_status'
          AND conrelid = 'vehicle_variants'::regclass
    ) THEN
        ALTER TABLE vehicle_variants
        ADD CONSTRAINT chk_vehicle_variants_review_status
        CHECK (review_status IS NULL OR review_status IN ('VERIFIED', 'PENDING_REVIEW', 'ADMIN_REVIEW'));
    END IF;
END $$;

