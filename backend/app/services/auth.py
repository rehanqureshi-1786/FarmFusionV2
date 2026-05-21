from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, Token, TokenRefresh, UserResponse


class AuthService:
    @staticmethod
    async def get_user_by_email(email: str, db: Optional[AsyncSession]):
        if db is None:
            return None
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(user_data: UserCreate, db: AsyncSession) -> UserResponse:
        hashed_password = get_password_hash(user_data.password)
        user = User(
            firebase_uid="",
            email=user_data.email,
            name=user_data.name or "",
            phone_number=user_data.phone_number or "",
            language_preference=user_data.language_preference,
            hashed_password=hashed_password,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserResponse(
            id=user.id,
            firebase_uid=user.firebase_uid,
            email=user.email,
            name=user.name,
            phone_number=user.phone_number,
            language_preference=user.language_preference,
            created_at=user.created_at,
        )

    @staticmethod
    async def login(email: str, password: str, db: AsyncSession) -> Optional[Token]:
        user = await AuthService.get_user_by_email(email, db)
        if not user or not verify_password(password, user.hashed_password or ""):
            return None
        access_token = create_access_token({"sub": user.email})
        refresh_token = create_refresh_token({"sub": user.email})
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def refresh_token(refresh_token: str) -> Optional[TokenRefresh]:
        decoded = decode_token(refresh_token)
        if not decoded or "sub" not in decoded:
            return None
        new_token = create_refresh_token({"sub": decoded["sub"]})
        return TokenRefresh(refresh_token=new_token)
