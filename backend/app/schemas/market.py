from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MarketPriceResponse(BaseModel):
    state: str
    district: Optional[str] = None
    market: str
    commodity: str
    variety: str
    grade: str
    arrival_date: Optional[str] = None
    min_price: float
    max_price: float
    modal_price: float
    source: Optional[str] = None


class MarketPriceListResponse(BaseModel):
    data: List[MarketPriceResponse]
    count: int
    region: str


class PricePredictionPoint(BaseModel):
    date: str
    predicted_price: float


class MarketPredictionRequest(BaseModel):
    commodity: str
    region: Optional[str] = None


class MarketPredictionResponse(BaseModel):
    commodity: str
    prediction: float
    history: Optional[List[PricePredictionPoint]] = None
