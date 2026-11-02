from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator, ConfigDict
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
    
    # Dual database support: default to local sqlite+aiosqlite for zero-friction run,
    # or postgresql+asyncpg for production / Supabase.
    DATABASE_URL: str = "sqlite+aiosqlite:///./gaadilelo.db"
    
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Supabase Integrations (optional for local, used when connecting to live Supabase)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Notification Providers
    SMS_PROVIDER: str = "mock"
    EMAIL_PROVIDER: str = "mock"
    WHATSAPP_ENABLED: bool = False
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings()
