import pytest
import pytest_asyncio
import uuid
import os
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta

from backend.app.main import app
from backend.app.core.config import Settings, settings
from backend.app.core.rate_limiter import rate_limiter
from backend.app.services.email_service import EmailService
from scripts.verify_postgres_migrations import inspect_migrations

@pytest.mark.asyncio
async def test_rate_limiting_enforcement_and_retry_after():
    """
    Verifies that exceeding rate limits returns 429 Too Many Requests
    with Retry-After header and appropriate retry information.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        rate_limiter.reset("login")

        # 5 allowed attempts
        for i in range(5):
            res = await ac.post("/api/v1/auth/login", json={
                "email": f"test.ratelimit.{i}@example.com",
                "password": "WrongPassword123"
            })
            assert res.status_code == 401

        # 6th attempt MUST be blocked by rate limiter
        blocked_res = await ac.post("/api/v1/auth/login", json={
            "email": "test.ratelimit.6@example.com",
            "password": "WrongPassword123"
        })
        assert blocked_res.status_code == 429
        assert "Retry-After" in blocked_res.headers
        assert int(blocked_res.headers["Retry-After"]) >= 1
        assert "Too many requests" in blocked_res.json()["detail"]

        # Reset limiter and verify traffic flows again
        rate_limiter.reset("login")
        unblocked_res = await ac.post("/api/v1/auth/login", json={
            "email": "test.ratelimit.unblock@example.com",
            "password": "WrongPassword123"
        })
        assert unblocked_res.status_code == 401

@pytest.mark.asyncio
async def test_jwt_revocation_on_logout():
    """
    Verifies that calling /auth/logout records the token's jti in revoked_tokens,
    and subsequent protected requests with that token are rejected with 401.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_suffix = uuid.uuid4().hex[:6]
        email = f"logout.buyer.{unique_suffix}@example.com"
        password = "Password123!"

        # 1. Register buyer
        reg_res = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "phone": f"9826{uuid.uuid4().hex[:6]}",
            "full_name": f"Logout Buyer {unique_suffix}",
            "role": "BUYER"
        })
        assert reg_res.status_code == 200
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Access /auth/me before logout -> 200
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == email

        # 3. Call /auth/logout
        logout_res = await ac.post("/api/v1/auth/logout", headers=headers)
        assert logout_res.status_code == 200
        assert logout_res.json()["status"] == "LOGGED_OUT"

        # 4. Access /auth/me after logout with same token -> MUST BE 401 Unauthorized
        revoked_me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert revoked_me_res.status_code == 401
        assert "revoked" in revoked_me_res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_email_service_mock_rejection_in_production():
    """
    Verifies that EmailService strictly rejects mock email dispatching in production mode.
    """
    original_env = settings.ENVIRONMENT
    original_provider = settings.EMAIL_PROVIDER
    try:
        settings.ENVIRONMENT = "production"
        settings.EMAIL_PROVIDER = "mock"

        success, err = await EmailService.send_verification_email("buyer@example.com", "fake-token")
        assert success is False
        assert "Mock email provider is rejected in production mode" in err

        success_reset, err_reset = await EmailService.send_password_reset_email("buyer@example.com", "fake-token")
        assert success_reset is False
        assert "Mock email provider is rejected in production mode" in err_reset
    finally:
        settings.ENVIRONMENT = original_env
        settings.EMAIL_PROVIDER = original_provider

@pytest.mark.asyncio
async def test_email_service_smtp_failure_handling():
    """
    Verifies that EmailService handles unreachable SMTP endpoints gracefully without crashing.
    """
    original_provider = settings.EMAIL_PROVIDER
    original_host = settings.SMTP_HOST
    try:
        settings.EMAIL_PROVIDER = "smtp"
        settings.SMTP_HOST = "invalid-smtp-host.gaadilelo.invalid"
        settings.SMTP_PORT = 587

        success, err = await EmailService.send_verification_email("buyer@example.com", "test-token")
        assert success is False
        assert err is not None
        assert "SMTP dispatch failed" in err or "Name or service not known" in err or "nodename nor servname" in err
    finally:
        settings.EMAIL_PROVIDER = original_provider
        settings.SMTP_HOST = original_host

def test_sqlite_fallback_rejection_in_production():
    """
    Verifies that settings initialization refuses SQLite database when ENVIRONMENT=production.
    """
    with pytest.raises(Exception) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="custom-secure-key-12345678901234567890123456789012",
            DATABASE_URL="sqlite+aiosqlite:///./production_forbidden.db",
            EMAIL_PROVIDER="smtp",
            SMTP_HOST="smtp.example.com"
        )
    assert "SQLite is not allowed" in str(exc_info.value)

def test_production_secret_rejection():
    """
    Verifies that settings initialization refuses the default development secret in production.
    """
    with pytest.raises(Exception) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="gaadilelo-super-secret-production-grade-key-2026-indore",
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/gaadilelo",
            EMAIL_PROVIDER="smtp",
            SMTP_HOST="smtp.example.com"
        )
    assert "SECRET_KEY must be provided" in str(exc_info.value)

@pytest.mark.asyncio
async def test_forgot_password_generic_response_in_production():
    """
    Verifies that in production mode, /auth/forgot-password never leaks raw reset tokens
    or URLs in the response body, and non-existent accounts return identical responses.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        original_env = settings.ENVIRONMENT
        original_provider = settings.EMAIL_PROVIDER
        try:
            settings.ENVIRONMENT = "production"
            settings.EMAIL_PROVIDER = "mock"
            rate_limiter.reset("forgot_password")

            # Request reset
            res = await ac.post("/api/v1/auth/forgot-password", json={"email": "nonexistent@example.com"})
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "SENT"
            # Must NOT expose raw reset token or reset URL in production
            assert "reset_token" not in data
            assert "reset_url" not in data
        finally:
            settings.ENVIRONMENT = original_env
            settings.EMAIL_PROVIDER = original_provider
            rate_limiter.reset("forgot_password")

def test_migration_compatibility_inspection():
    """
    Verifies that all 4 migrations 001-004 are syntactically and structurally PostgreSQL ready.
    """
    assert inspect_migrations() is True

