"""User model."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base

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
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.FARMER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    village: Mapped[str] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str] = mapped_column(String(10), nullable=True)
    
    preferred_language: Mapped[str] = mapped_column(String(10), default="hi")
    consent_voice_storage: Mapped[bool] = mapped_column(Boolean, default=False)
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

    # Relationships
    farms = relationship("Farm", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    disease_detections = relationship("DiseaseDetection", back_populates="user", cascade="all, delete-orphan")
    listings = relationship("MarketListing", back_populates="seller")
    jobs = relationship("LabourJob", back_populates="poster")
    crop_cycles = relationship("CropCycle", back_populates="user")

    @property
    def name(self) -> str:
        return self.full_name or ""

    @name.setter
    def name(self, val: str):
        self.full_name = val

    @property
    def phone_number(self) -> str:
        return self.phone or ""

    @phone_number.setter
    def phone_number(self, val: str):
        self.phone = val
