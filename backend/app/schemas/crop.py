from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.crop import CropStatus, SoilType


class CropBase(BaseModel):
    name: str
    soil_type: SoilType
    location: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class CropCreate(CropBase):
    pass


class CropUpdate(CropBase):
    status: Optional[CropStatus] = None


class CropResponse(CropBase):
    id: int
    status: CropStatus
    created_at: Optional[datetime] = None


class CropRecommendationRequest(BaseModel):
    crop_name: str
    soil_type: SoilType


class CropRecommendation(BaseModel):
    recommendation: str


class CropRecommendationResponse(BaseModel):
    crop_name: str
    recommendations: List[CropRecommendation]


class CropRecommendRequest(CropRecommendationRequest):
    pass


class CropRecommendResponse(CropRecommendationResponse):
    pass
