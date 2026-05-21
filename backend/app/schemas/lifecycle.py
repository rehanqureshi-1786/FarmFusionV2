from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CropCycleBase(BaseModel):
    farm_id: int
    current_stage: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class CropCycleCreate(CropCycleBase):
    pass


class CropCycleUpdate(CropCycleBase):
    pass


class CropCycleResponse(CropCycleBase):
    id: int
    status: str
    created_at: Optional[datetime] = None
