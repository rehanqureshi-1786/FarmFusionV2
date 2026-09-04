"""
Pydantic v2 schemas for Disaster Risk Analysis and Early Warning.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DisasterRiskRequest(BaseModel):
    lat: Optional[float] = Field(None, description="Farm latitude coordinate")
    lon: Optional[float] = Field(None, description="Farm longitude coordinate")
    location_name: Optional[str] = Field(None, description="City, village, or farm identifier")
    farmer_phone: Optional[str] = Field(None, description="Farmer E.164 phone number for proactive alerting")
    farmer_name: Optional[str] = Field("Farmer", description="Farmer name")
    language: Optional[str] = Field("hi", description="BCP-47 language code (hi, gu, mr, pa, bn, en, etc.)")
    crop_name: Optional[str] = Field(None, description="Current standing crop")
    
    # Optional weather overrides (e.g. for direct scenario testing or pre-fetched metrics)
    temperature: Optional[float] = Field(None, description="Air temperature in °C")
    humidity: Optional[float] = Field(None, description="Relative humidity in %")
    rainfall: Optional[float] = Field(None, description="24-hour cumulative precipitation in mm")
    wind_speed: Optional[float] = Field(None, description="10m sustained wind speed in km/h")
    pressure: Optional[float] = Field(None, description="Mean sea level pressure in hPa")


class DisasterPredictionItem(BaseModel):
    disaster_type: str = Field(..., description="Hazard type (Flood Risk, Cyclone Risk, Drought Risk, Low Risk)")
    risk_level: str = Field(..., description="Deterministic category: LOW, MEDIUM, HIGH, CRITICAL")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Continuous risk metric 0.0 - 100.0")
    probability: float = Field(..., ge=0.0, le=1.0, description="Model class probability normalized to 0.0 - 1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Ensemble confidence score normalized to 0.0 - 1.0")
    prediction_horizon: str = Field("24-48 hours", description="Forecast time window")
    trigger_factors: List[str] = Field(default_factory=list, description="Traceable factors from actual weather inputs")
    recommendations: List[str] = Field(default_factory=list, description="Agronomic safety actions")
    probabilities: Dict[str, float] = Field(default_factory=dict, description="Full posterior probability distribution")
    xgboost: Optional[Dict[str, Any]] = Field(None, description="Direct XGBoost model inference output")


class DisasterAlertInfo(BaseModel):
    should_alert: bool = Field(..., description="True if risk level warrants proactive outbound phone call")
    severity: str = Field(..., description="Alert severity: LOW, MEDIUM, HIGH, CRITICAL")
    reason: str = Field(..., description="Deterministic explanation of alert decision")
    alert_status: str = Field(
        ...,
        description="DISPLAY_ONLY | ELIGIBLE | TRIGGERED | SKIPPED_COOLDOWN | NO_PHONE | CALL_FAILED"
    )
    call_id: Optional[str] = Field(None, description="Vobiz call identifier if call was queued")
    alert_message: Optional[str] = Field(None, description="Localized voice alert message dispatched to farmer")
    cooldown_remaining_seconds: Optional[int] = Field(None, description="Remaining seconds if suppressed by cooldown")


class DisasterModelMeta(BaseModel):
    name: str = "DisasterPredictorAI-RealXGBoost-Ensemble"
    version: str = "2.0.0"
    training_data: str = "6,982 Real Indian Historical Observations (Open-Meteo ERA5 Archive)"
    ensemble_members: List[str] = ["XGBoost", "RandomForest", "GradientBoosting", "ExtraTrees"]
    xgboost_accuracy: str = "97.17%"
    ensemble_accuracy: str = "97.25%"


class DisasterRiskResponse(BaseModel):
    location: Dict[str, Any] = Field(..., description="Resolved location coordinates and name")
    weather_metrics: Dict[str, float] = Field(..., description="Weather parameters evaluated by the model")
    predictions: List[DisasterPredictionItem] = Field(default_factory=list, description="Hazard assessments")
    alert: DisasterAlertInfo = Field(..., description="Deterministic alerting outcome")
    model: DisasterModelMeta = Field(default_factory=DisasterModelMeta, description="Model provenance metadata")
    generated_at: str = Field(..., description="ISO 8601 UTC timestamp")
