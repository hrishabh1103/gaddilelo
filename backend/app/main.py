from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1 import (
    auth, catalog, groups, dealers, leads, pricing, notifications, admin
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Indian Vehicle Group-Buying Marketplace API Core (Indore Pilot)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware - allows any localhost or deployed origin seamlessly
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

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
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

