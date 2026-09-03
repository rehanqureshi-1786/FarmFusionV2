"""
Crop Recommendation schemas for the "No Soil Report" and Environmental Suitability flow.

Every returned parameter contains full data provenance:
- value
- unit
- source
- status (e.g. REAL, UNAVAILABLE)
- period / depth where applicable
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NoSoilReportRequest(BaseModel):
    """
    Request body for the No Soil Report crop recommendation flow.
    """
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    state: Optional[str] = Field(
        default=None,
        description="State name (optional). Used for regional context.",
    )
    location_name: Optional[str] = Field(
        default=None,
        description="Full place name from device geocoding (e.g. Village/City, District, State, Country)",
    )
    farmer_selected_soil_type: Optional[str] = Field(
        default=None,
        description="Farmer selected soil type: Sandy Soil, Black Soil, Red Soil, Alluvial Soil",
    )
    soil_type: Optional[str] = Field(
        default=None,
        description="Alias for farmer_selected_soil_type for compatibility",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code for response (hi, en, gu, mr, pa, bn, ta, te, kn, ml, or, as, ur, mai)",
    )


class ProvenanceField(BaseModel):
    """A single parameter with transparent provenance metadata."""
    value: Optional[Any] = None
    unit: Optional[str] = None
    source: Optional[str] = None
    status: str = Field(default="REAL", description="REAL, ESTIMATED, or UNAVAILABLE")
    estimated: bool = False
    requires_soil_test: bool = False
    note: Optional[str] = None
    period: Optional[str] = None
    depth: Optional[str] = None


class ProvenanceLocation(BaseModel):
    latitude: float
    longitude: float
    display_name: Optional[str] = None
    state: Optional[str] = None
    source: str = "Device GPS"


class ProvenanceWeather(BaseModel):
    temperature: ProvenanceField
    humidity: ProvenanceField
    current_conditions: Optional[str] = None
    weather_available: bool = True


class ProvenanceRainfall(BaseModel):
    annual_rainfall: ProvenanceField
    period: Optional[str] = "2025"
    rainfall_available: bool = True


class ProvenanceSoil(BaseModel):
    farmer_selected_type: Optional[str] = None
    ph: ProvenanceField
    sand: ProvenanceField
    clay: ProvenanceField
    silt: ProvenanceField
    texture_class: Optional[str] = None
    depth_used: str = "0-5cm"
    soil_data_available: bool = False


class ProvenanceNutrients(BaseModel):
    nitrogen: ProvenanceField
    phosphorus: ProvenanceField
    potassium: ProvenanceField


class EnvironmentalCropRecommendation(BaseModel):
    crop_name: str
    hindi_name: Optional[str] = None
    suitability_level: str = Field(..., description="Highly Suitable, Suitable, Moderately Suitable")
    suitability_score: float = Field(..., ge=0, le=1)
    season: str
    water_requirement: Optional[str] = None
    contributing_factors: List[str] = []
    management_notes: List[str] = []


class NoSoilReportResponse(BaseModel):
    """
    Structured real-data-only response with complete provenance for all parameters.
    """
    success: bool = True
    recommendation_available: bool = True
    recommendation_mode: str = "ENVIRONMENTAL_SUITABILITY"
    reason: Optional[str] = None
    message: Optional[str] = None
    location: ProvenanceLocation
    weather: ProvenanceWeather
    rainfall: ProvenanceRainfall
    soil: ProvenanceSoil
    nutrients: ProvenanceNutrients
    soil_parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    recommendations: List[EnvironmentalCropRecommendation] = []
    # Retain top_crops / estimated_soil dictionary aliases for backward client resilience
    top_crops: List[Dict[str, Any]] = []
    estimated_soil: Optional[Dict[str, Any]] = None
    season: Optional[str] = None
    season_window: Optional[str] = None
    soil_source: Optional[str] = None
    explanation: Optional[str] = None
    warnings: List[str] = []