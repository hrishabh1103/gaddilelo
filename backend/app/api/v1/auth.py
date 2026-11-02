from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.models.models import User, UserProfile, Dealer, City
from backend.app.schemas.schemas import UserRegister, UserLogin, TokenResponse, UserResponse, UserProfileUpdate
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
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

    token = create_access_token(subject=user.id, role=user.role)

    user_data = {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "full_name": payload.full_name,
        "is_verified": user.is_verified
    }

    return TokenResponse(access_token=token, user=user_data)

@router.post("/login", response_model=TokenResponse)
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

    token = create_access_token(subject=user.id, role=user.role)

    user_data = {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "full_name": user.profile.full_name if user.profile else user.email,
        "is_verified": user.is_verified,
        "city_id": user.profile.city_id if user.profile else None,
        "dealer": {
            "id": user.dealer.id,
            "dealership_name": user.dealer.dealership_name,
            "verification_status": user.dealer.verification_status
        } if user.dealer else None
    }

    return TokenResponse(access_token=token, user=user_data)

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "profile": {
            "full_name": current_user.profile.full_name if current_user.profile else "",
            "city_id": current_user.profile.city_id if current_user.profile else None,
            "preferred_language": current_user.profile.preferred_language if current_user.profile else "en",
            "communication_consent": current_user.profile.communication_consent if current_user.profile else True
        } if current_user.profile else None,
        "dealer": {
            "id": current_user.dealer.id,
            "dealership_name": current_user.dealer.dealership_name,
            "gstin": current_user.dealer.gstin,
            "verification_status": current_user.dealer.verification_status,
            "authorized_brands": current_user.dealer.authorized_brands
        } if current_user.dealer else None
    }

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

