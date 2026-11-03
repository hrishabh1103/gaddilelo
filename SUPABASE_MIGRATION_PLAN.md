# GaadiLelo.com — Supabase Migration Plan

## 1. Supabase Project Context
- **Project URL**: `https://khgvmqfidpazfdjitkeb.supabase.co`
- **Database Engine**: PostgreSQL 15 (Supabase Cloud)
- **Target Schema**: Public schema (`public`)

---

## 2. Migration Files & Sequence

The migration suite consists of four sequential SQL migrations located in `database/migrations/`:

| Sequence | File Name | Description | Key Tables / Objects |
| :---: | :--- | :--- | :--- |
| **001** | `001_initial_schema.sql` | Core domain entities | `users`, `dealers`, `dealer_documents`, `vehicles`, `vehicle_variants`, `vehicle_images`, `buying_groups`, `group_memberships`, `dealer_quotations`, `quotation_revisions`, `quotation_reviews`, `dealer_invitations`, `admin_audit_logs`, `lead_dispatches` (22 tables, foreign keys, and indexes) |
| **002** | `002_vehicle_intelligence.sql` | Market intelligence engine | `source_registries`, `ingestion_runs`, `vehicle_market_snapshots`, `rto_tax_rules`, `intelligence_audit_logs`, `ingestion_quarantine` (6 tables) |
| **003** | `003_free_vehicle_data.sql` | Reference seed catalogue | Seeds verified vehicle models (Tata Nexon, Punch, Safari, Mahindra XUV700, Thar, Scorpio-N, Maruti Brezza, Grand Vitara, Hyundai Creta) and regional Indore RTO rates |
| **004** | `004_buyer_intent_and_auth.sql` | Auth security, intent audit & RLS | `buyer_intent_confirmations`, `auth_tokens`, `revoked_tokens` + Row-Level Security (RLS) policies for user privacy and quotation protection |

---

## 3. Schema Compatibility Verification

All 4 migrations were parsed, validated, and verified using `scripts/verify_postgres_migrations.py`:
- **PostgreSQL Native Types**: Uses `UUID PRIMARY KEY DEFAULT gen_random_uuid()`, `TIMESTAMPTZ`, and `BOOLEAN DEFAULT TRUE`.
- **Foreign Key Integrity**: All foreign keys match parent column data types (`VARCHAR(36)` or `UUID`).
- **Idempotency**: All table creation statements use `CREATE TABLE IF NOT EXISTS` and index creation uses `CREATE INDEX IF NOT EXISTS`.
- **RLS Integration**: 11 sensitive tables enforce Supabase Row-Level Security (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`), ensuring client-side Supabase requests cannot bypass business authorization rules.

---

## 4. Safe Migration Execution Procedure

### Step 4.1: Local Validation (100% Safe, Zero DB Connection)
Validate migration files, sequence, and SHA-256 checksums locally:
```bash
python scripts/run_migrations.py --validate
```

### Step 4.2: Read-Only Connection Probe (Safe Probe)
Verify that your Supabase instance is reachable without modifying any data:
```bash
python scripts/run_migrations.py --check-connection --db-url "postgresql://postgres:[PASSWORD]@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
```

### Step 4.3: Dry-Run Migration Plan (Read-Only Inspection)
Inspect remote `schema_migrations`, applied checksums, and generate the exact execution plan without writing any DDL:
```bash
python scripts/run_migrations.py --plan --db-url "postgresql://postgres:[PASSWORD]@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
```

### Step 4.4: Live Migration Execution (Requires Explicit Approval)
Once the plan is reviewed and approved by the owner, execute pending migrations:
```bash
python scripts/run_migrations.py --execute --confirm-live-migration --db-url "postgresql://postgres:[PASSWORD]@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
```
*Note: This creates `schema_migrations`, runs each pending migration in an isolated transaction, logs execution times and checksums, and rolls back on failure.*

---

## 5. Rollback & Disaster Recovery Guidance

If any migration fails mid-execution:
1. The script stops execution immediately upon encountering an error.
2. Tables created with `IF NOT EXISTS` remain intact; no existing data is dropped.
3. To inspect table status directly via Supabase SQL Editor:
   ```sql
   SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
   ```
4. If a partial migration must be rolled back, execute targeted `DROP TABLE IF EXISTS <table_name> CASCADE;` for newly added tables in reverse order.

