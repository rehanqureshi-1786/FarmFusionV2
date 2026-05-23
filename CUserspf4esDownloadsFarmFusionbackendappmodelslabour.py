"""
Labour services models.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class LabourType(str, enum.Enum):
    HARVESTING = "harvesting"
    SOWING = "sowing"
    WEEDING = "weeding"
    IRRIGATION = "irrigation"
    PEST_CONTROL = "pest_control"
    OTHER = "other"


class LabourStatus(str, enum.Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LabourRequest(Base):
    __tablename__ = "labour_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Labour Details
    labour_type: Mapped[LabourType] = mapped_column(Enum(LabourType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Location
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Work Details
    workers_needed: Mapped[int] = mapped_column(Integer, default=1)
    wage_per_day: Mapped[float] = mapped_column(Float, nullable=False)  # in INR
    duration_days: Mapped[int] = mapped_column(Integer, default=1)
    
    # Dates
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    status: Mapped[LabourStatus] = mapped_column(Enum(LabourStatus), default=LabourStatus.OPEN)
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Requirements
    requires_experience: Mapped[bool] = mapped_column(Boolean, default=False)
    skills_required: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
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
    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id], back_populates="labour_requests")
    worker: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])
