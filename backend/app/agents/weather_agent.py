from typing import Any, Dict, Optional


class WeatherAgent:
    def get_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        return {"temperature": 25.0, "rain_chance": 10}
