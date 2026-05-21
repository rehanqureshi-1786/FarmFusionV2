from typing import Any, Dict, List

from app.agents.weather_agent import WeatherAgent


class WeatherService:
    @staticmethod
    def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
        agent = WeatherAgent()
        return agent.get_weather(latitude, longitude)

    @staticmethod
    def get_forecast(latitude: float, longitude: float, days: int) -> List[Dict[str, Any]]:
        agent = WeatherAgent()
        return agent.get_forecast(latitude, longitude, days)
