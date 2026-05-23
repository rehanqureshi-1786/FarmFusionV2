from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class MarketListingBase(BaseModel):
    crop_name: str
    quantity: float
    unit: str = "Quintal"
    price_per_unit: float
    image_url: Optional[str] = None
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    description: Optional[str] = None

class MarketListingCreate(MarketListingBase):
    pass

class MarketListingUpdate(BaseModel):
    crop_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    price_per_unit: Optional[float] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class MarketListingResponse(MarketListingBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MarketListingSearch(BaseModel):
    query: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = 50.0
    crop_filter: Optional[str] = None
