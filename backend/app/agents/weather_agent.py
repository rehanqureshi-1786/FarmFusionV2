from datetime import datetime
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

from app.core.config import settings


class WeatherAgent:
    BASE_URL = "https://api.openweathermap.org/data/2.5/onecall"

    def _fetch_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        api_key = getattr(settings, "OPENWEATHER_API_KEY", None) or getattr(settings, "WEATHER_API_KEY", None)
        if not api_key:
            raise RuntimeError("OpenWeather API key is not configured")

        url = (
            f"{self.BASE_URL}?lat={latitude}&lon={longitude}"
            f"&units=metric&exclude=minutely,alerts&appid={api_key}"
        )
        req = Request(url, headers={"User-Agent": "FarmFusion/1.0 (contact: dev)"})
        try:
            with urlopen(req, timeout=10) as resp:
                return json.load(resp)
        except HTTPError as err:
            raise RuntimeError(f"Weather API request failed ({err.code}): {err.reason}")
        except URLError as err:
            raise RuntimeError(f"Weather API request failed: {err.reason}")
        except json.JSONDecodeError:
            raise RuntimeError("Weather API returned invalid JSON")

    def _parse_current(self, data: Dict[str, Any]) -> Dict[str, Any]:
        current = data.get("current") or {}
        if not current:
            raise RuntimeError("Weather API returned no current weather data")

        weather_info = current.get("weather") or []
        description = "Unknown"
        if weather_info and isinstance(weather_info, list):
            description = weather_info[0].get("description", "Unknown").title()

        daily = data.get("daily") or []
        rain_chance = 0
        if daily and isinstance(daily, list):
            rain_chance = int((daily[0].get("pop", 0)) * 100)

        sunrise = current.get("sunrise")
        sunset = current.get("sunset")

        return {
            "temperature": current.get("temp"),
            "rain_chance": rain_chance,
            "humidity": current.get("humidity"),
            "pressure": current.get("pressure"),
            "description": description,
            "wind_speed": current.get("wind_speed"),
            "visibility": current.get("visibility"),
            "clouds": current.get("clouds"),
            "sunrise": datetime.utcfromtimestamp(sunrise).isoformat() if sunrise else None,
            "sunset": datetime.utcfromtimestamp(sunset).isoformat() if sunset else None,
            "daily": daily,
        }

    def _parse_forecast(self, data: Dict[str, Any], days: int) -> List[Dict[str, Any]]:
        daily = data.get("daily") or []
        if not daily:
            raise RuntimeError("Weather API returned no forecast data")

        forecast_items: List[Dict[str, Any]] = []
        for index, day in enumerate(daily[:days]):
            temp_data = day.get("temp") or {}
            weather_info = day.get("weather") or []
            description = "Unknown"
            if weather_info and isinstance(weather_info, list):
                description = weather_info[0].get("description", "Unknown").title()

            forecast_items.append(
                {
                    "date": datetime.utcfromtimestamp(day.get("dt", 0)).strftime("%Y-%m-%d"),
                    "temperature_c": temp_data.get("day"),
                    "min_temperature_c": temp_data.get("min"),
                    "max_temperature_c": temp_data.get("max"),
                    "humidity_percent": day.get("humidity"),
                    "weather": description,
                    "wind_speed_ms": day.get("wind_speed"),
                    "rain_chance": int((day.get("pop", 0)) * 100),
                }
            )
        return forecast_items

    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        data = self._fetch_weather(latitude, longitude)
        return self._parse_current(data)

    def get_forecast(self, latitude: float, longitude: float, days: int) -> List[Dict[str, Any]]:
        data = self._fetch_weather(latitude, longitude)
        return self._parse_forecast(data, days)
