from datetime import datetime
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

from app.core.config import settings


class WeatherAgent:
    BASE_URL_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
    BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"

    def _fetch(self, url: str) -> Dict[str, Any]:
        api_key = getattr(settings, "OPENWEATHER_API_KEY", None) or getattr(settings, "WEATHER_API_KEY", None)
        if not api_key:
            raise RuntimeError("OpenWeather API key is not configured")

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

    def _fetch_current(self, latitude: float, longitude: float) -> Dict[str, Any]:
        url = (
            f"{self.BASE_URL_CURRENT}?lat={latitude}&lon={longitude}"
            f"&units=metric&appid={getattr(settings, 'OPENWEATHER_API_KEY', None) or getattr(settings, 'WEATHER_API_KEY', None)}"
        )
        return self._fetch(url)

    def _fetch_forecast(self, latitude: float, longitude: float) -> Dict[str, Any]:
        url = (
            f"{self.BASE_URL_FORECAST}?lat={latitude}&lon={longitude}"
            f"&units=metric&appid={getattr(settings, 'OPENWEATHER_API_KEY', None) or getattr(settings, 'WEATHER_API_KEY', None)}"
        )
        return self._fetch(url)

    def _parse_current(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data:
            raise RuntimeError("Weather API returned no current weather data")

        weather_info = data.get("weather") or []
        description = "Unknown"
        if weather_info and isinstance(weather_info, list):
            description = weather_info[0].get("description", "Unknown").title()

        sunrise = data.get("sys", {}).get("sunrise")
        sunset = data.get("sys", {}).get("sunset")

        return {
            "temperature": data.get("main", {}).get("temp"),
            "rain_chance": int((data.get("pop", 0)) * 100) if data.get("pop") is not None else 0,
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "description": description,
            "wind_speed": data.get("wind", {}).get("speed"),
            "visibility": data.get("visibility"),
            "clouds": data.get("clouds", {}).get("all"),
            "sunrise": datetime.utcfromtimestamp(sunrise).isoformat() if sunrise else None,
            "sunset": datetime.utcfromtimestamp(sunset).isoformat() if sunset else None,
            "daily": [],
        }

    def _parse_forecast(self, data: Dict[str, Any], days: int) -> List[Dict[str, Any]]:
        items = data.get("list") or []
        if not items:
            raise RuntimeError("Weather API returned no forecast data")

        grouped: Dict[str, Dict[str, Any]] = {}
        for entry in items:
            dt = entry.get("dt")
            if not dt:
                continue
            date_str = datetime.utcfromtimestamp(dt).strftime("%Y-%m-%d")
            if date_str not in grouped:
                grouped[date_str] = {
                    "dt": dt,
                    "entry": entry,
                    "min_temp": entry.get("main", {}).get("temp_min"),
                    "max_temp": entry.get("main", {}).get("temp_max"),
                }
                continue

            temp_min = entry.get("main", {}).get("temp_min")
            temp_max = entry.get("main", {}).get("temp_max")
            if temp_min is not None and (grouped[date_str]["min_temp"] is None or temp_min < grouped[date_str]["min_temp"]):
                grouped[date_str]["min_temp"] = temp_min
            if temp_max is not None and (grouped[date_str]["max_temp"] is None or temp_max > grouped[date_str]["max_temp"]):
                grouped[date_str]["max_temp"] = temp_max
            if dt == grouped[date_str]["dt"]:
                grouped[date_str]["entry"] = entry

        forecast_items: List[Dict[str, Any]] = []
        for date_str, info in list(grouped.items())[:days]:
            entry = info["entry"]
            weather_info = entry.get("weather") or []
            description = "Unknown"
            if weather_info and isinstance(weather_info, list):
                description = weather_info[0].get("description", "Unknown").title()

            forecast_items.append({
                "date": date_str,
                "temperature_c": entry.get("main", {}).get("temp"),
                "min_temperature_c": info.get("min_temp"),
                "max_temperature_c": info.get("max_temp"),
                "humidity_percent": entry.get("main", {}).get("humidity"),
                "weather": description,
                "wind_speed_ms": entry.get("wind", {}).get("speed"),
                "rain_chance": int((entry.get("pop", 0)) * 100) if entry.get("pop") is not None else 0,
            })
        return forecast_items

    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        data = self._fetch_current(latitude, longitude)
        return self._parse_current(data)

    def get_forecast(self, latitude: float, longitude: float, days: int) -> List[Dict[str, Any]]:
        data = self._fetch_forecast(latitude, longitude)
        return self._parse_forecast(data, days)
