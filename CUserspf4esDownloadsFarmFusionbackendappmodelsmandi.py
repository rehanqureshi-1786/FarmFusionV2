"""
Mandi (market) prices model.
"""
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MandiPrice(Base):
    __tablename__ = "mandi_prices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Market Details
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    market: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    
    # Commodity Details
    commodity: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    variety: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Prices (in INR per quintal)
    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    modal_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Date
    price_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    
    # Source
    source: Mapped[str] = mapped_column(String(100), default="Agmarknet")
    
    # Timestamps
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # API metadata
    external_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
