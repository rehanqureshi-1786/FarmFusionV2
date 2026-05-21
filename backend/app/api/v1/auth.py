from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import AuthResponse, UserCreate, UserResponse, Token, TokenRefresh
from app.services.auth import AuthService
from app.services.auth_service import AuthService as FirebaseAuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await AuthService.get_user_by_email(user_create.email, db)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = await AuthService.create_user(user_create, db)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    token = await AuthService.login(form_data.username, form_data.password, db)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return token


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=TokenRefresh)
async def refresh(token: TokenRefresh):
    refreshed = AuthService.refresh_token(token.refresh_token)
    if not refreshed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return refreshed


@router.post("/verify", response_model=AuthResponse)
async def verify(
    firebase_token: str = Query(..., alias="firebase_token"),
    db: AsyncSession = Depends(get_db),
):
    user_data = await FirebaseAuthService.verify_token(firebase_token)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase token")

    uid = user_data.get("uid")
    if not uid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Firebase token missing uid")

    user = await UserService.get_user_by_firebase_uid(uid, db)
    if not user:
        email = user_data.get("email") or ""
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Firebase token missing email")

        user = await UserService.create_user_from_firebase(
            firebase_uid=uid,
            email=email,
            name=user_data.get("name") or user_data.get("displayName"),
            phone_number=user_data.get("phone_number"),
            db=db,
        )

    return AuthResponse(
        success=True,
        message="Token verified",
        user=UserResponse(
            id=user.id,
            firebase_uid=user.firebase_uid,
            email=user.email,
            name=user.name,
            phone_number=user.phone_number,
            language_preference=user.language_preference,
            created_at=user.created_at,
        ),
    )


@router.get("/user/{uid}")
async def get_user_info(uid: str, db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user_by_firebase_uid(uid, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "success": True,
        "user": {
            "uid": user.firebase_uid,
            "phone_number": user.phone_number,
            "email": user.email,
            "name": user.name,
            "photo_url": None,
            "disabled": False,
        },
    }
