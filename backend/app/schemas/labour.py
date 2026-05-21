from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class LabourJobBase(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    wage: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class LabourJobCreate(LabourJobBase):
    pass


class LabourJobUpdate(LabourJobBase):
    pass


class LabourJobResponse(LabourJobBase):
    id: int
    created_at: Optional[datetime] = None


class LabourSearch(BaseModel):
    location: Optional[str] = None
    model_config = ConfigDict(extra='ignore')
