"""
SQLAlchemy ORM models for IoT Animal Intrusion Detection System.
"""
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnimalDetection(Base):
    """Event history for detected and cleared animal intrusions."""
    __tablename__ = "animal_detections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    sensor: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # IR or PIR
    status: Mapped[str] = mapped_column(String(20), nullable=False)       # detected or cleared
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )

    __table_args__ = (
        Index("ix_animal_detections_device_timestamp", "device_id", "timestamp"),
    )


class DeviceStatus(Base):
    """Latest heartbeat and online health status per IoT node device."""
    __tablename__ = "device_status"

    device_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SensorStatus(Base):
    """Granular latest status and telemetry per sensor on each IoT node."""
    __tablename__ = "sensor_status"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    sensor: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # IR or PIR
    status: Mapped[str] = mapped_column(String(20), nullable=False)       # detected or cleared
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("device_id", "sensor", name="uq_device_sensor"),
    )
