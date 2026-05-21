from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.services.weather_service import WeatherService


def _default_alert() -> Dict[str, Any]:
    return {"message": "Monitor your crops closely and water as needed.", "timestamp": datetime.now(timezone.utc).isoformat()}


def get_dashboard_urgent_alert(latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
    if latitude is None or longitude is None:
        return _default_alert()
    weather = WeatherService.get_weather(latitude, longitude)
    if weather and weather.get("rain_chance", 0) > 70:
        return {"message": "Heavy rain expected soon. Secure loose materials.", "timestamp": datetime.now(timezone.utc).isoformat()}
    return _default_alert()
