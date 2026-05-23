"""
Product store and marketplace models.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class ProductCategory(str, enum.Enum):
    SEEDS = "seeds"
    FERTILIZERS = "fertilizers"
    PESTICIDES = "pesticides"
    TOOLS = "tools"
    MACHINERY = "machinery"
    ORGANIC = "organic"
    OTHER = "other"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Product Details
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Pricing
    price: Mapped[float] = mapped_column(Float, nullable=False)  # in INR
    unit: Mapped[str] = mapped_column(String(50), default="piece")  # kg, liter, piece, etc.
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    
    # Images
    image_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of URLs
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Location
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    
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


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Order Details
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Shipping Address
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    shipping_state: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Payment
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(50), default="pending")
    
    # Tracking
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
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
    buyer: Mapped["User"] = relationship("User", back_populates="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
