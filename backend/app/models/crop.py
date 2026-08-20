"""Crop models."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class SoilType(str, enum.Enum):
    SANDY = "sandy"
    CLAY = "clay"
    SILTY = "silty"
    LOAMY = "loamy"
    PEATY = "peaty"


class CropStatus(str, enum.Enum):
    PLANNED = "planned"
    SOWN = "sown"
    GROWING = "growing"
    FLOWERING = "flowering"
    READY = "ready"
    HARVESTED = "harvested"


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    variety: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    
    status: Mapped[CropStatus] = mapped_column(Enum(CropStatus), default=CropStatus.PLANNED)
    
    sowing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_harvest_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_yield_quintals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_yield_quintals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
