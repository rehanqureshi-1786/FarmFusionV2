from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class CropCycleBase(BaseModel):
    crop_name: str
    sowing_date: datetime
    farm_id: Optional[int] = None
    predicted_harvest_date: Optional[datetime] = None

class CropCycleCreate(CropCycleBase):
    pass

class CropCycleUpdate(BaseModel):
    status: Optional[str] = None
    predicted_harvest_date: Optional[datetime] = None
    notes: Optional[str] = None

class CropCycleResponse(CropCycleBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
