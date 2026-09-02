"""
Weather tool fetching real-time and forecast weather data through unified WeatherService.
"""
from typing import Any, List
import structlog
from pydantic import BaseModel, Field
from app.services.weather_service import WeatherService

logger = structlog.get_logger(__name__)


class WeatherInput(BaseModel):
    latitude: float = Field(..., description="Latitude of the location (e.g. 26.9124 for Jaipur)")
    longitude: float = Field(..., description="Longitude of the location (e.g. 75.7873 for Jaipur)")
    location_name: str | None = Field(default=None, description="Optional name of city/village")


class DailyForecast(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation_mm: float
    condition: str


class WeatherOutput(BaseModel):
    location: str
    temperature_c: float
    windspeed_kmh: float
    weather_code: int
    condition: str
    daily_forecast: list[DailyForecast] = []
    error: str | None = None


async def weather_tool(input_data: WeatherInput) -> WeatherOutput:
    """
    Purpose: Fetch real-time weather and 7-day daily forecast via WeatherService (Single Source of Truth).
    Inputs: WeatherInput with latitude, longitude, optional location_name.
    Outputs: WeatherOutput with temperature, condition, daily forecast.
    Side effects: Logs request via structlog.
    Error cases: Returns WeatherOutput with error set if backend call fails.
    """
    location_str = input_data.location_name or f"{input_data.latitude:.2f}, {input_data.longitude:.2f}"

    try:
        logger.info("weather_tool_invoked", location=location_str, lat=input_data.latitude, lon=input_data.longitude)
        current = await WeatherService.get_current_weather(
            lat=input_data.latitude,
            lon=input_data.longitude,
            location_name=input_data.location_name
        )
        if not current.get("success"):
            raise ValueError(current.get("error", "Weather service unavailable"))

        forecast_res = await WeatherService.get_forecast(
            lat=input_data.latitude,
            lon=input_data.longitude,
            days=7,
            location_name=input_data.location_name
        )
        if not forecast_res.get("success"):
            raise ValueError(forecast_res.get("error", "Forecast service unavailable"))

        forecast_list: List[DailyForecast] = []
        for day in forecast_res.get("forecast", []):
            forecast_list.append(DailyForecast(
                date=day.get("date", ""),
                temp_max=float(day.get("temperature_max_c", 0.0)),
                temp_min=float(day.get("temperature_min_c", 0.0)),
                precipitation_mm=float(day.get("precipitation_mm", 0.0)),
                condition=day.get("condition", day.get("weather", "Clear"))
            ))

        return WeatherOutput(
            location=current.get("location_name") or current.get("location") or location_str,
            temperature_c=float(current.get("temperature_c", 0.0)),
            windspeed_kmh=float(current.get("wind_speed_kmh", 0.0)),
            weather_code=int(current.get("weather_code", 0)),
            condition=str(current.get("condition") or current.get("weather") or "Clear"),
            daily_forecast=forecast_list,
            error=None
        )

    except Exception as e:
        logger.error("weather_tool_failed", location=location_str, error=str(e))
        return WeatherOutput(
            location=location_str,
            temperature_c=0.0,
            windspeed_kmh=0.0,
            weather_code=-1,
            condition="Unavailable",
            daily_forecast=[],
            error=f"Failed to retrieve weather data: {str(e)}"
        )
