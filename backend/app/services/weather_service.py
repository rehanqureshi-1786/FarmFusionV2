"""
Weather Service - Business logic for weather data
"""
from typing import Dict, Any, Optional
from app.agents.weather_agent import weather_agent


class WeatherService:
    """Service layer for weather data"""

    @staticmethod
    async def get_current_weather(
        lat: float,
        lon: float,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current weather for location with localized farming advice
        """
        from app.core.language import get_current_language
        return await weather_agent.get_current_weather(lat, lon, language=language or get_current_language())

    @staticmethod
    async def get_forecast(
        lat: float,
        lon: float,
        days: int = 5,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast with localized farming advice
        """
        from app.core.language import get_current_language
        return await weather_agent.get_forecast(lat, lon, days, language=language or get_current_language())

    @staticmethod
    async def get_farming_weather(
        lat: float,
        lon: float,
        days: int = 7,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive weather data for farming decisions
        """
        from app.core.language import get_current_language
        lang = language or get_current_language()
        current = await weather_agent.get_current_weather(lat, lon, language=lang)
        if not current.get("success"):
            return current

        forecast = await weather_agent.get_forecast(lat, lon, days, language=lang)
        if not forecast.get("success"):
            return forecast

        return {
            "success": True,
            "current": current,
            "forecast": forecast,
            "farming_summary": WeatherService._generate_farming_summary(current, forecast)
        }

    @staticmethod
    async def get_weather_timeline(
        lat: float,
        lon: float,
        forecast_days: int = 7,
        past_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get both recent historical days and upcoming forecast days.
        Used by the voice assistant for queries like "last week" or "next week".
        """
        return await weather_agent.get_weather_timeline(lat, lon, forecast_days, past_days)

    @staticmethod
    async def get_seasonal_rainfall(
        lat: float,
        lon: float,
        season: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get seasonal rainfall from historical reanalysis data.
        
        This matches the model's training feature (seasonal/annual rainfall)
        rather than using a short-term forecast.
        
        Args:
            lat: Latitude
            lon: Longitude
            season: "Kharif", "Rabi", or "Zaid"
            year: Year (defaults to current year)
            
        Returns:
            Dict with seasonal rainfall total and daily breakdown
        """
        return await weather_agent.get_seasonal_rainfall(lat, lon, season, year)

    @staticmethod
    async def get_annual_rainfall(
        lat: float,
        lon: float,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get annual rainfall from historical reanalysis data.
        
        Args:
            lat: Latitude
            lon: Longitude
            year: Year (defaults to previous complete year)
            
        Returns:
            Dict with annual rainfall total and daily breakdown
        """
        return await weather_agent.get_annual_rainfall(lat, lon, year)

    @staticmethod
    def _generate_farming_summary(
        current: Dict[str, Any],
        forecast: Dict[str, Any]
    ) -> str:
        """Generate farming-specific weather summary"""
        summary = []

        # Current conditions
        if "temperature_c" in current:
            temp = current["temperature_c"]
            if temp > 35:
                summary.append("High temperatures expected - ensure irrigation")
            elif temp < 15:
                summary.append("Cold conditions - protect sensitive crops")

        # Rain forecast
        forecast_days = forecast.get("forecast", [])
        rainy_days = sum(1 for day in forecast_days if day.get("rain_chance", 0) > 40)

        if rainy_days > 0:
            summary.append(f"{rainy_days} rainy days ahead - adjust irrigation schedule")
        else:
            summary.append("Dry period ahead - monitor soil moisture")

        # Wind conditions
        high_wind_days = sum(
            1 for day in forecast_days
            if day.get("wind_speed_ms", 0) > 8
        )
        if high_wind_days > 0:
            summary.append(f"{high_wind_days} windy days - delay spraying operations")

        return " | ".join(summary) if summary else "Good weather conditions for farming"
