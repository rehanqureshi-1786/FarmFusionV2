"""
Disaster Risk Prediction Tool for FarmFusion LangGraph Orchestrator.
Evaluates 1 to 7-day agricultural disaster risk (Flood, Cyclone, Drought, Low Risk)
using the 4-model DisasterPredictorAI ensemble and physical NWP forecast from Open-Meteo.
"""
from typing import Any, Dict, List, Optional
import structlog
from pydantic import BaseModel, Field

from app.services.weather_service import WeatherService
from app.ml.disaster.inference import disaster_predictor

logger = structlog.get_logger(__name__)


class DisasterRiskInput(BaseModel):
    latitude: float = Field(default=26.9124, description="Latitude of the farm/location")
    longitude: float = Field(default=75.7873, description="Longitude of the farm/location")
    location_name: Optional[str] = Field(default=None, description="City, village, or farm identifier")
    crop_name: Optional[str] = Field(default=None, description="Current standing crop name")
    days: int = Field(default=7, ge=1, le=7, description="Number of forecast days to evaluate (1 to 7)")


class DailyDisasterRisk(BaseModel):
    date: str
    temperature_c: float
    rainfall_mm: float
    wind_speed_kmh: float
    humidity_percent: float
    disaster_type: str
    risk_level: str
    risk_score: float
    probability: float
    trigger_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class DisasterRiskOutput(BaseModel):
    location: str
    forecast_days: int
    current_disaster_type: str
    current_risk_level: str
    current_risk_score: float
    peak_disaster_type: str
    peak_risk_level: str
    peak_risk_score: float
    peak_risk_date: str
    has_critical_alert: bool
    daily_timeline: List[DailyDisasterRisk] = Field(default_factory=list)
    summary: str
    error: Optional[str] = None


async def disaster_risk_tool(input_data: DisasterRiskInput) -> DisasterRiskOutput:
    """
    Purpose: Evaluates 1 to 7-day disaster risk using DisasterPredictorAI ensemble and Open-Meteo.
    Inputs: DisasterRiskInput with coordinates, optional location_name, crop_name, and days (1-7).
    Outputs: DisasterRiskOutput with full daily disaster timeline, peak hazard, and agronomic summary.
    Side effects: Logs execution via structlog.
    Error cases: Returns DisasterRiskOutput with error set if physical weather or ML inference fails.
    """
    location_str = input_data.location_name or f"{input_data.latitude:.2f}, {input_data.longitude:.2f}"
    days = max(1, min(input_data.days, 7))

    try:
        logger.info(
            "disaster_risk_tool_invoked",
            location=location_str,
            lat=input_data.latitude,
            lon=input_data.longitude,
            days=days,
            crop=input_data.crop_name
        )

        # 1. Fetch physical weather forecast from Open-Meteo
        forecast_res = await WeatherService.get_forecast(
            lat=input_data.latitude,
            lon=input_data.longitude,
            days=days,
            location_name=input_data.location_name
        )
        if not forecast_res.get("success"):
            raise ValueError(forecast_res.get("error", "Weather forecast unavailable"))

        # Fetch current weather to calibrate current humidity & pressure
        curr_res = await WeatherService.get_current_weather(
            lat=input_data.latitude,
            lon=input_data.longitude,
            location_name=input_data.location_name
        )
        base_humidity = float(curr_res.get("humidity_percent", 60.0)) if curr_res.get("success") else 60.0
        base_pressure = float(curr_res.get("pressure_hpa", 1013.0)) if curr_res.get("success") else 1013.0

        daily_items = forecast_res.get("forecast", [])
        if not daily_items:
            raise ValueError("No forecast items returned by Open-Meteo")

        timeline: List[DailyDisasterRisk] = []
        peak_score = -1.0
        peak_hazard = "Low Risk"
        peak_level = "LOW"
        peak_date = daily_items[0].get("date", "Today")

        for idx, item in enumerate(daily_items):
            date_str = item.get("date", f"Day {idx + 1}")
            temp_max = float(item.get("temperature_max_c") or item.get("temperature_c") or 28.0)
            precip_mm = float(item.get("precipitation_mm", 0.0))
            
            # Wind speed: handle km/h or m/s
            wind_kmh = float(
                item.get("wind_speed_max_kmh")
                or (float(item.get("wind_speed_max_ms", 0.0)) * 3.6)
                or 12.0
            )

            # Daily humidity estimation (elevated on rainy days)
            day_humidity = min(98.0, base_humidity + 20.0) if precip_mm >= 25.0 else base_humidity

            # Run DisasterPredictorAI ML inference for this day
            pred = disaster_predictor.predict(
                temperature=temp_max,
                humidity=day_humidity,
                rainfall=precip_mm,
                wind_speed=wind_kmh,
                pressure=base_pressure,
                crop_name=input_data.crop_name
            )

            d_type = pred["disaster_type"]
            r_level = pred["risk_level"]
            r_score = float(pred["risk_score"])
            prob = float(pred["probability"])

            daily_risk = DailyDisasterRisk(
                date=date_str,
                temperature_c=temp_max,
                rainfall_mm=precip_mm,
                wind_speed_kmh=wind_kmh,
                humidity_percent=day_humidity,
                disaster_type=d_type,
                risk_level=r_level,
                risk_score=r_score,
                probability=prob,
                trigger_factors=pred.get("trigger_factors", []),
                recommendations=pred.get("recommendations", [])
            )
            timeline.append(daily_risk)

            # Track peak risk across the horizon
            if r_score > peak_score:
                peak_score = r_score
                peak_hazard = d_type
                peak_level = r_level
                peak_date = date_str

        current_risk_item = timeline[0]
        has_critical = any(d.risk_level in ["HIGH", "CRITICAL"] for d in timeline)

        # Build concise natural language summary
        if has_critical:
            summary = (
                f"Severe hazard detected: {peak_hazard} ({peak_level}, score {peak_score:.1f}) on {peak_date}. "
                f"Immediate agricultural safeguards recommended."
            )
        elif peak_level == "MEDIUM":
            summary = (
                f"Moderate weather fluctuation expected: {peak_hazard} ({peak_level}) on {peak_date}. "
                f"Monitor field conditions."
            )
        else:
            summary = (
                f"Favorable conditions across the next {len(timeline)} days with Low Risk. "
                f"Normal farming activities can proceed safely."
            )

        return DisasterRiskOutput(
            location=forecast_res.get("location_name") or location_str,
            forecast_days=len(timeline),
            current_disaster_type=current_risk_item.disaster_type,
            current_risk_level=current_risk_item.risk_level,
            current_risk_score=current_risk_item.risk_score,
            peak_disaster_type=peak_hazard,
            peak_risk_level=peak_level,
            peak_risk_score=peak_score,
            peak_risk_date=peak_date,
            has_critical_alert=has_critical,
            daily_timeline=timeline,
            summary=summary,
            error=None
        )

    except Exception as exc:
        logger.error("disaster_risk_tool_failed", location=location_str, error=str(exc))
        return DisasterRiskOutput(
            location=location_str,
            forecast_days=days,
            current_disaster_type="Low Risk",
            current_risk_level="LOW",
            current_risk_score=0.0,
            peak_disaster_type="Low Risk",
            peak_risk_level="LOW",
            peak_risk_score=0.0,
            peak_risk_date="",
            has_critical_alert=False,
            daily_timeline=[],
            summary="Disaster risk forecasting is temporarily unavailable.",
            error=f"Disaster prediction failed: {str(exc)}"
        )
