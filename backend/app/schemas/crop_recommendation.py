"""
Crop Recommendation schemas for the "No Soil Report" flow.

These are the data contracts for
    POST /api/v1/crop-recommendation/no-soil-report
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class NoSoilReportRequest(BaseModel):
    """
    Request body for the No Soil Report crop recommendation flow.

    Latitude/longitude are used to obtain soil (SIS India) and weather
    (Open-Meteo). ``state`` is optional and only softens regional validation.
    """
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    state: Optional[str] = Field(
        default=None,
        description="State name (optional). Used only for the regional scoring layer.",
    )


class NoSoilReportLocation(BaseModel):
    latitude: float
    longitude: float
    state: Optional[str] = None
    display_name: Optional[str] = None


class CropCandidate(BaseModel):
    """A single candidate crop emitted after regional validation."""
    crop_name: str
    rank: int
    model_probability: float = Field(..., ge=0, le=1)
    regional_score: float = Field(..., ge=0)
    final_score: float = Field(..., ge=0)


class NoSoilReportResponse(BaseModel):
    success: bool = True
    location: Optional[NoSoilReportLocation] = None
    season: Optional[str] = None
    season_window: Optional[str] = None
    estimated_soil: Optional[dict] = None
    soil_source: Optional[str] = None
    weather: Optional[dict] = None
    top_crops: List[CropCandidate] = Field(default_factory=list)
    explanation: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)