from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional
import hashlib
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import (
    get_password_hash, verify_password, create_access_token, decode_access_token,
    create_password_reset_token, decode_password_reset_token,
    create_email_verification_token, decode_email_verification_token
)
from backend.app.core.rate_limiter import rate_limit
from backend.app.models.models import User, UserProfile, Dealer, City, AuthToken, RevokedToken
from backend.app.schemas.schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse, UserProfileUpdate,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest
)
from backend.app.services.email_service import EmailService
from backend.app.api.deps import get_current_user, get_current_user_optional, security_scheme

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit(max_requests=5, window_seconds=60, key_prefix="register"))]
)
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if email or phone already registered
    existing_email = await db.execute(select(User).where(User.email == payload.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    existing_phone = await db.execute(select(User).where(User.phone == payload.phone))
    if existing_phone.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="An account with this phone number already exists")

    # If dealer registration, gstin must be unique
    if payload.role == "DEALER":
        if not payload.gstin or not payload.dealership_name or not payload.city_id:
            raise HTTPException(
                status_code=400,
                detail="Dealership name, GSTIN, and city are mandatory for dealer registration"
            )
        existing_gstin = await db.execute(select(Dealer).where(Dealer.gstin == payload.gstin))
        if existing_gstin.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="This GSTIN is already registered")

    # Create user
    user = User(
        email=payload.email,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_active=True,
        is_verified=(payload.role == "BUYER") # Buyers verified by default, Dealers require admin approval
    )
    db.add(user)
    await db.flush()

    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        full_name=payload.full_name,
        city_id=payload.city_id,
        communication_consent=True
    )
    db.add(profile)

    # If dealer, create dealer record
    if payload.role == "DEALER":
        dealer = Dealer(
            user_id=user.id,
            dealership_name=payload.dealership_name,
            legal_entity_name=payload.legal_entity_name or payload.dealership_name,
            gstin=payload.gstin.upper(),
            city_id=payload.city_id,
            address=payload.address or "Indore, Madhya Pradesh",
            authorized_brands=payload.authorized_brands or [],
            verification_status="PENDING"
        )
        db.add(dealer)

    await db.commit()
    await db.refresh(user)

    token = create_access_token(subject=str(user.id), role=user.role)

    user_data = {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "full_name": payload.full_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "city_id": payload.city_id,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

    return TokenResponse(access_token=token, user=user_data)

@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit(max_requests=5, window_seconds=60, key_prefix="login"))]
)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(User)
        .options(selectinload(User.profile), selectinload(User.dealer))
        .where(User.email == payload.email)
    )
    user = res.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")

    token = create_access_token(subject=str(user.id), role=user.role)

    user_data = {
        "id": str(user.id),
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "full_name": user.profile.full_name if user.profile else user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "city_id": str(user.profile.city_id) if (user.profile and user.profile.city_id) else None,
        "dealer": {
            "id": str(user.dealer.id),
            "dealership_name": user.dealer.dealership_name,
            "verification_status": user.dealer.verification_status
        } if user.dealer else None
    }

    return TokenResponse(access_token=token, user=user_data)

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "profile": {
            "full_name": current_user.profile.full_name if current_user.profile else "",
            "city_id": str(current_user.profile.city_id) if (current_user.profile and current_user.profile.city_id) else None,
            "preferred_language": current_user.profile.preferred_language if current_user.profile else "en",
            "communication_consent": current_user.profile.communication_consent if current_user.profile else True
        } if current_user.profile else None,
        "dealer": {
            "id": str(current_user.dealer.id),
            "dealership_name": current_user.dealer.dealership_name,
            "gstin": current_user.dealer.gstin,
            "verification_status": current_user.dealer.verification_status,
            "authorized_brands": current_user.dealer.authorized_brands
        } if current_user.dealer else None
    }

@router.post("/logout")
async def logout_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if credentials:
        payload = decode_access_token(credentials.credentials)
        if payload and payload.get("jti"):
            jti = payload["jti"]
            exp = payload.get("exp")
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc) + timedelta(days=1)
            
            # Record token revocation
            revoked = RevokedToken(
                jti=jti,
                user_id=current_user.id,
                revoked_at=datetime.now(timezone.utc),
                expires_at=expires_at
            )
            db.add(revoked)
            await db.commit()

    return {"message": "Successfully logged out. Session has been revoked.", "status": "LOGGED_OUT"}

@router.put("/profile")
async def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.profile:
        if payload.full_name is not None:
            current_user.profile.full_name = payload.full_name
        if payload.city_id is not None:
            current_user.profile.city_id = payload.city_id
        if payload.preferred_language is not None:
            current_user.profile.preferred_language = payload.preferred_language
        if payload.communication_consent is not None:
            current_user.profile.communication_consent = payload.communication_consent

    if payload.phone is not None:
        current_user.phone = payload.phone

    await db.commit()
    return {"message": "Profile updated successfully"}

@router.post(
    "/forgot-password",
    dependencies=[Depends(rate_limit(max_requests=3, window_seconds=60, key_prefix="forgot_password"))]
)
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .where(User.email == payload.email)
    )
    user = res.scalar_one_or_none()

    if not user:
        # Prevent user enumeration by returning standard positive response
        return {
            "message": "If an account with this email exists, password reset instructions have been sent.",
            "status": "SENT"
        }

    token = create_password_reset_token(email=user.email, user_id=user.id)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    auth_tok = AuthToken(
        user_id=user.id,
        token_type="PASSWORD_RESET",
        token_hash=token_hash,
        expires_at=expires_at,
        is_used=False
    )
    db.add(auth_tok)
    await db.commit()

    # Dispatch email
    user_name = user.profile.full_name if user.profile else user.email
    await EmailService.send_password_reset_email(to_email=user.email, token=token, user_name=user_name)

    # In production, do NOT expose the raw reset token or reset URL in the response
    if settings.ENVIRONMENT.lower() == "production":
        return {
            "message": "If an account with this email exists, password reset instructions have been sent.",
            "status": "SENT"
        }

    # In local development and testing, return the self-service reset token URL
    reset_url = f"/reset-password?token={token}"
    return {
        "message": "Password reset instructions generated successfully.",
        "status": "SENT",
        "reset_token": token,
        "reset_url": reset_url
    }

@router.post(
    "/reset-password",
    dependencies=[Depends(rate_limit(max_requests=5, window_seconds=60, key_prefix="reset_password"))]
)
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    data = decode_password_reset_token(payload.token)
    if not data or not data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password reset link is invalid or has expired. Please request a new one."
        )

    user_id = data["sub"]
    token_hash = hashlib.sha256(payload.token.encode("utf-8")).hexdigest()

    # Verify single-use token in auth_tokens
    token_res = await db.execute(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash,
            AuthToken.token_type == "PASSWORD_RESET"
        )
    )
    auth_tok = token_res.scalar_one_or_none()
    if auth_tok:
        if auth_tok.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This password reset token has already been used. Please request a new one."
            )
        auth_tok.is_used = True

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    user.password_hash = get_password_hash(payload.new_password)
    await db.commit()

    return {
        "message": "Your password has been successfully reset. You may now log in with your new credentials.",
        "status": "SUCCESS"
    }

@router.post(
    "/request-verification-email",
    dependencies=[Depends(rate_limit(max_requests=3, window_seconds=60, key_prefix="request_verification"))]
)
async def request_verification_email(
    payload: Optional[ForgotPasswordRequest] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    user = None
    if current_user:
        user = current_user
    elif payload and payload.email:
        res = await db.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.email == payload.email)
        )
        user = res.scalar_one_or_none()

    if not user:
        return {
            "message": "If an account with this email exists, verification instructions have been sent.",
            "status": "SENT"
        }

    token = create_email_verification_token(email=user.email, user_id=user.id)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=2)
    auth_tok = AuthToken(
        user_id=user.id,
        token_type="EMAIL_VERIFICATION",
        token_hash=token_hash,
        expires_at=expires_at,
        is_used=False
    )
    db.add(auth_tok)
    await db.commit()

    user_name = user.profile.full_name if user.profile else user.email
    await EmailService.send_verification_email(to_email=user.email, token=token, user_name=user_name)

    if settings.ENVIRONMENT.lower() == "production":
        return {
            "message": "If an account with this email exists, verification instructions have been sent.",
            "status": "SENT"
        }

    return {
        "message": "Verification instructions generated successfully.",
        "status": "SENT",
        "verification_token": token,
        "verification_url": f"/verify-email?token={token}"
    }

@router.get("/verify-email")
@router.post(
    "/verify-email",
    dependencies=[Depends(rate_limit(max_requests=5, window_seconds=60, key_prefix="verify_email"))]
)
async def verify_email(
    token: Optional[str] = None,
    payload: Optional[VerifyEmailRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    token_str = token or (payload.token if payload else None)
    if not token_str:
        raise HTTPException(status_code=400, detail="Verification token is required")

    data = decode_email_verification_token(token_str)
    if not data or not data.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is invalid or has expired."
        )

    user_id = data["sub"]
    token_hash = hashlib.sha256(token_str.encode("utf-8")).hexdigest()

    # Verify single-use token in auth_tokens
    token_res = await db.execute(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash,
            AuthToken.token_type == "EMAIL_VERIFICATION"
        )
    )
    auth_tok = token_res.scalar_one_or_none()
    if auth_tok:
        if auth_tok.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This verification token has already been used."
            )
        auth_tok.is_used = True

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    await db.commit()

    return {
        "message": "Email address verified successfully. Your account is active.",
        "status": "VERIFIED"
    }

