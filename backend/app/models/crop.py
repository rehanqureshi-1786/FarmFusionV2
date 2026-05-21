from __future__ import annotations

from enum import Enum
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, DateTime, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SoilType(str, Enum):
    clay = "clay"
    sandy = "sandy"
    loamy = "loamy"
    silty = "silty"
    peaty = "peaty"


class CropStatus(str, Enum):
    planted = "planted"
    growing = "growing"
    ready = "ready"
    harvested = "harvested"


class Crop(Base):
    __tablename__ = "crops"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[CropStatus] = mapped_column(SqlEnum(CropStatus), nullable=False, default=CropStatus.planted)
    soil_type: Mapped[SoilType] = mapped_column(SqlEnum(SoilType), nullable=False)
    location: Mapped[str] = mapped_column(String(256), nullable=True)
    planted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
