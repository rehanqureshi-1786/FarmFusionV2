"""Authentication service."""
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
            
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_tokens(user: User) -> dict:
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 60 * 60
        }

    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
