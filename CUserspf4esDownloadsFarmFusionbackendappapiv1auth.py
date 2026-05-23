"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    TokenRefresh,
    UserUpdate,
    PasswordChange,
    MessageResponse
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if email exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token."""
    user = await AuthService.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await AuthService.update_last_login(db, user)
    
    # Create tokens
    tokens = await AuthService.create_tokens(user)
    
    return Token(
        **tokens,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    tokens = await AuthService.refresh_access_token(token_data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user for response
    payload = AuthService.decode_token(tokens["access_token"])
    user = await AuthService.get_user_by_id(db, int(payload["sub"]))
    
    return Token(
        **tokens,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    updated_user = await AuthService.update_user(db, current_user, user_data)
    return updated_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    success = await AuthService.change_password(
        db,
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return MessageResponse(message="Password changed successfully")
