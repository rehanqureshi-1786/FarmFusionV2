"""
Pydantic Models - Define the shape of data for API requests and responses
Think of these as "data contracts" between Android app and backend
"""
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


# ============ CROP RECOMMENDATION ============

class SoilType(str, Enum):
    """Enum for soil types - ensures only valid values are accepted"""
    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILTY = "silty"
    PEATY = "peaty"


class CropRecommendRequest(BaseModel):
    """Data sent FROM Android app TO backend when requesting crop recommendation"""
    location: str  # e.g., "Nairobi, Kenya" or "Jaipur, Rajasthan"
    soil_type: str = "loamy"
    rainfall_mm: float = -1.0  # Annual rainfall in millimeters (-1 for auto-fetch)
    temperature_c: float = 25.0  # Average temperature in Celsius
    farm_size_acres: float = 1.0
    budget_usd: Optional[float] = None
    preferred_language: str = "en"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None


class CropRecommendation(BaseModel):
    """A single crop recommendation"""
    crop_name: str
    confidence_score: float  # 0.0 to 1.0
    expected_yield_tons: float
    market_demand: str  # "high", "medium", "low"
    estimated_profit_usd: float
    growing_duration_months: int
    water_requirement: str  # "low", "medium", "high"


class CropRecommendResponse(BaseModel):
    """Data sent BACK TO Android app from backend"""
    success: bool
    recommendations: List[CropRecommendation]
    ai_insights: str  # Natural language advice from AI
    timestamp: str


# ============ DISEASE DETECTION ============

class DiseaseDetectResponse(BaseModel):
    """Response for disease detection"""
    success: bool
    disease_name: Optional[str]
    confidence: float
    description: str
    treatment_suggestions: List[str]
    prevention_tips: List[str]
    severity: str  # "low", "medium", "high", "critical"


# ============ MARKET PREDICTION ============

class MarketPredictionRequest(BaseModel):
    """Request for market price prediction"""
    crop_name: str
    region: str
    prediction_months: int = 3  # How many months ahead to predict


class MarketPrice(BaseModel):
    """Price prediction for a specific time period"""
    month: str
    predicted_price_per_kg: float
    price_trend: str  # "rising", "falling", "stable"
    confidence: float


class MarketPredictionResponse(BaseModel):
    """Response with market predictions"""
    success: bool
    crop_name: str
    current_price_per_kg: float
    predictions: List[MarketPrice]
    ai_analysis: str
    best_time_to_sell: str


# ============ COMMON RESPONSES ============

class HealthCheckResponse(BaseModel):
    """Simple health check response"""
    status: str
    message: str
    version: str = "1.0.0"