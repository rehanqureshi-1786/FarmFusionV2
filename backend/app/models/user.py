"""User model."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.crop import Crop


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    LABOR = "labor"
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.FARMER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    village: Mapped[str] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str] = mapped_column(String(10), nullable=True)
    
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
