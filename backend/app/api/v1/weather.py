from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/")
async def weather_index():
    return {
        "success": True,
        "available": ["/current?lat=<>&lon=<>", "/forecast?lat=<>&lon=<>", "/farming?lat=<>&lon=<>"] ,
        "note": "Use query parameters lat and lon for location; example: /api/v1/weather/current?lat=12.97&lon=77.59",
    }


def build_current_weather(latitude: float, longitude: float) -> dict:
    weather = WeatherService.get_weather(latitude, longitude)
    temp = weather.get("temperature") if isinstance(weather, dict) else None
    rain_chance = weather.get("rain_chance") if isinstance(weather, dict) else None
    if temp is None:
        raise HTTPException(status_code=502, detail="Failed to fetch weather data")

    return {
        "success": True,
        "data": {
            "location": f"{latitude},{longitude}",
            "temperature_c": float(temp),
            "feels_like_c": float(temp) - 1.0,
            "humidity_percent": weather.get("humidity", 0),
            "pressure_hpa": weather.get("pressure", 0),
            "weather": weather.get("description", "Unknown"),
            "wind_speed_ms": weather.get("wind_speed", 0.0),
            "visibility_m": weather.get("visibility", 0),
            "cloudiness_percent": weather.get("clouds", 0),
            "sunrise": weather.get("sunrise") or (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "sunset": weather.get("sunset") or (datetime.utcnow() + timedelta(hours=10)).isoformat(),
            "farming_advice": weather.get("advice", ""),
            "source": "openweathermap",
        },
    }


def build_forecast(latitude: float, longitude: float, days: int) -> dict:
    forecasts = WeatherService.get_forecast(latitude, longitude, days)
    if not forecasts:
        raise HTTPException(status_code=502, detail="Failed to fetch forecast data")

    return {
        "success": True,
        "data": {
            "location": f"{latitude},{longitude}",
            "forecast": forecasts,
            "farming_advice": "Use this forecast to plan irrigation and spray schedules.",
            "source": "openweathermap",
        },
    }


@router.get("/current")
async def get_current_weather(
    lat: float = Query(...),
    lon: float = Query(...),
):
    return build_current_weather(lat, lon)


@router.get("/forecast")
async def get_weather_forecast(
    lat: float = Query(...),
    lon: float = Query(...),
    days: int = Query(5),
):
    return build_forecast(lat, lon, days)


@router.get("/farming")
async def get_farming_weather(
    lat: float = Query(...),
    lon: float = Query(...),
    days: int = Query(7),
):
    current = build_current_weather(lat, lon)["data"]
    forecast = build_forecast(lat, lon, days)["data"]
    return {
        "success": True,
        "data": {
            "current": current,
            "forecast": forecast,
            "farming_summary": "Conditions are favorable for crop maintenance this week.",
        },
    }
