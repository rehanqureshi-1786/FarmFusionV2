"""
Pydantic v2 schemas for FarmFusion Weather System.
Strictly separates machine-readable numeric observations from human-facing agricultural advisories.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class SoilMoistureDepthItem(BaseModel):
    depth_cm: str = Field(..., description="Depth range e.g. '0-1cm (Surface)', '3-9cm (Root Zone)'")
    moisture_percentage: float = Field(..., description="Moisture percentage 0-100%")
    moisture_m3m3: float = Field(..., description="Volumetric water content m3/m3")
    status: str = Field(..., description="DEFICIT, OPTIMAL, or SATURATED")


class SmartIrrigationAdvisor(BaseModel):
    root_zone_moisture_percent: float = Field(..., description="Volumetric moisture in active 3-9cm root zone (0-100%)")
    surface_moisture_percent: float = Field(..., description="Moisture in 0-1cm surface crust (0-100%)")
    deep_moisture_percent: float = Field(..., description="Moisture in 9-27cm subsoil reserve (0-100%)")
    soil_temperature_c: float = Field(..., description="Soil temperature in Celsius")
    status: str = Field(..., description="DEFICIT, OPTIMAL, or SATURATED")
    status_badge: str = Field(..., description="NEEDS_WATER, OPTIMAL, or WATERLOGGED_RISK")
    status_title: str = Field(..., description="Localized status title (e.g. 'पर्याप्त नमी' / 'Optimal Moisture')")
    irrigation_need_score: int = Field(..., ge=0, le=100, description="0-100 index where higher means more urgent watering")
    actionable_advice: str = Field(..., description="Specific farming recommendation for today")
    actionable_advice_hi: Optional[str] = Field(None, description="Localized Hindi advice")
    watering_hours_recommended: float = Field(0.0, description="Recommended tube-well/pump hours")
    next_irrigation_window: str = Field(..., description="When to irrigate (e.g. 'This Evening', 'After 2-3 Days')")
    tillage_suitability: str = Field(..., description="Ploughing/sowing readiness (Vapsa status)")
    tillage_suitable: bool = Field(True, description="Boolean flag if field trafficability/tillage is suitable")
    next_24h_rain_sum_mm: float = Field(0.0, description="Total expected rainfall in upcoming 24 hours")
    depth_breakdown: List[SoilMoistureDepthItem] = Field(default_factory=list, description="Depth-wise metrics")


class CurrentWeather(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    location_name: Optional[str] = Field(None, description="Resolved city/village/region name, or None if unavailable")
    location_source: str = Field("coordinates_only", description="Source: 'gps', 'saved_farm', 'user_selected', or 'coordinates_only'")
    location: Optional[str] = Field(None, description="Backward compatibility alias for location_name")
    weather: Optional[str] = Field(None, description="Backward compatibility alias for condition")
    farming_advice: Optional[str] = Field(None, description="Backward compatibility single string")
    timestamp: str = Field(..., description="ISO observation timestamp")
    temperature_c: float = Field(..., description="Current temperature in Celsius")
    feels_like_c: float = Field(..., description="Apparent temperature in Celsius")
    humidity_percent: int = Field(..., ge=0, le=100, description="Relative humidity percentage")
    pressure_hpa: int = Field(..., description="Atmospheric pressure in hPa")
    wind_speed_kmh: float = Field(..., ge=0.0, description="Wind speed in km/h")
    wind_speed_ms: float = Field(..., ge=0.0, description="Wind speed in m/s")
    weather_code: int = Field(..., description="WMO standard weather condition code")
    condition: str = Field(..., description="Human-readable condition in requested language")
    weather: Optional[str] = Field(None, description="Condition description for mobile app compatibility")
    location: Optional[str] = Field(None, description="Location text for mobile app compatibility")
    farming_advice: Optional[str] = Field(None, description="Farming advice summary for mobile app compatibility")
    language: Optional[str] = Field(None, description="Resolved language code")
    cloudiness_percent: int = Field(0, ge=0, le=100, description="Cloud cover percentage")
    visibility_m: int = Field(10000, ge=0, description="Horizontal visibility in meters")
    sunrise: Optional[str] = Field(None, description="Sunrise ISO timestamp")
    sunset: Optional[str] = Field(None, description="Sunset ISO timestamp")
    source: str = Field("Open-Meteo", description="Underlying NWP weather data provider")
    smart_irrigation: Optional[SmartIrrigationAdvisor] = Field(None, description="Smart irrigation advisor and soil moisture metrics")

    @model_validator(mode="after")
    def populate_compatibility_fields(self):
        if not self.location:
            self.location = self.location_name or f"{round(self.latitude, 2)}°N, {round(self.longitude, 2)}°E"
        if not self.weather:
            self.weather = self.condition
        return self


class DailyForecastItem(BaseModel):
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    temperature_max_c: float = Field(..., description="Maximum expected temperature in Celsius")
    temperature_min_c: float = Field(..., description="Minimum expected temperature in Celsius")
    temperature_avg_c: Optional[float] = Field(None, description="Average temperature in Celsius")
    precipitation_mm: float = Field(0.0, ge=0.0, description="Expected precipitation accumulation in mm")
    precipitation_probability_percent: int = Field(0, ge=0, le=100, description="Probability of precipitation (0-100%)")
    wind_speed_max_kmh: float = Field(0.0, ge=0.0, description="Maximum wind speed in km/h")
    wind_speed_max_ms: float = Field(0.0, ge=0.0, description="Maximum wind speed in m/s")
    weather_code: int = Field(0, description="WMO standard weather condition code")
    condition: str = Field(..., description="Forecast condition text in requested language")
    sunrise: Optional[str] = Field(None, description="Sunrise time")
    sunset: Optional[str] = Field(None, description="Sunset time")


class WeatherAlertItem(BaseModel):
    alert_id: str = Field(..., description="Deterministic unique ID for deduplication: hash(type, loc, window, value)")
    alert_type: str = Field(..., description="HEAVY_RAIN, THUNDERSTORM, FROST, HEATWAVE, or HIGH_WIND")
    severity: str = Field(..., description="INFO, WARNING, or EMERGENCY")
    location_name: Optional[str] = Field(None, description="Location identifier")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    start_time: str = Field(..., description="Alert window start ISO timestamp")
    end_time: str = Field(..., description="Alert window end ISO timestamp")
    trigger_value: float = Field(..., description="Actual forecasted numeric metric triggering alert")
    threshold_value: float = Field(..., description="Configured rule threshold")
    unit: str = Field(..., description="Metric unit (e.g. °C, mm, km/h)")
    title: str = Field(..., description="Alert title in farmer's language")
    message: str = Field(..., description="Detailed alert description in farmer's language")
    farming_recommendation: str = Field(..., description="Actionable crop protection step")
    source: str = Field("Open-Meteo-NWP", description="Provider source")
    created_at: str = Field(..., description="Timestamp of alert generation")


class AgriculturalAdvisory(BaseModel):
    irrigation_advice: str = Field(..., description="Specific recommendation on whether to irrigate or pause")
    spraying_advice: str = Field(..., description="Recommendation regarding pesticide/fertilizer spraying windows")
    fieldwork_advice: str = Field(..., description="Suitability for harvesting, tilling, or general field operations")
    summary: str = Field(..., description="Overall concise agricultural weather summary")
    language: str = Field("hi", description="Language code used for narrative advice")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions made (e.g. crop growth stage, soil type)")


class WeatherCurrentResponse(BaseModel):
    success: bool = True
    data: CurrentWeather
    advisory: Optional[AgriculturalAdvisory] = None


class WeatherForecastResponse(BaseModel):
    success: bool = True
    latitude: float
    longitude: float
    location_name: Optional[str] = None
    location_source: str = "coordinates_only"
    forecast_days: int
    forecast: List[DailyForecastItem]
    farming_advice: Optional[str] = None
    smart_irrigation: Optional[SmartIrrigationAdvisor] = None
    source: str = "Open-Meteo"
    generated_at: str
    language: str = "hi"
    data: Optional[dict] = None


class WeatherAlertsResponse(BaseModel):
    success: bool = True
    count: int
    alerts: List[WeatherAlertItem]
    checked_at: str
