"""
Weather Service - Single Source of Truth for FarmFusion Weather Architecture.
"""
from typing import Dict, Any, Optional, List
from app.agents.weather_agent import weather_agent
from app.schemas.weather import WeatherAlertItem, AgriculturalAdvisory


class WeatherService:
    """Service layer for weather data, alerts, and agricultural advisory"""

    @staticmethod
    async def get_current_weather(
        lat: float,
        lon: float,
        location_name: Optional[str] = None,
        location_source: str = "coordinates_only",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current physical weather for location with localized farming advice.
        """
        from app.core.language import get_current_language
        return await weather_agent.get_current_weather(
            lat=lat,
            lon=lon,
            location_name=location_name,
            location_source=location_source,
            language=language or get_current_language()
        )

    @staticmethod
    async def get_forecast(
        lat: float,
        lon: float,
        days: int = 7,
        location_name: Optional[str] = None,
        location_source: str = "coordinates_only",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get 1-7 day physical weather forecast with localized farming advice.
        """
        from app.core.language import get_current_language
        return await weather_agent.get_forecast(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            location_source=location_source,
            language=language or get_current_language()
        )

    @staticmethod
    async def get_weather_alerts(
        lat: float,
        lon: float,
        days: int = 7,
        location_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[WeatherAlertItem]:
        """
        Evaluates forecast against deterministic agronomic alert thresholds.
        """
        from app.core.language import get_current_language
        return await weather_agent.get_weather_alerts(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            language=language or get_current_language()
        )

    @staticmethod
    async def get_agricultural_advisory(
        lat: float,
        lon: float,
        crop_name: Optional[str] = None,
        growth_stage: Optional[str] = None,
        soil_type: Optional[str] = None,
        language: Optional[str] = None
    ) -> AgriculturalAdvisory:
        """
        Constructs an explicit agronomic advisory interpreting weather for farm tasks.
        """
        from app.core.language import get_current_language
        return await weather_agent.get_agricultural_advisory(
            lat=lat,
            lon=lon,
            crop_name=crop_name,
            growth_stage=growth_stage,
            soil_type=soil_type,
            language=language or get_current_language()
        )

    @staticmethod
    async def get_farming_weather(
        lat: float,
        lon: float,
        days: int = 7,
        location_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive weather data for farming decisions.
        """
        from app.core.language import get_current_language
        lang = language or get_current_language()
        current = await WeatherService.get_current_weather(lat, lon, location_name=location_name, language=lang)
        if not current.get("success"):
            return current

        forecast = await WeatherService.get_forecast(lat, lon, days, location_name=location_name, language=lang)
        if not forecast.get("success"):
            return forecast

        alerts = await WeatherService.get_weather_alerts(lat, lon, days, location_name=location_name, language=lang)
        advisory = await WeatherService.get_agricultural_advisory(lat, lon, language=lang)

        return {
            "success": True,
            "current": current,
            "forecast": forecast,
            "alerts": [alert.model_dump() for alert in alerts],
            "agricultural_advisory": advisory.model_dump(),
            "farming_summary": WeatherService._generate_farming_summary(current, forecast)
        }

    @staticmethod
    async def get_weather_timeline(
        lat: float,
        lon: float,
        forecast_days: int = 7,
        past_days: int = 7,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        return await weather_agent.get_weather_timeline(lat, lon, forecast_days, past_days, language=language)

    @staticmethod
    async def get_seasonal_rainfall(
        lat: float,
        lon: float,
        season: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        return await weather_agent.get_seasonal_rainfall(lat, lon, season, year)

    @staticmethod
    async def get_annual_rainfall(
        lat: float,
        lon: float,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        return await weather_agent.get_annual_rainfall(lat, lon, year)

    @staticmethod
    def _generate_farming_summary(
        current: Dict[str, Any],
        forecast: Dict[str, Any]
    ) -> str:
        summary = []
        if "temperature_c" in current:
            temp = current["temperature_c"]
            if temp > 35:
                summary.append("High temperatures expected - ensure irrigation")
            elif temp < 15:
                summary.append("Cold conditions - protect sensitive crops")

        forecast_days = forecast.get("forecast", [])
        rainy_days = sum(1 for day in forecast_days if (day.get("rain_chance", 0) > 40 or day.get("precipitation_probability_percent", 0) > 40))

        if rainy_days > 0:
            summary.append(f"{rainy_days} rainy days ahead - adjust irrigation schedule")
        else:
            summary.append("Dry period ahead - monitor soil moisture")

        high_wind_days = sum(
            1 for day in forecast_days
            if (day.get("wind_speed_ms", 0) > 8 or day.get("wind_speed_max_ms", 0) > 8)
        )
        if high_wind_days > 0:
            summary.append(f"{high_wind_days} windy days - delay spraying operations")

        return " | ".join(summary) if summary else "Good weather conditions for farming"
