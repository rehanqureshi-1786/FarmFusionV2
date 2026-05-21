from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


def build_current_weather(latitude: float, longitude: float) -> dict:
    weather = WeatherService.get_weather(latitude, longitude)
    return {
        "success": True,
        "data": {
            "location": f"{latitude},{longitude}",
            "temperature_c": weather.get("temperature", 25.0),
            "feels_like_c": weather.get("temperature", 25.0) - 1.0,
            "humidity_percent": 60,
            "pressure_hpa": 1013,
            "weather": "Partly Cloudy",
            "wind_speed_ms": 3.5,
            "visibility_m": 10000,
            "cloudiness_percent": 40,
            "sunrise": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "sunset": (datetime.utcnow() + timedelta(hours=10)).isoformat(),
            "farming_advice": "Water the crop in the early morning and check moisture levels.",
            "source": "farmfusion-ai",
        },
    }


def build_forecast(latitude: float, longitude: float, days: int) -> dict:
    forecasts: List[dict] = []
    now = datetime.utcnow()
    for index in range(days):
        forecasts.append(
            {
                "date": (now + timedelta(days=index)).strftime("%Y-%m-%d"),
                "temperature_c": 24.0 + index,
                "humidity_percent": 55 + index,
                "weather": "Sunny" if index % 2 == 0 else "Cloudy",
                "wind_speed_ms": 3.5 + 0.2 * index,
                "rain_chance": 10.0 + 5.0 * index,
            }
        )
    return {
        "success": True,
        "data": {
            "location": f"{latitude},{longitude}",
            "forecast": forecasts,
            "farming_advice": "Use this forecast to plan irrigation and spray schedules.",
            "source": "farmfusion-ai",
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
