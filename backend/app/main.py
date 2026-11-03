from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.core.logging_redaction import setup_logging
from backend.app.db.migrate_provenance import run_migration
from backend.app.services.vehicle_intelligence.scheduler import VehicleIntelligenceScheduler
from backend.app.api.v1 import (
    auth, catalog, groups, dealers, leads, pricing, notifications, admin, intelligence
)

# Initialize logging redaction
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify database setup
    if settings.DATABASE_URL.startswith("sqlite") or "sqlite" in settings.DATABASE_URL:
        if settings.ENVIRONMENT.lower() == "production":
            raise RuntimeError(
                "CRITICAL STARTUP ERROR: SQLite database is forbidden in production! "
                "A managed PostgreSQL connection URL (postgresql+asyncpg://...) must be configured."
            )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        run_migration("gaadilelo.db")
    else:
        # PostgreSQL / Supabase in production
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    
    # Start Background Autonomous Vehicle Intelligence Scheduler
    scheduler = VehicleIntelligenceScheduler.get_instance()
    await scheduler.start(initial_delay_seconds=3)

    yield

    # Graceful Shutdown
    await scheduler.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Indian Vehicle Group-Buying Marketplace API Core (Indore Pilot)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
if settings.ENVIRONMENT.lower() == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register API v1 Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(catalog.router, prefix=settings.API_V1_STR)
app.include_router(groups.router, prefix=settings.API_V1_STR)
app.include_router(dealers.router, prefix=settings.API_V1_STR)
app.include_router(leads.router, prefix=settings.API_V1_STR)
app.include_router(pricing.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(intelligence.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
async def health_check():
    db_status = "connected"
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "email_provider": settings.EMAIL_PROVIDER,
        "brand": settings.BRAND_NAME,
        "tagline": settings.BRAND_TAGLINE,
        "pilot_city": settings.DEFAULT_PILOT_CITY,
        "state": settings.DEFAULT_STATE
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.BRAND_NAME} API Core",
        "tagline": settings.BRAND_TAGLINE,
        "docs_url": "/docs",
        "pilot_market": f"{settings.DEFAULT_PILOT_CITY}, {settings.DEFAULT_STATE}"
    }

