from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MarketPriceResponse(BaseModel):
    commodity: str
    price: float
    mandi: Optional[str] = None
    created_at: Optional[datetime] = None


class MarketPriceListResponse(BaseModel):
    prices: List[MarketPriceResponse]


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
