"""
Animal detection model.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AnimalDetection(Base):
    __tablename__ = "animal_detections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Detection Details
    animal_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "wild_boar", "elephant"
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 to 1.0
    
    # Image
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Location
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Detection Metadata
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Alert Status
    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Threat Level
    threat_level: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
