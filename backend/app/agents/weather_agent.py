from typing import Any, Dict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

from app.core.config import settings


class WeatherAgent:
    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch current weather using OpenWeather One Call API.

        Returns a dict with at least `temperature` (C) and `rain_chance` (percent).
        Falls back to a modest default on any error.
        """
        api_key = getattr(settings, "OPENWEATHER_API_KEY", None) or getattr(settings, "WEATHER_API_KEY", None)
        if not api_key:
            return {"temperature": 25.0, "rain_chance": 10}

        url = (
            f"https://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}"
            f"&units=metric&exclude=minutely,alerts&appid={api_key}"
        )
        req = Request(url, headers={"User-Agent": "FarmFusion/1.0 (contact: dev)"})
        try:
            with urlopen(req, timeout=10) as resp:
                data = json.load(resp)
        except (HTTPError, URLError, json.JSONDecodeError, Exception):
            return {"temperature": 25.0, "rain_chance": 10}

        # Extract sensible defaults from API response
        temp = None
        rain_chance = 0
        try:
            temp = data.get("current", {}).get("temp")
            # daily[0].pop is probability of precipitation for today
            daily = data.get("daily") or []
            if daily:
                rain_chance = int((daily[0].get("pop", 0)) * 100)
        except Exception:
            pass

        if temp is None:
            temp = 25.0

        return {"temperature": float(temp), "rain_chance": int(rain_chance)}
