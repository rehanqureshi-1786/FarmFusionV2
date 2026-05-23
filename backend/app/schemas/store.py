from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class StoreProductBase(BaseModel):
    name: str
    category: str
    price: float
    currency: str = "INR"
    stock_quantity: float
    unit: str
    image_url: Optional[str] = None
    description: Optional[str] = None

class StoreProductCreate(StoreProductBase):
    pass

class StoreProductResponse(StoreProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StoreOrderCreate(BaseModel):
    product_id: int
    quantity: float

class StoreOrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    total_price: float
    status: str = "pending"
    created_at: datetime


class StoreRecommendationItem(BaseModel):
    title: str
    subtitle: str
    category: str
    image_url: Optional[str] = None
    shop_url: str


class StoreRecommendationsResponse(BaseModel):
    success: bool
    source: str
    items: List[StoreRecommendationItem]
