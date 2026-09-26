from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, generate_otp, otp_expiry
from app.models.user import User, OTPToken
from app.schemas.user import UserCreate, UserOut, Token, LoginRequest, OTPRequest, OTPVerify
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account is inactive")
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/forgot-password")
async def forgot_password(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        # Return 200 even if user not found — don't leak whether email exists
        return {"message": "If that email exists, an OTP has been sent."}

    otp = generate_otp()
    hashed = hash_password(otp)  # store OTP as bcrypt hash
    token = OTPToken(user_id=user.id, hashed_otp=hashed, expires_at=otp_expiry())
    db.add(token)
    await db.commit()

    # In production: send otp via email. For hackathon: log to console.
    print(f"\n[OTP] User: {user.email} | OTP: {otp} | Expires: {token.expires_at}\n")
    return {"message": "If that email exists, an OTP has been sent.", "otp_debug": otp}


@router.post("/reset-password")
async def reset_password(data: OTPVerify, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(400, "Invalid request")

    # Find valid, unused OTP token
    tokens_result = await db.execute(
        select(OTPToken).where(
            OTPToken.user_id == user.id,
            OTPToken.used == False,  # noqa: E712
            OTPToken.expires_at > datetime.now(timezone.utc),
        ).order_by(OTPToken.created_at.desc())
    )
    tokens = tokens_result.scalars().all()

    valid_token = None
    for t in tokens:
        if verify_password(data.otp, t.hashed_otp):
            valid_token = t
            break

    if not valid_token:
        raise HTTPException(400, "Invalid or expired OTP")

    valid_token.used = True
    user.hashed_password = hash_password(data.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
