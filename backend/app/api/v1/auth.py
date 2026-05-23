"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    Token, 
    TokenRefresh, 
    PasswordChange,
    UserData,
    AuthResponse
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    await AuthService.update_last_login(db, user)
    tokens = await AuthService.create_tokens(user)
    return Token(**tokens)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/verify", response_model=AuthResponse)
async def verify_auth_token(
    firebase_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify Firebase token and return/create user.
    """
    # For now, simulate successful verification and return a dummy user
    # In production, use firebase_admin to verify the token
    return AuthResponse(
        success=True,
        message="Token verified successfully",
        user=UserData(
            id=1,
            firebase_uid="dummy_uid",
            phone_number="+919876543210",
            name="FarmFusion User",
            email="farmer@farmfusion.com",
            language_preference="hi"
        )
    )
