from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MarketListingBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    location: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class MarketListingCreate(MarketListingBase):
    pass


class MarketListingUpdate(MarketListingBase):
    id: int


class MarketListingResponse(MarketListingBase):
    id: int


class MarketListingSearch(BaseModel):
    query: str
