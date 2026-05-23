"""
Urgent / dashboard alerts derived from live weather when coordinates are provided.
Falls back to a static advisory when location is missing or weather is unavailable.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.services.weather_service import WeatherService


def _default_alert() -> Dict[str, Any]:
    return {
        "success": True,
        "title": "High Humidity Alert",
        "message": (
            "Humidity is rising (85%). Fungal risk for wheat is high. "
            "Use prevention sprays."
        ),
        "severity": "WARNING",
        "source": "default",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


async def get_dashboard_urgent_alert(
    lat: Optional[float], lon: Optional[float]
) -> Dict[str, Any]:
    if lat is None or lon is None:
        return _default_alert()

    weather = await WeatherService.get_current_weather(lat, lon)
    if not weather.get("success"):
        return _default_alert()

    temp = float(weather.get("temperature_c") or 0)
    hum = int(weather.get("humidity_percent") or 0)
    text = (weather.get("weather") or "").lower()
    advice = (weather.get("farming_advice") or "").strip()

    title = "Farm Weather Alert"
    message = advice if advice else (
        "Review today's conditions and adjust irrigation and crop protection."
    )
    severity = "INFO"

    if temp >= 41:
        title = "Extreme Heat Warning"
        message = (
            f"Temperature near {temp:.0f}°C. Avoid field work midday; "
            "increase irrigation and protect sensitive crops."
        )
        severity = "EMERGENCY"
    elif any(k in text for k in ("thunder", "storm", "heavy rain")):
        title = "Severe Weather Alert"
        message = (
            "Strong rain or storms possible. Secure equipment and delay spraying "
            "until conditions stabilize."
        )
        severity = "EMERGENCY"
    elif hum >= 85:
        title = "High Humidity Alert"
        message = (
            f"Humidity is very high ({hum}%). Fungal disease risk is elevated. "
            "Improve airflow and consider preventive sprays where appropriate."
        )
        severity = "WARNING"
    elif temp >= 38:
        title = "High Temperature Alert"
        message = (
            f"Temperature around {temp:.0f}°C. Prefer irrigation early morning "
            "or evening; watch for heat stress."
        )
        severity = "WARNING"
    elif hum >= 75:
        title = "Moisture Advisory"
        message = (
            f"Humidity is elevated ({hum}%). Monitor for fungal issues on dense canopies."
        )
        severity = "WARNING"
    elif temp <= 5:
        title = "Cold Weather Alert"
        message = (
            "Cold conditions may stress sensitive crops. Protect nurseries and delay "
            "spraying until temperatures recover."
        )
        severity = "WARNING"

    return {
        "success": True,
        "title": title,
        "message": message,
        "severity": severity,
        "source": "weather",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
