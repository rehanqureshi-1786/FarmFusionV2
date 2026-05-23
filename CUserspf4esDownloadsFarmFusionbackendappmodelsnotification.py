"""
Notification model for alerts and messages.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, Text, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, enum.Enum):
    IRRIGATION_ALERT = "irrigation_alert"
    PRICE_ALERT = "price_alert"
    WEATHER_ALERT = "weather_alert"
    LABOUR_UPDATE = "labour_update"
    ORDER_UPDATE = "order_update"
    ANIMAL_DETECTION = "animal_detection"
    GENERAL = "general"


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    IN_APP = "in_app"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Notification Details
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel), default=NotificationChannel.IN_APP)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Data payload for deep linking
    data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
