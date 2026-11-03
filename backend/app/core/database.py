import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings

# Normalize database URL scheme for SQLAlchemy asyncpg
raw_db_url = settings.DATABASE_URL.strip()
if raw_db_url.startswith("postgresql://"):
    db_url = "postgresql+asyncpg://" + raw_db_url[len("postgresql://"):]
elif raw_db_url.startswith("postgres://"):
    db_url = "postgresql+asyncpg://" + raw_db_url[len("postgres://"):]
else:
    db_url = raw_db_url

# Engine configuration
connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False
else:
    # Supabase / PostgreSQL configuration
    ca_cert = os.getenv("DB_SSL_CA_CERT")
    if not ca_cert:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        default_ca = os.path.join(project_root, "certs", "prod-ca-2021.crt")
        if os.path.exists(default_ca):
            ca_cert = default_ca

    if ca_cert and os.path.exists(ca_cert):
        ssl_ctx = ssl.create_default_context(cafile=ca_cert)
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.check_hostname = True
        connect_args["ssl"] = ssl_ctx
    elif "supabase" in db_url.lower() or "ssl" in db_url.lower():
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.check_hostname = True
        connect_args["ssl"] = ssl_ctx

    # Support for Supabase PgBouncer / Shared Pooler mode (disables prepared statement cache)
    if ":6543" in db_url or "pooler" in db_url.lower():
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_cache_size"] = 0

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

