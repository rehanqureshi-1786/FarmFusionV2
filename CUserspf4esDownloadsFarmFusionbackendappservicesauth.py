"""
Authentication service layer.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserUpdate, Token


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user by email and password."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
            
        return user

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate
    ) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            hashed_password=hashed_password,
            role=user_data.role,
            state=user_data.state,
            district=user_data.district,
            village=user_data.village,
            pincode=user_data.pincode,
            preferred_language=user_data.preferred_language
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str
    ) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user: User,
        user_data: UserUpdate
    ) -> User:
        """Update user details."""
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)
        
        return user

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password."""
        if not verify_password(current_password, user.hashed_password):
            return False
            
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        
        return True

    @staticmethod
    async def create_tokens(user: User) -> dict:
        """Create access and refresh tokens for user."""
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 60 * 60  # 1 hour in seconds
        }

    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Optional[dict]:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
            
        user_id = int(payload.get("sub"))
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": str(user_id)}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user_id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 60 * 60
        }

    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
