"""
Weather tool fetching real-time and forecast weather data from Open-Meteo API.
"""
from typing import Any
import httpx
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

# Weather code descriptions from WMO standard
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with light hail", 99: "Thunderstorm with heavy hail",
}


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
    Purpose: Fetch real-time weather and 7-day daily forecast from Open-Meteo API.
    Inputs: WeatherInput with latitude, longitude, optional location_name.
    Outputs: WeatherOutput with temperature, condition, daily forecast.
    Side effects: Logs request via structlog.
    Error cases: Catches network errors or bad responses and returns WeatherOutput with error set.
    """
    location_str = input_data.location_name or f"{input_data.latitude:.2f}, {input_data.longitude:.2f}"
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": input_data.latitude,
        "longitude": input_data.longitude,
        "current_weather": "true",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "auto"
    }

    try:
        logger.info("weather_tool_fetching", location=location_str, lat=input_data.latitude, lon=input_data.longitude)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        current = data.get("current_weather", {})
        daily_raw = data.get("daily", {})
        
        weather_code = int(current.get("weathercode", 0))
        condition = WMO_WEATHER_CODES.get(weather_code, "Unknown weather condition")
        
        forecast_list: list[DailyForecast] = []
        dates = daily_raw.get("time", [])
        max_temps = daily_raw.get("temperature_2m_max", [])
        min_temps = daily_raw.get("temperature_2m_min", [])
        precip = daily_raw.get("precipitation_sum", [])
        codes = daily_raw.get("weathercode", [])

        for i in range(min(len(dates), 7)):
            code = int(codes[i]) if i < len(codes) else 0
            forecast_list.append(DailyForecast(
                date=dates[i],
                temp_max=float(max_temps[i]) if i < len(max_temps) else 0.0,
                temp_min=float(min_temps[i]) if i < len(min_temps) else 0.0,
                precipitation_mm=float(precip[i]) if i < len(precip) else 0.0,
                condition=WMO_WEATHER_CODES.get(code, "Clear")
            ))

        return WeatherOutput(
            location=location_str,
            temperature_c=float(current.get("temperature", 0.0)),
            windspeed_kmh=float(current.get("windspeed", 0.0)),
            weather_code=weather_code,
            condition=condition,
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
