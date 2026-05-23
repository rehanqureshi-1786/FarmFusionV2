from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class LabourJobBase(BaseModel):
    title: str
    job_type: str
    wage_amount: float
    wage_period: str = "day"
    workers_needed: int
    latitude: float
    longitude: float
    location_name: Optional[str] = None

class LabourJobCreate(LabourJobBase):
    pass

class LabourJobUpdate(BaseModel):
    title: Optional[str] = None
    job_type: Optional[str] = None
    wage_amount: Optional[float] = None
    wage_period: Optional[str] = None
    workers_needed: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    status: Optional[str] = None

class LabourJobResponse(LabourJobBase):
    id: int
    poster_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LabourSearch(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 25.0
    job_type: Optional[str] = None
