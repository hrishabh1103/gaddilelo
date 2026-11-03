import sqlite3
import os

def run_migration(db_path: str = "gaadilelo.db"):
    """
    Applies incremental columns to support MeterApp canonical identity,
    source metadata, and variant review provenance without dropping data.
    """
    if not os.path.exists(db_path):
        print(f"[Migration] Database file {db_path} does not exist.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    def get_columns(table_name):
        cur.execute(f"PRAGMA table_info({table_name})")
        return [r[1] for r in cur.fetchall()]

    print(f"[Migration] Running provenance column migration on {db_path}...")

    # 1. Update vehicle_brands
    brand_cols = get_columns("vehicle_brands")
    brand_additions = [
        ("canonical_name", "VARCHAR(100)"),
        ("external_source_id", "VARCHAR(100)"),
        ("source_name", "VARCHAR(50) DEFAULT 'meterapp'"),
        ("source_license", "VARCHAR(50) DEFAULT 'ISC'"),
        ("country", "VARCHAR(50) DEFAULT 'India'"),
    ]
    for col_name, col_def in brand_additions:
        if col_name not in brand_cols:
            print(f"[Migration] Adding {col_name} to vehicle_brands")
            cur.execute(f"ALTER TABLE vehicle_brands ADD COLUMN {col_name} {col_def}")

    # 2. Update vehicle_models
    model_cols = get_columns("vehicle_models")
    model_additions = [
        ("canonical_brand_name", "VARCHAR(100)"),
        ("canonical_model_name", "VARCHAR(150)"),
        ("vehicle_category_slug", "VARCHAR(50)"),
        ("external_source_id", "VARCHAR(100)"),
        ("source_name", "VARCHAR(50) DEFAULT 'meterapp'"),
        ("source_license", "VARCHAR(50) DEFAULT 'ISC'"),
        ("source_provenance", "JSON DEFAULT '{}'"),
        ("imported_at", "DATETIME"),
    ]
    for col_name, col_def in model_additions:
        if col_name not in model_cols:
            print(f"[Migration] Adding {col_name} to vehicle_models")
            cur.execute(f"ALTER TABLE vehicle_models ADD COLUMN {col_name} {col_def}")

    # 3. Update vehicle_variants
    variant_cols = get_columns("vehicle_variants")
    variant_additions = [
        ("source_url", "TEXT"),
        ("source_document", "VARCHAR(200)"),
        ("confidence_score", "NUMERIC(3, 2) DEFAULT 1.0"),
        ("review_status", "VARCHAR(30) DEFAULT 'VERIFIED'"),
    ]
    for col_name, col_def in variant_additions:
        if col_name not in variant_cols:
            print(f"[Migration] Adding {col_name} to vehicle_variants")
            cur.execute(f"ALTER TABLE vehicle_variants ADD COLUMN {col_name} {col_def}")

    conn.commit()
    conn.close()
    print("[Migration] Provenance migration completed successfully.")

if __name__ == "__main__":
    run_migration()

