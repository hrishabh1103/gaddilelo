from pydantic_settings import BaseSettings
from typing import List, Union, Optional
from pydantic import field_validator, model_validator, ConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "GaadiLelo Platform"
    BRAND_NAME: str = "GaadiLelo"
    BRAND_TAGLINE: str = "Buy Together. Save Together."
    DEFAULT_PILOT_CITY: str = "Indore"
    DEFAULT_STATE: str = "Madhya Pradesh"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "gaadilelo-super-secret-production-grade-key-2026-indore"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Dual database support: default to local sqlite+aiosqlite for zero-friction run,
    # or postgresql+asyncpg for production / Supabase.
    DATABASE_URL: str = "sqlite+aiosqlite:///./gaadilelo.db"
    
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Distributed cache / shared rate limiter backend
    REDIS_URL: Optional[str] = None

    # Supabase Integrations (optional for local, used when connecting to live Supabase)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Notification & Email Providers
    SMS_PROVIDER: str = "mock"
    EMAIL_PROVIDER: str = "mock" # "mock", "smtp", "sendgrid"
    WHATSAPP_ENABLED: bool = False

    # SMTP Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@gaadilelo.com"
    SMTP_USE_TLS: bool = True

    # SendGrid Configuration
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@gaadilelo.com"
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        env = (self.ENVIRONMENT or os.getenv("ENVIRONMENT", "development")).lower()
        if env == "production":
            if self.SECRET_KEY == "gaadilelo-super-secret-production-grade-key-2026-indore":
                raise ValueError("In production mode, a custom non-default SECRET_KEY must be provided via environment variables!")
            if self.DATABASE_URL.startswith("sqlite") or "sqlite" in self.DATABASE_URL:
                raise ValueError("In production mode, SQLite is not allowed! A managed PostgreSQL database (e.g. postgresql+asyncpg://...) must be configured.")
            if self.EMAIL_PROVIDER.lower() == "mock":
                raise ValueError("In production mode, EMAIL_PROVIDER cannot be 'mock'. A transactional email provider (smtp, sendgrid) must be configured.")
        return self

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings()
