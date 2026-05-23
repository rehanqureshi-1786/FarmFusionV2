"""
Crop and soil-related models.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SoilType(str, enum.Enum):
    SANDY = "sandy"
    CLAY = "clay"
    SILTY = "silty"
    PEATY = "peaty"
    LOAMY = "loamy"
    CHALKY = "chalky"


class CropStatus(str, enum.Enum):
    PLANNED = "planned"
    SOWN = "sown"
    GROWING = "growing"
    FLOWERING = "flowering"
    READY = "ready"
    HARVESTED = "harvested"


class SoilReport(Base):
    __tablename__ = "soil_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Soil Test Results
    ph_level: Mapped[float] = mapped_column(Float, nullable=False)
    nitrogen: Mapped[float] = mapped_column(Float, nullable=False)  # kg/ha
    phosphorus: Mapped[float] = mapped_column(Float, nullable=False)  # kg/ha
    potassium: Mapped[float] = mapped_column(Float, nullable=False)  # kg/ha
    organic_matter: Mapped[float] = mapped_column(Float, nullable=True)
    soil_type: Mapped[SoilType] = mapped_column(Enum(SoilType), nullable=False)
    
    # Location
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Report File
    report_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Crop Details
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    variety: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # cereals, pulses, etc.
    
    # Land Details
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    soil_report_id: Mapped[Optional[int]] = mapped_column(ForeignKey("soil_reports.id"), nullable=True)
    
    # Status
    status: Mapped[CropStatus] = mapped_column(Enum(CropStatus), default=CropStatus.PLANNED)
    
    # Dates
    sowing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_harvest_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_harvest_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Yield
    expected_yield_quintals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_yield_quintals: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="crops")
