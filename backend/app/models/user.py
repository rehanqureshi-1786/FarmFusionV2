from __future__ import annotations

from enum import Enum
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, Enum):
    farmer = "farmer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firebase_uid: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(64), nullable=True)
    language_preference: Mapped[str] = mapped_column(String(32), nullable=True, default="en")
    role: Mapped[UserRole] = mapped_column(String(32), nullable=False, default=UserRole.farmer)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    farms = relationship("Farm", back_populates="user")
