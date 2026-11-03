import os
import sys
import pytest
import hashlib
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.run_migrations import (
    get_local_migrations,
    compute_checksum,
    mask_connection_url,
    normalize_db_url,
    validate_local_migrations,
    check_connection,
    plan_migrations,
    execute_migrations,
    MIGRATIONS_DIR
)
from backend.app.core.config import settings

class TestMigrationSafetyTooling:

    def test_local_validation_without_database(self):
        """Validates that local validation runs and passes without any database connection."""
        success = validate_local_migrations()
        assert success is True

    def test_migration_sequence_and_integrity(self):
        """Verifies migration sequence, versions 001 through 004, and positive file size."""
        manifest = get_local_migrations()
        assert len(manifest) == 4
        versions = [m["version"] for m in manifest]
        assert versions == ["001", "002", "003", "004"]
        for m in manifest:
            assert m["size_bytes"] > 0
            assert len(m["checksum"]) == 64  # Valid SHA-256 length

    def test_checksum_generation_deterministic(self, tmp_path):
        """Verifies SHA-256 calculation is deterministic across executions."""
        test_file = tmp_path / "test_migration.sql"
        test_file.write_text("CREATE TABLE test_table (id INT);", encoding="utf-8")
        
        expected_hash = hashlib.sha256(b"CREATE TABLE test_table (id INT);").hexdigest()
        assert compute_checksum(str(test_file)) == expected_hash

    def test_connection_url_masking(self):
        """Ensures database passwords are never printed or logged."""
        raw_url = "postgresql://postgres:MySecretPassword123@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
        masked = mask_connection_url(raw_url)
        assert "MySecretPassword123" not in masked
        assert "postgres:***@" in masked
        assert "db.khgvmqfidpazfdjitkeb.supabase.co" in masked

    def test_normalize_db_url_scheme(self):
        """Verifies conversion from standard postgresql:// to SQLAlchemy asyncpg format."""
        raw_url = "postgresql://user:pass@host:5432/db"
        normalized = normalize_db_url(raw_url)
        assert normalized.startswith("postgresql+asyncpg://")

        # Idempotent if already has asyncpg
        assert normalize_db_url(normalized) == normalized

    @pytest.mark.asyncio
    async def test_connection_failure_handling(self):
        """Ensures invalid host / connection errors fail gracefully without raising uncaught exceptions."""
        bad_url = "postgresql+asyncpg://user:pass@nonexistent-host-12345.local:5432/db"
        success = await check_connection(bad_url)
        assert success is False

    @pytest.mark.asyncio
    async def test_plan_migrations_detects_already_applied_and_pending(self):
        """Tests planner logic when some migrations are already recorded in schema_migrations."""
        local_manifest = get_local_migrations()
        first_checksum = local_manifest[0]["checksum"]

        # Mock engine, connection, and result sets
        mock_conn = AsyncMock()
        # 1. table_check scalar() -> True (schema_migrations exists)
        mock_conn.execute.side_effect = [
            None, # SET TRANSACTION READ ONLY
            AsyncMock(scalar=MagicMock(return_value=True)), # information_schema table_check
            AsyncMock(fetchall=MagicMock(return_value=[
                ("001", "001_initial_schema.sql", first_checksum, "2026-11-03 10:00:00", "APPLIED")
            ])), # schema_migrations rows
            AsyncMock(fetchall=MagicMock(return_value=[("users",), ("cities",)])) # existing tables
        ]

        mock_engine = MagicMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_engine.dispose = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine):
            success = await plan_migrations("postgresql://fake:fake@localhost:5432/fake")
            assert success is True

    @pytest.mark.asyncio
    async def test_plan_migrations_detects_checksum_tampering(self):
        """Tests planner detection when an applied migration file was modified on disk."""
        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = [
            None, # SET TRANSACTION READ ONLY
            AsyncMock(scalar=MagicMock(return_value=True)), # schema_migrations exists
            AsyncMock(fetchall=MagicMock(return_value=[
                ("001", "001_initial_schema.sql", "tampered_fake_checksum_0000000000000000000000000000000000000000", "2026-11-03 10:00:00", "APPLIED")
            ])), # checksum mismatch
            AsyncMock(fetchall=MagicMock(return_value=[]))
        ]

        mock_engine = MagicMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_engine.dispose = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine):
            success = await plan_migrations("postgresql://fake:fake@localhost:5432/fake")
            # Should fail because of checksum mismatch
            assert success is False

    @pytest.mark.asyncio
    async def test_execute_migrations_rolls_back_on_failure(self):
        """Verifies transaction rollback and failure return if SQL execution raises an error."""
        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = [
            None, # CREATE TABLE schema_migrations
            AsyncMock(fetchall=MagicMock(return_value=[])), # applied rows (empty)
            Exception("Simulated SQL syntax or constraint failure") # migration execution fails
        ]

        mock_engine = MagicMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_engine.dispose = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine):
            success = await execute_migrations("postgresql://fake:fake@localhost:5432/fake")
            assert success is False

    def test_no_automatic_migration_on_production_startup(self):
        """
        Critical safety check: In production mode with PostgreSQL, FastAPI app lifespan
        must NEVER call create_all or run DDL migrations automatically.
        """
        import inspect
        from backend.app.main import lifespan
        
        source = inspect.getsource(lifespan)
        # Check that production PostgreSQL branch only executes SELECT 1, not create_all or migration
        assert 'SELECT 1' in source
        assert 'Base.metadata.create_all' not in source.split('else:')[1]
        assert 'run_migration' not in source.split('else:')[1]

    def test_cli_execute_blocked_without_confirm_flag(self):
        """Ensures --execute fails immediately if --confirm-live-migration is missing."""
        from scripts.run_migrations import main
        with patch("sys.argv", ["run_migrations.py", "--execute", "--db-url", "postgresql://user:pass@localhost/db"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_cli_defaults_to_validate_safely(self):
        """Ensures calling script with zero arguments runs local validation without network calls."""
        from scripts.run_migrations import main
        with patch("sys.argv", ["run_migrations.py"]):
            with patch("scripts.run_migrations.validate_local_migrations", return_value=True) as mock_val:
                main()
                mock_val.assert_called_once()

    def test_build_ssl_connect_args_default_cert(self):
        """Verifies build_ssl_connect_args creates a verified SSLContext with prod-ca-2021.crt."""
        from scripts.run_migrations import build_ssl_connect_args, DEFAULT_CA_CERT
        import ssl
        
        url = "postgresql://postgres:pass@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
        connect_args, resolved_ca = build_ssl_connect_args(url)
        
        assert "ssl" in connect_args
        ssl_ctx = connect_args["ssl"]
        assert isinstance(ssl_ctx, ssl.SSLContext)
        assert ssl_ctx.verify_mode == ssl.CERT_REQUIRED
        assert ssl_ctx.check_hostname is True
        assert resolved_ca == DEFAULT_CA_CERT

    def test_build_ssl_connect_args_env_var(self, tmp_path, monkeypatch):
        """Verifies DB_SSL_CA_CERT environment variable is prioritized."""
        from scripts.run_migrations import build_ssl_connect_args
        import ssl
        
        # Write dummy certificate in temp path
        dummy_ca = tmp_path / "custom-ca.crt"
        dummy_ca.write_text("-----BEGIN CERTIFICATE-----\nFAKE\n-----END CERTIFICATE-----")
        
        monkeypatch.setenv("DB_SSL_CA_CERT", str(dummy_ca))
        url = "postgresql://postgres:pass@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
        
        # Mock ssl.create_default_context to accept dummy CA
        orig_create = ssl.create_default_context
        with patch("ssl.create_default_context", side_effect=lambda cafile=None: orig_create()) as mock_ssl:
            connect_args, resolved_ca = build_ssl_connect_args(url)
            assert resolved_ca == str(dummy_ca)
            assert "ssl" in connect_args
            assert connect_args["ssl"].verify_mode == ssl.CERT_REQUIRED
            assert connect_args["ssl"].check_hostname is True

    def test_build_ssl_connect_args_nonexistent_file_raises(self, monkeypatch):
        """Verifies FileNotFoundError is raised if a specified CA file does not exist."""
        from scripts.run_migrations import build_ssl_connect_args
        
        monkeypatch.setenv("DB_SSL_CA_CERT", "/nonexistent/path/to/cert.crt")
        url = "postgresql://postgres:pass@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            build_ssl_connect_args(url)
        assert "Configured SSL CA certificate not found" in str(exc_info.value)

    def test_build_ssl_connect_args_local_db_no_ssl(self):
        """Verifies local databases (sqlite, localhost) do not enforce SSL."""
        from scripts.run_migrations import build_ssl_connect_args
        
        connect_args, resolved_ca = build_ssl_connect_args("sqlite+aiosqlite:///./test.db")
        assert connect_args == {}
        assert resolved_ca is None

    @pytest.mark.asyncio
    async def test_check_connection_uses_custom_ssl_context(self):
        """Verifies check_connection passes the custom verified SSLContext into create_async_engine."""
        import ssl
        from scripts.run_migrations import check_connection

        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = [
            None,  # SET TRANSACTION READ ONLY
            AsyncMock(fetchone=MagicMock(return_value=["PostgreSQL 15.1", "postgres", "postgres", "2026-11-03"]))
        ]
        mock_engine = MagicMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        mock_engine.dispose = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine) as mock_create_engine:
            url = "postgresql://postgres:pass@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
            success = await check_connection(url)
            assert success is True

            # Verify engine was called with an SSLContext in connect_args
            call_kwargs = mock_create_engine.call_args[1]
            assert "connect_args" in call_kwargs
            assert "ssl" in call_kwargs["connect_args"]
            ssl_ctx = call_kwargs["connect_args"]["ssl"]
            assert isinstance(ssl_ctx, ssl.SSLContext)
            assert ssl_ctx.verify_mode == ssl.CERT_REQUIRED
            assert ssl_ctx.check_hostname is True

    def test_migration_003_foreign_key_type_matches_uuid(self):
        """Verifies that vehicle_variants.data_source_id uses UUID to match vehicle_data_sources.id."""
        import re
        fpath = os.path.join(MIGRATIONS_DIR, "003_free_vehicle_data.sql")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verify data_source_id is defined as UUID
        match = re.search(r'data_source_id\s+(\w+)\s+REFERENCES\s+vehicle_data_sources\(id\)', content)
        assert match is not None, "data_source_id foreign key reference not found in 003"
        col_type = match.group(1).upper()
        assert col_type == "UUID", f"Expected UUID for data_source_id, found {col_type}"
        
        # Ensure VARCHAR(36) is not referencing vehicle_data_sources
        assert not re.search(r'data_source_id\s+VARCHAR\(\d+\)\s+REFERENCES', content, re.IGNORECASE)

    @pytest.mark.asyncio
    async def test_execute_sql_script_simple_query_protocol(self):
        """Verifies execute_sql_script uses driver_connection.execute for multi-statement execution."""
        from scripts.run_migrations import execute_sql_script

        mock_driver_conn = AsyncMock()
        mock_raw_conn = MagicMock()
        mock_raw_conn.driver_connection = mock_driver_conn
        
        mock_conn = AsyncMock()
        mock_conn.get_raw_connection.return_value = mock_raw_conn

        multi_stmt_sql = "CREATE TABLE t1 (id INT); CREATE TABLE t2 (id INT);"
        await execute_sql_script(mock_conn, multi_stmt_sql)

        # Ensure driver_connection.execute was called with the full multi-statement content
        mock_driver_conn.execute.assert_called_once_with(multi_stmt_sql)

    @pytest.mark.asyncio
    async def test_execute_sql_script_fallback(self):
        """Verifies execute_sql_script falls back to conn.execute if driver_connection is absent."""
        from scripts.run_migrations import execute_sql_script

        mock_conn = AsyncMock()
        # Mock conn without get_raw_connection returning driver_connection
        mock_conn.get_raw_connection.return_value = object()

        sql = "SELECT 1;"
        await execute_sql_script(mock_conn, sql)
        mock_conn.execute.assert_called_once()

    def test_ssl_configuration_remains_verify_full(self):
        """Verifies SSL configuration strictly enforces CERT_REQUIRED and check_hostname=True."""
        import ssl
        from scripts.run_migrations import build_ssl_connect_args

        supabase_url = "postgresql://postgres:pass@db.khgvmqfidpazfdjitkeb.supabase.co:5432/postgres"
        connect_args, resolved_ca = build_ssl_connect_args(supabase_url)
        
        assert "ssl" in connect_args
        ctx = connect_args["ssl"]
        assert isinstance(ctx, ssl.SSLContext)
        # Verify mode must be CERT_REQUIRED (2)
        assert ctx.verify_mode == ssl.CERT_REQUIRED
        assert ctx.check_hostname is True

