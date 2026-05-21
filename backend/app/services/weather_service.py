from typing import Any, Dict

from app.agents.weather_agent import WeatherAgent


class WeatherService:
    @staticmethod
    def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
        agent = WeatherAgent()
        return agent.get_weather(latitude, longitude)
