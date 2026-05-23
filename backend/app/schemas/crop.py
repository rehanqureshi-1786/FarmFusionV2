"""Crop schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.crop import SoilType, CropStatus


class CropBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    variety: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    area_hectares: float = Field(..., gt=0)


class CropCreate(CropBase):
    sowing_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    expected_yield_quintals: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = None


class CropUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[CropStatus] = None
    expected_yield_quintals: Optional[float] = Field(None, gt=0)
    actual_yield_quintals: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class CropResponse(CropBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    owner_id: int
    status: CropStatus
    sowing_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    actual_harvest_date: Optional[datetime] = None
    expected_yield_quintals: Optional[float] = None
    actual_yield_quintals: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class CropRecommendationRequest(BaseModel):
    soil_type: SoilType
    ph_level: float = Field(..., ge=0, le=14)
    season: str
    state: str


class CropRecommendation(BaseModel):
    crop_name: str
    confidence: float
    description: str
    expected_yield: str


class CropRecommendationResponse(BaseModel):
    recommendations: list[CropRecommendation]
