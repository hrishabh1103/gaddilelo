# GaadiLelo.com — Supabase Migration Safety Report

**Date**: November 3, 2026  
**Subject**: Safe PostgreSQL Migration Architecture, Tooling, History Tracking, and Idempotency  
**Target Environment**: Supabase Project `https://khgvmqfidpazfdjitkeb.supabase.co`  
**Status**: **TOOLING VERIFIED LOCALLY — REMOTE EXECUTION BLOCKED PENDING OWNER APPROVAL**

---

## 1. Executive Summary

In response to the critical audit findings, the migration runner (`scripts/run_migrations.py`) and migration SQL files (`database/migrations/`) have been rebuilt to enforce enterprise-grade database migration safety:

1. **Migration History Tracking Table (`schema_migrations`)**:
   Tracks applied migration version, filename, SHA-256 checksum, execution time in milliseconds, applied timestamp, and status. Detects already-applied migrations, missing files, and out-of-order executions.
2. **Checksum Integrity & Tamper Detection**:
   Every local migration file is verified against its cryptographic SHA-256 hash. If an applied migration file is edited or tampered with on disk, the runner halts immediately and warns the operator.
3. **Guarded Idempotent DDL**:
   - `001_initial_schema.sql` now wraps all 12 `CREATE TYPE ... AS ENUM` statements inside idempotent `DO $$ BEGIN IF NOT EXISTS ... END IF; END $$;` blocks.
   - All Row-Level Security (RLS) policies in `001_initial_schema.sql` and `004_buyer_intent_and_auth.sql` are wrapped with `IF NOT EXISTS` policy checks against `pg_policies`.
   - Tables and indexes continue to use `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.
4. **Strictly Separated Command Modes**:
   - `--validate`: Local validation only (zero DB access, zero credentials required).
   - `--check-connection`: Read-only probe executing `SELECT version()` in a `READ ONLY` transaction.
   - `--plan`: Read-only inspection of remote `schema_migrations` and `information_schema.tables`. Generates a dry-run plan without applying SQL.
   - `--execute`: Requires explicit `--execute` AND `--confirm-live-migration` flags. Applies only pending migrations in isolated transactions with automatic rollback on error.
5. **No Automatic Migrations on Startup**:
   Verified that FastAPI lifespan in `backend/app/main.py` **never** runs DDL or automatic migrations against production PostgreSQL (it strictly issues a passive `SELECT 1` ping).

---

## 2. Migration Manifest & SHA-256 Checksums

The local migration files in `database/migrations/` have been verified and registered:

| Sequence | Version | File Name | Size (Bytes) | SHA-256 Checksum |
| :---: | :---: | :--- | :---: | :--- |
| **1** | `001` | `001_initial_schema.sql` | 15,248 | `5687a4513b3aeb56fe8cf860ba26c922572bca5362ffb587a840e6981fae6a00` |
| **2** | `002` | `002_vehicle_intelligence.sql` | 6,482 | `e6d1ad26e96e8c304d27f88ebbc19f906540b3724c9c1aa2bfa7c91a0cba54b1` |
| **3** | `003` | `003_free_vehicle_data.sql` | 3,881 | `88b229099d8b7c3ad99d87304245ad35db4057881079d846b08aa3eb1fe3910c` |
| **4** | `004` | `004_buyer_intent_and_auth.sql` | 3,124 | `900143bbf47553a1a364807963d7eeb3544d9f6a738c6fa2f16ef062b08fa176` |

---

## 3. What is Safe to Run vs. What Requires Approval

| Operation | Command | DB Access | Credentials | Safety Level |
| :--- | :--- | :---: | :---: | :--- |
| **Local File Validation** | `python scripts/run_migrations.py --validate` | **None** | None | **100% Safe Locally**. Validates syntax, sequence, and hashes without network calls. |
| **Connection Check** | `python scripts/run_migrations.py --check-connection` | **Read-Only** | Required | **Safe Read-Only Probe**. Runs `SET TRANSACTION READ ONLY; SELECT version();`. Modifies zero data. |
| **Migration Plan** | `python scripts/run_migrations.py --plan` | **Read-Only** | Required | **Safe Read-Only Inspection**. Inspects `schema_migrations` and tables to output pending diffs. Modifies zero data. |
| **Live Migration Execution** | `python scripts/run_migrations.py --execute --confirm-live-migration` | **Write / DDL** | Required | **REQUIRES EXPLICIT OWNER APPROVAL**. Executes pending migrations in transactional blocks. |

---

## 4. How to Distinguish an Empty Database vs. Existing Database

When the owner runs `python scripts/run_migrations.py --plan`, the tool automatically inspects the database and reports one of two states:

### Case A: Completely Empty / Fresh Database
```
  Migration History Table: NOT FOUND (Database is uninitialized or unmanaged)
  Existing Public Tables : 0 tables present
  Plan Summary: Total Migrations: 4 | Already Applied: 0 | Pending to Apply: 4
```
*Action*: Safe to proceed with `--execute --confirm-live-migration`. It will create `schema_migrations` and apply 001 through 004 in order.

### Case B: Existing / Partially Populated Database
```
  Migration History Table: FOUND (schema_migrations, 2 records)
  Existing Public Tables : 28 tables present
  Plan Summary: Total Migrations: 4 | Already Applied: 2 | Pending to Apply: 2
```
*Action*: The tool will automatically skip already-applied migrations (001 and 002) and queue only the remaining pending migrations (003 and 004).

---

## 5. Rollback & Failure Recovery Procedures

1. **Transactional Isolation**:
   Every migration runs inside an explicit `async with engine.begin() as conn:` block. If any error occurs during SQL execution (e.g. syntax error, constraint violation, connection drop):
   - The entire transaction for that migration is immediately rolled back by PostgreSQL.
   - No record is inserted into `schema_migrations`.
   - The database remains in its exact prior valid state.
2. **Resuming After Failure**:
   - Resolve the underlying issue (e.g. invalid type or network interruption).
   - Re-run `python scripts/run_migrations.py --plan` to verify the state.
   - Re-run `python scripts/run_migrations.py --execute --confirm-live-migration`. The runner resumes execution from the failed migration without duplicating previously applied steps.
3. **Manual Table Removal (Emergency Rollback)**:
   If an operator ever needs to reverse a migration manually via the Supabase SQL Editor:
   ```sql
   -- View applied history:
   SELECT * FROM schema_migrations ORDER BY version DESC;

   -- Remove record if rolling back migration 004:
   DROP TABLE IF EXISTS buyer_intent_confirmations CASCADE;
   DROP TABLE IF EXISTS auth_tokens CASCADE;
   DROP TABLE IF EXISTS revoked_tokens CASCADE;
   DELETE FROM schema_migrations WHERE version = '004';
   ```

---

## 6. Secure Connection & IPv4/IPv6 Handling

1. **Password Masking**:
   The runner automatically intercepts all database URLs and masks passwords in logs (e.g., `postgresql+asyncpg://postgres:***@db...:5432/postgres`).
2. **Direct Connection (Port 5432) vs. Session Pooler (Port 5432/6543)**:
   - Direct port 5432 connects directly to the PostgreSQL instance. Note that direct connections on Supabase AWS regions use IPv6.
   - If connecting from a network that does not support IPv6, use the **Supabase Session Pooler** URI (e.g. `aws-0-ap-south-1.pooler.supabase.co:5432`) which supports IPv4.
   - **Important**: Do not use port 6543 (Transaction Pooler) for DDL migrations, as PgBouncer in transaction mode does not support PostgreSQL named prepared statements.

