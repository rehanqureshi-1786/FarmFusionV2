"""
SQLAlchemy ORM models for Mandi Price Intelligence and Opportunity Alerts.
"""
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MandiPriceAlert(Base):
    """User-defined price trigger condition for agricultural commodities."""
    __tablename__ = "mandi_price_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True, default="default_user", nullable=False)
    commodity: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    market: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    target_price: Mapped[float] = mapped_column(Float, nullable=True)
    direction: Mapped[str] = mapped_column(String(20), default="ABOVE", nullable=False)  # ABOVE or BELOW
    target_percentage_change: Mapped[float] = mapped_column(Float, nullable=True)
    base_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True, nullable=False)  # ACTIVE, TRIGGERED, CANCELLED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_mandi_alerts_user_commodity", "user_id", "commodity", "status"),
    )
