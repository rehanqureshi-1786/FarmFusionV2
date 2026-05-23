"""
Weather API Routes
GET /weather/current - Current weather
GET /weather/forecast - Weather forecast
GET /weather/farming - Weather for farming decisions
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current")
async def get_current_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """
    GET /weather/current

    Get current weather conditions

    - **lat**: Latitude coordinate
    - **lon**: Longitude coordinate

    Returns temperature, humidity, conditions, and farming advice
    """
    try:
        weather = await WeatherService.get_current_weather(lat, lon)
        if not weather.get("success"):
            raise HTTPException(status_code=503, detail=weather.get("error", "Weather service unavailable"))
        return {
            "success": True,
            "data": weather
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather: {str(e)}")


@router.get("/forecast")
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    days: int = Query(5, ge=1, le=7, description="Number of days (1-7)"),
):
    """
    GET /weather/forecast

    Get weather forecast

    - **lat**: Latitude coordinate
    - **lon**: Longitude coordinate
    - **days**: Forecast days (1-7)

    Returns daily forecast with farming advice
    """
    try:
        forecast = await WeatherService.get_forecast(lat, lon, days)
        if not forecast.get("success"):
            raise HTTPException(status_code=503, detail=forecast.get("error", "Forecast service unavailable"))
        return {
            "success": True,
            "data": forecast
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast: {str(e)}")


@router.get("/farming")
async def get_farming_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    days: int = Query(7, ge=1, le=7, description="Number of days"),
):
    """
    GET /weather/farming

    Get comprehensive weather for farming decisions

    - **lat**: Latitude coordinate
    - **lon**: Longitude coordinate
    - **days**: Number of days (1-7)

    Returns current + forecast with farming-specific summary
    """
    try:
        weather = await WeatherService.get_farming_weather(lat, lon, days)
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
    """
    GET /weather/test

    Test endpoint for weather API
    """
    return {
        "success": True,
        "message": "Weather API is working!",
        "endpoints": {
            "current": "GET /weather/current?lat=19.076&lon=72.877",
            "forecast": "GET /weather/forecast?lat=19.076&lon=72.877&days=5",
            "farming": "GET /weather/farming?lat=19.076&lon=72.877&days=7"
        },
        "note": "Replace lat/lon with your farm coordinates"
    }
