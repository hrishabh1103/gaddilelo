#!/usr/bin/env python3
"""
GaadiLelo.com — Production-Grade Safe PostgreSQL Migration Runner
Supports:
  1. Local Validation (--validate): Verifies migration file sequence, integrity, and SHA-256 checksums without DB access.
  2. Connection Check (--check-connection): Safe read-only probe testing connectivity, SSL, and DB version.
  3. Migration Plan (--plan): Read-only inspection of remote migration history, applied checksums, and schema conflicts.
  4. Migration Execution (--execute --confirm-live-migration): Transactional, history-tracked execution with rollback.
"""

import os
import sys
import ssl
import hashlib
import time
import re
import argparse
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse, urlunparse

MIGRATIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "migrations"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CA_CERT = os.path.join(PROJECT_ROOT, "certs", "prod-ca-2021.crt")

MIGRATION_SEQUENCE = [
    "001_initial_schema.sql",
    "002_vehicle_intelligence.sql",
    "003_free_vehicle_data.sql",
    "004_buyer_intent_and_auth.sql"
]

def mask_connection_url(url: str) -> str:
    """Masks database password in connection string for safe console logging."""
    if not url:
        return "<EMPTY>"
    try:
        # Match standard URI pattern: protocol://user:pass@host:port/db
        pattern = r"://([^:]+):([^@]+)@"
        if re.search(pattern, url):
            return re.sub(pattern, r"://\1:***@", url)
        return url
    except Exception:
        return "postgresql://***:***@<masked>"

def normalize_db_url(url: str) -> str:
    """Ensures asyncpg dialect is present for SQLAlchemy async engine."""
    clean = url.strip()
    if clean.startswith("postgresql://"):
        clean = "postgresql+asyncpg://" + clean[len("postgresql://"):]
    elif clean.startswith("postgres://"):
        clean = "postgresql+asyncpg://" + clean[len("postgres://"):]
    return clean

def build_ssl_connect_args(db_url: str, ca_cert_path: Optional[str] = None) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Builds connect_args for asyncpg / SQLAlchemy engine with strict SSL verification.
    Enforces CERT_REQUIRED and check_hostname=True.
    
    Resolution order for CA certificate:
      1. Explicit ca_cert_path argument / --ssl-ca-cert
      2. DB_SSL_CA_CERT environment variable
      3. PGSSLROOTCERT environment variable
      4. Default project cert: certs/prod-ca-2021.crt (if exists)
      5. Standard system trusted CA bundle
    """
    connect_args: Dict[str, Any] = {}
    
    # Determine if target requires SSL
    is_remote = not any(local in db_url.lower() for local in ["sqlite", "localhost", "127.0.0.1"])
    needs_ssl = is_remote or "supabase" in db_url.lower() or "ssl" in db_url.lower()

    if not needs_ssl:
        return connect_args, None

    # Resolve target CA path
    target_ca = (
        ca_cert_path
        or os.getenv("DB_SSL_CA_CERT")
        or os.getenv("PGSSLROOTCERT")
    )

    if not target_ca and os.path.exists(DEFAULT_CA_CERT):
        target_ca = DEFAULT_CA_CERT

    if target_ca:
        if not os.path.exists(target_ca):
            raise FileNotFoundError(f"Configured SSL CA certificate not found: {target_ca}")
        ssl_ctx = ssl.create_default_context(cafile=target_ca)
    else:
        ssl_ctx = ssl.create_default_context()

    # Strict SSL verification and hostname checking (never disabled)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.check_hostname = True
    connect_args["ssl"] = ssl_ctx
    return connect_args, target_ca

def compute_checksum(file_path: str) -> str:
    """Computes SHA-256 checksum of file content."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

async def execute_sql_script(conn: Any, sql_content: str) -> None:
    """
    Executes a multi-statement SQL script safely within an active SQLAlchemy transaction.
    Under asyncpg, using conn.execute(text(sql)) creates a prepared statement, which
    PostgreSQL extended query protocol rejects for multi-command scripts.
    Instead, accessing raw_conn.driver_connection.execute() uses the PostgreSQL
    Simple Query protocol, executing all commands atomically within the transaction.
    """
    if hasattr(conn, "get_raw_connection"):
        raw_conn = await conn.get_raw_connection()
        driver_conn = getattr(raw_conn, "driver_connection", None)
        if driver_conn is not None and hasattr(driver_conn, "execute"):
            await driver_conn.execute(sql_content)
            return

    # Fallback for DBAPI / test mocks
    from sqlalchemy import text
    await conn.execute(text(sql_content))

def get_local_migrations() -> List[Dict[str, Any]]:
    """Inspects local migration files and returns metadata and checksums."""
    manifest = []
    for idx, fname in enumerate(MIGRATION_SEQUENCE, start=1):
        fpath = os.path.join(MIGRATIONS_DIR, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Migration file missing on disk: {fpath}")
        
        checksum = compute_checksum(fpath)
        version_id = fname.split("_")[0]
        
        manifest.append({
            "sequence": idx,
            "version": version_id,
            "filename": fname,
            "filepath": fpath,
            "checksum": checksum,
            "size_bytes": os.path.getsize(fpath)
        })
    return manifest

def validate_local_migrations() -> bool:
    """Validates local migration file structure, ordering, and checksums."""
    print("====================================================================")
    print("GAADILELO — LOCAL MIGRATION FILE VALIDATION (NO DB CONNECTION)")
    print("====================================================================")
    print(f"Directory: {MIGRATIONS_DIR}\n")

    try:
        manifest = get_local_migrations()
    except Exception as e:
        print(f"[FATAL ERROR] {str(e)}")
        return False

    print(f"{'Seq':<4} {'Version':<8} {'Filename':<35} {'Size (KB)':<10} {'SHA-256 Checksum':<20}")
    print("-" * 85)
    for m in manifest:
        kb = round(m["size_bytes"] / 1024, 2)
        short_hash = f"{m['checksum'][:16]}..."
        print(f"{m['sequence']:<4} {m['version']:<8} {m['filename']:<35} {kb:<10} {short_hash:<20}")

    print("\n[SUCCESS] Local validation passed. All 4 migration files exist in proper sequence.")
    print("Checksums are registered and ready for integrity tracking.")
    return True

async def check_connection(db_url: str, ca_cert_path: Optional[str] = None) -> bool:
    """Executes a safe read-only probe against PostgreSQL."""
    masked = mask_connection_url(db_url)
    async_url = normalize_db_url(db_url)
    print("====================================================================")
    print("GAADILELO — READ-ONLY POSTGRESQL CONNECTION CHECK")
    print("====================================================================")
    print(f"Target: {masked}")

    # Check for PgBouncer transaction mode warning
    if ":6543" in db_url:
        print("[NOTICE] Port 6543 detected (Supabase PgBouncer Transaction Pooler).")
        print("For DDL migrations, Direct port 5432 or Session Pooler is strongly recommended.")

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        connect_args, resolved_ca = build_ssl_connect_args(db_url, ca_cert_path)
        if "ssl" in connect_args:
            print("  SSL Mode        : VERIFY-FULL (CERT_REQUIRED, check_hostname=True)")
            if resolved_ca:
                print(f"  SSL CA Cert     : {resolved_ca}")

        start_time = time.time()
        engine = create_async_engine(async_url, connect_args=connect_args)
        
        async with engine.begin() as conn:
            # Enforce read-only transaction for safety
            await conn.execute(text("SET TRANSACTION READ ONLY"))
            result = await conn.execute(text("SELECT version(), current_database(), current_user, NOW()"))
            row = result.fetchone()
            latency_ms = round((time.time() - start_time) * 1000, 2)

        await engine.dispose()

        print("\n[SUCCESS] Connected to target PostgreSQL database successfully!")
        print(f"  Database Name : {row[1]}")
        print(f"  Connected User: {row[2]}")
        print(f"  Database Time : {row[3]}")
        print(f"  Roundtrip Time: {latency_ms} ms")
        print(f"  PG Version    : {row[0]}")
        return True

    except Exception as e:
        print(f"\n[CONNECTION FAILED] {str(e)}")
        print("Tips:")
        print(" - Verify credentials and database password.")
        print(" - Verify network access (ensure your IP/network can route to Supabase).")
        print(" - Ensure you are using port 5432 or Supabase Session Pooler.")
        return False

async def plan_migrations(db_url: str, ca_cert_path: Optional[str] = None) -> bool:
    """Connects read-only to inspect remote migration history and plan execution."""
    masked = mask_connection_url(db_url)
    async_url = normalize_db_url(db_url)
    print("====================================================================")
    print("GAADILELO — REMOTE MIGRATION PLAN (READ-ONLY INSPECTION)")
    print("====================================================================")
    print(f"Target: {masked}\n")

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        local_manifest = get_local_migrations()
        connect_args, resolved_ca = build_ssl_connect_args(db_url, ca_cert_path)
        if "ssl" in connect_args:
            print("  SSL Mode        : VERIFY-FULL (CERT_REQUIRED, check_hostname=True)")
            if resolved_ca:
                print(f"  SSL CA Cert     : {resolved_ca}")
            print()

        engine = create_async_engine(async_url, connect_args=connect_args)

        applied_migrations = {}
        has_history_table = False

        async with engine.begin() as conn:
            await conn.execute(text("SET TRANSACTION READ ONLY"))

            # 1. Check if schema_migrations history table exists
            table_check = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'schema_migrations'
                )
            """))
            has_history_table = bool(table_check.scalar())

            if has_history_table:
                # Read applied history
                rows = await conn.execute(text("""
                    SELECT version, filename, checksum, applied_at, status 
                    FROM schema_migrations 
                    ORDER BY version ASC
                """))
                for r in rows.fetchall():
                    applied_migrations[r[0]] = {
                        "filename": r[1],
                        "checksum": r[2],
                        "applied_at": r[3],
                        "status": r[4]
                    }

            # 2. Inspect existing tables in public schema
            tables_result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name ASC
            """))
            existing_tables = [t[0] for t in tables_result.fetchall()]

        await engine.dispose()

        print("--- Remote Database Status ---")
        if has_history_table:
            print(f"  Migration History Table: FOUND (schema_migrations, {len(applied_migrations)} records)")
        else:
            print("  Migration History Table: NOT FOUND (Database is uninitialized or unmanaged)")
        print(f"  Existing Public Tables : {len(existing_tables)} tables present\n")

        print(f"{'Version':<8} {'Filename':<35} {'State':<15} {'Details'}")
        print("-" * 80)

        pending_count = 0
        error_count = 0

        for m in local_manifest:
            v = m["version"]
            if v in applied_migrations:
                applied = applied_migrations[v]
                if applied["checksum"] == m["checksum"]:
                    state = "APPLIED"
                    details = f"Applied on {applied['applied_at']}"
                else:
                    state = "CHECKSUM MISMATCH"
                    details = f"WARNING! Local file was altered after migration (DB: {applied['checksum'][:8]}... Local: {m['checksum'][:8]}...)"
                    error_count += 1
            else:
                state = "PENDING"
                details = "Ready to be applied"
                pending_count += 1

            print(f"{v:<8} {m['filename']:<35} {state:<15} {details}")

        print("\n--- Plan Summary ---")
        print(f"Total Migrations : {len(local_manifest)}")
        print(f"Already Applied  : {len(applied_migrations)}")
        print(f"Pending to Apply : {pending_count}")
        print(f"Integrity Errors : {error_count}")

        if error_count > 0:
            print("\n[ACTION REQUIRED] Checksum mismatch detected! Do not proceed until discrepancies are resolved.")
            return False
        elif pending_count == 0:
            print("\n[SUCCESS] Database is fully up to date. No pending migrations.")
            return True
        else:
            print(f"\n[READY] {pending_count} pending migration(s) ready to apply.")
            print("To execute, run with: python scripts/run_migrations.py --execute --confirm-live-migration")
            return True

    except Exception as e:
        print(f"\n[PLAN FAILED] Error inspecting remote database: {str(e)}")
        return False

async def execute_migrations(db_url: str, ca_cert_path: Optional[str] = None) -> bool:
    """Applies pending migrations in strict sequence with transactional integrity and history logging."""
    masked = mask_connection_url(db_url)
    async_url = normalize_db_url(db_url)
    print("====================================================================")
    print("GAADILELO — LIVE DATABASE MIGRATION EXECUTION")
    print("====================================================================")
    print(f"Target: {masked}\n")

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        local_manifest = get_local_migrations()
        connect_args, resolved_ca = build_ssl_connect_args(db_url, ca_cert_path)
        if "ssl" in connect_args and resolved_ca:
            print(f"  SSL CA Cert     : {resolved_ca}\n")

        engine = create_async_engine(async_url, connect_args=connect_args)

        # 1. Initialize schema_migrations table if not exists
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(50) PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    execution_time_ms INTEGER NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'APPLIED'
                );
            """))

        # 2. Fetch applied migrations
        async with engine.begin() as conn:
            rows = await conn.execute(text("SELECT version, checksum FROM schema_migrations"))
            applied = {r[0]: r[1] for r in rows.fetchall()}

        # 3. Determine pending migrations
        pending = []
        for m in local_manifest:
            v = m["version"]
            if v in applied:
                if applied[v] != m["checksum"]:
                    raise ValueError(f"Checksum mismatch for migration {m['filename']}! DB: {applied[v]}, File: {m['checksum']}")
            else:
                pending.append(m)

        if not pending:
            print("[INFO] No pending migrations to apply. Database is already up to date.")
            await engine.dispose()
            return True

        print(f"Found {len(pending)} pending migration(s) to execute.\n")

        # 4. Execute each migration in its own isolated transaction
        for m in pending:
            print(f"Applying [{m['version']}] {m['filename']}...")
            with open(m["filepath"], "r", encoding="utf-8") as f:
                sql_content = f.read()

            t0 = time.time()
            async with engine.begin() as conn:
                # Execute multi-statement DDL block via simple query protocol
                await execute_sql_script(conn, sql_content)
                elapsed_ms = int((time.time() - t0) * 1000)

                # Record in schema_migrations
                await conn.execute(
                    text("""
                        INSERT INTO schema_migrations (version, filename, checksum, execution_time_ms, status)
                        VALUES (:version, :filename, :checksum, :execution_time_ms, 'APPLIED')
                    """),
                    {
                        "version": m["version"],
                        "filename": m["filename"],
                        "checksum": m["checksum"],
                        "execution_time_ms": elapsed_ms
                    }
                )
            print(f"  -> Successfully applied {m['filename']} in {elapsed_ms} ms.\n")

        await engine.dispose()
        print("[SUCCESS] All pending migrations have been safely applied and recorded in schema_migrations.")
        return True

    except Exception as e:
        print(f"\n[FATAL ERROR] Migration failed: {str(e)}")
        print("Transaction was rolled back. Database remains in its prior valid state.")
        return False

def main():
    parser = argparse.ArgumentParser(description="GaadiLelo Safe PostgreSQL Migration Tool")
    parser.add_argument("--validate", action="store_true", help="Validate local migration files and checksums (No DB connection)")
    parser.add_argument("--check-connection", action="store_true", help="Execute read-only connection test to PostgreSQL")
    parser.add_argument("--plan", action="store_true", help="Inspect remote migration history and generate execution plan (Read-Only)")
    parser.add_argument("--execute", action="store_true", help="Execute pending migrations")
    parser.add_argument("--confirm-live-migration", action="store_true", help="Explicit confirmation guard required for --execute")
    parser.add_argument("--db-url", type=str, default=os.getenv("DATABASE_URL", ""), help="Target PostgreSQL connection string")
    parser.add_argument("--ssl-ca-cert", type=str, default=os.getenv("DB_SSL_CA_CERT", ""), help="Path to CA certificate for SSL verification")

    args = parser.parse_args()

    # Default to validate if no arguments provided
    if not (args.validate or args.check_connection or args.plan or args.execute):
        validate_local_migrations()
        return

    if args.validate:
        success = validate_local_migrations()
        sys.exit(0 if success else 1)

    if args.check_connection:
        if not args.db_url:
            print("[ERROR] DATABASE_URL environment variable or --db-url argument is required for --check-connection.")
            sys.exit(1)
        success = asyncio.run(check_connection(args.db_url, ca_cert_path=args.ssl_ca_cert or None))
        sys.exit(0 if success else 1)

    if args.plan:
        if not args.db_url:
            print("[ERROR] DATABASE_URL environment variable or --db-url argument is required for --plan.")
            sys.exit(1)
        success = asyncio.run(plan_migrations(args.db_url, ca_cert_path=args.ssl_ca_cert or None))
        sys.exit(0 if success else 1)

    if args.execute:
        if not args.confirm_live_migration:
            print("[ERROR] Safety Guard: Live migration requires both --execute AND --confirm-live-migration.")
            print("This ensures migrations are never triggered accidentally.")
            sys.exit(1)
        if not args.db_url:
            print("[ERROR] DATABASE_URL environment variable or --db-url argument is required for --execute.")
            sys.exit(1)
        success = asyncio.run(execute_migrations(args.db_url, ca_cert_path=args.ssl_ca_cert or None))
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
