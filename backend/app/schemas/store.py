from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class StoreProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

    model_config = ConfigDict(extra='ignore')


class StoreProductCreate(StoreProductBase):
    pass


class StoreProductResponse(StoreProductBase):
    id: int
    available: bool
    created_at: Optional[datetime] = None


class StoreOrderCreate(BaseModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(extra='ignore')


class StoreOrderResponse(BaseModel):
    order_id: int
    success: bool


class StoreRecommendationItem(BaseModel):
    name: str
    url: str
    price: float


class StoreRecommendationsResponse(BaseModel):
    recommendations: List[StoreRecommendationItem]
