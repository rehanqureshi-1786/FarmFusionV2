from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class MarketPriceResponse(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    grade: str
    arrival_date: str
    min_price: float
    max_price: float
    modal_price: float
    source: str = "CSV Dataset"

    model_config = ConfigDict(from_attributes=True)

class MarketPriceListResponse(BaseModel):
    data: List[MarketPriceResponse]
    count: int
    region: str

class PricePredictionPoint(BaseModel):
    month: str
    predicted_price: float
    trend: str
    confidence: float

class MarketPredictionRequest(BaseModel):
    commodity: str
    state: str
    district: Optional[str] = None
    current_price: Optional[float] = None
    prediction_months: int = 3

class MarketPredictionResponse(BaseModel):
    commodity: str
    region: str
    current_price: float
    predictions: List[PricePredictionPoint]
    best_time_to_sell: str
    ai_analysis: str
    source: str
