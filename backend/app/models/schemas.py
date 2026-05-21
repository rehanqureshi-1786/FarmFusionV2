from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


class SoilType(str, Enum):
    clay = "clay"
    sandy = "sandy"
    loamy = "loamy"
    silty = "silty"
    peaty = "peaty"


class CropRecommendRequest(BaseModel):
    crop_name: str
    soil_type: SoilType
    location: Optional[str] = None


class CropRecommendation(BaseModel):
    recommendation: str


class CropRecommendResponse(BaseModel):
    crop_name: str
    recommendations: List[CropRecommendation]


class DiseaseDetectResponse(BaseModel):
    disease: str
    confidence: float


class MarketPredictionRequest(BaseModel):
    commodity: str
    region: Optional[str] = None


class MarketPrice(BaseModel):
    commodity: str
    price: float


class MarketPredictionResponse(BaseModel):
    commodity: str
    prediction: float


class HealthCheckResponse(BaseModel):
    status: str
    version: str
