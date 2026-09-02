"""
Weather API Routes
GET /api/v1/weather/current - Real-time physical weather
GET /api/v1/weather/forecast - 1-7 day physical forecast
GET /api/v1/weather/alerts - Deterministic agronomic weather alerts
GET /api/v1/weather/advisory - Actionable agricultural weather advisory
GET /api/v1/weather/farming - Comprehensive farming weather bundle
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone

from app.services.weather_service import WeatherService
from app.schemas.weather import (
    WeatherCurrentResponse,
    WeatherForecastResponse,
    WeatherAlertsResponse,
    CurrentWeather,
    DailyForecastItem,
    WeatherAlertItem,
    AgriculturalAdvisory
)

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=WeatherCurrentResponse)
async def get_current_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    location_name: Optional[str] = Query(None, description="Optional farm/city/village location name"),
    language: Optional[str] = Query(None, description="Language code (hi, gu, mr, pa, bn, en)")
):
    """
    Get current verified physical weather observations from Open-Meteo NWP.
    """
    from app.core.language import get_current_language
    req_lang = language or get_current_language()
    try:
        weather_dict = await WeatherService.get_current_weather(
            lat=lat,
            lon=lon,
            location_name=location_name,
            language=req_lang
        )
        if not weather_dict.get("success"):
            raise HTTPException(status_code=503, detail=weather_dict.get("error", "Weather service unavailable"))

        # Strip internal keys and map to CurrentWeather
        weather_dict.pop("success", None)
        advisory_text = weather_dict.pop("farming_advice", None)
        current_obj = CurrentWeather(**weather_dict)

        advisory_obj = await WeatherService.get_agricultural_advisory(
            lat=lat,
            lon=lon,
            language=req_lang
        )

        return WeatherCurrentResponse(
            success=True,
            data=current_obj,
            advisory=advisory_obj
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather: {str(e)}")


@router.get("/forecast", response_model=WeatherForecastResponse)
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=7, description="Number of forecast days (1-7)"),
    location_name: Optional[str] = Query(None, description="Optional farm/city/village location name"),
    language: Optional[str] = Query(None, description="Language code")
):
    """
    Get 1 to 7-day physical weather forecast from Open-Meteo NWP.
    """
    from app.core.language import get_current_language
    req_lang = language or get_current_language()
    try:
        forecast_dict = await WeatherService.get_forecast(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            language=req_lang
        )
        if not forecast_dict.get("success"):
            raise HTTPException(status_code=503, detail=forecast_dict.get("error", "Forecast service unavailable"))

        items = [DailyForecastItem(**d) for d in forecast_dict.get("forecast", [])]
        legacy_data = {
            "location": forecast_dict.get("location_name") or location_name or "",
            "forecast": [
                {
                    "date": d.date,
                    "temperature_c": d.temperature_avg_c or d.temperature_max_c,
                    "temperature_max_c": d.temperature_max_c,
                    "temperature_min_c": d.temperature_min_c,
                    "humidity_percent": 0,
                    "weather": d.condition,
                    "wind_speed_ms": d.wind_speed_max_ms,
                    "rain_chance": float(d.precipitation_probability_percent)
                } for d in items
            ],
            "farming_advice": forecast_dict.get("farming_advice") or "",
            "source": "Open-Meteo"
        }

        return WeatherForecastResponse(
            success=True,
            latitude=lat,
            longitude=lon,
            location_name=forecast_dict.get("location_name") or location_name,
            location_source=forecast_dict.get("location_source", "coordinates_only"),
            forecast_days=forecast_dict.get("forecast_days", days),
            forecast=items,
            farming_advice=forecast_dict.get("farming_advice"),
            source="Open-Meteo",
            generated_at=forecast_dict.get("generated_at", datetime.now(timezone.utc).isoformat()),
            language=req_lang,
            data=legacy_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast: {str(e)}")


@router.get("/alerts", response_model=WeatherAlertsResponse)
async def get_weather_alerts(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=7, description="Number of forecast days to evaluate"),
    location_name: Optional[str] = Query(None, description="Optional location name"),
    language: Optional[str] = Query(None, description="Language code")
):
    """
    Get deterministic agronomic weather alerts (Heavy Rain, Heatwave, Frost, High Wind, Thunderstorm).
    """
    from app.core.language import get_current_language
    req_lang = language or get_current_language()
    try:
        alerts = await WeatherService.get_weather_alerts(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            language=req_lang
        )
        return WeatherAlertsResponse(
            success=True,
            count=len(alerts),
            alerts=alerts,
            checked_at=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate weather alerts: {str(e)}")


@router.get("/advisory", response_model=AgriculturalAdvisory)
async def get_agricultural_advisory(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    crop_name: Optional[str] = Query(None, description="Optional crop name (e.g. Wheat, Mustard)"),
    growth_stage: Optional[str] = Query(None, description="Optional growth stage"),
    soil_type: Optional[str] = Query(None, description="Optional soil type"),
    language: Optional[str] = Query(None, description="Language code")
):
    """
    Get actionable agricultural advisory based on 3-day weather forecast.
    """
    from app.core.language import get_current_language
    req_lang = language or get_current_language()
    try:
        return await WeatherService.get_agricultural_advisory(
            lat=lat,
            lon=lon,
            crop_name=crop_name,
            growth_stage=growth_stage,
            soil_type=soil_type,
            language=req_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate agricultural advisory: {str(e)}")


@router.get("/farming")
async def get_farming_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=7, description="Number of days"),
    location_name: Optional[str] = Query(None, description="Location name"),
    language: Optional[str] = Query(None, description="Language code"),
):
    """
    Comprehensive bundle returning current, forecast, alerts, and farming summary.
    """
    from app.core.language import get_current_language
    req_lang = language or get_current_language()
    try:
        weather = await WeatherService.get_farming_weather(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            language=req_lang
        )
        if not weather.get("success"):
            raise HTTPException(status_code=503, detail=weather.get("error", "Farming weather service unavailable"))
        return {
            "success": True,
            "data": weather
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get farming weather: {str(e)}")


@router.get("/test")
async def test_weather_api():
    """Test endpoint for weather API."""
    return {
        "success": True,
        "message": "FarmFusion Weather API is fully operational with Open-Meteo NWP & Deterministic Alert Engine.",
        "endpoints": {
            "current": "GET /api/v1/weather/current?lat=26.9124&lon=75.7873&location_name=Jaipur",
            "forecast": "GET /api/v1/weather/forecast?lat=26.9124&lon=75.7873&days=7",
            "alerts": "GET /api/v1/weather/alerts?lat=26.9124&lon=75.7873",
            "advisory": "GET /api/v1/weather/advisory?lat=26.9124&lon=75.7873&crop_name=Wheat",
            "farming": "GET /api/v1/weather/farming?lat=26.9124&lon=75.7873&days=7"
        }
    }
