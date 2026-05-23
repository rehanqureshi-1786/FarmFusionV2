"""
Weather agent powered by Open-Meteo.
Uses a free no-key weather API and returns normalized weather data for the app.
"""
from datetime import datetime
from typing import Any, Dict, List

import httpx


class WeatherAgent:
    def __init__(self) -> None:
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def is_available(self) -> bool:
        return True

    async def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            payload = await self._fetch_weather_bundle(lat, lon, forecast_days=1, past_days=0)
            current = payload.get("current", {})
            daily = payload.get("daily", {})

            sunrise = daily.get("sunrise", [None])[0]
            sunset = daily.get("sunset", [None])[0]
            temperature = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind_speed = current.get("wind_speed_10m")
            weather_code = current.get("weather_code")

            return {
                "success": True,
                "location": "",
                "temperature_c": temperature,
                "feels_like_c": current.get("apparent_temperature", temperature),
                "humidity_percent": int(humidity or 0),
                "pressure_hpa": int(current.get("pressure_msl") or 0),
                "weather": self._weather_code_to_text(weather_code),
                "wind_speed_ms": self._kmh_to_ms(current.get("wind_speed_10m")),
                "visibility_m": int(current.get("visibility") or 10000),
                "cloudiness_percent": int(current.get("cloud_cover") or 0),
                "sunrise": sunrise,
                "sunset": sunset,
                "farming_advice": self._generate_farming_advice(
                    temperature_c=temperature,
                    humidity_percent=humidity,
                    wind_speed_kmh=current.get("wind_speed_10m"),
                    weather_code=weather_code
                ),
                "source": "open-meteo"
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Open-Meteo weather request failed: {str(exc)}",
                "source": "open-meteo"
            }

    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> Dict[str, Any]:
        try:
            payload = await self._fetch_weather_bundle(lat, lon, forecast_days=days, past_days=0)
            daily = payload.get("daily", {})
            forecasts = self._build_daily_rows(daily, days)

            return {
                "success": True,
                "location": "",
                "forecast": forecasts,
                "farming_advice": self._generate_forecast_advice(forecasts),
                "source": "open-meteo"
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Open-Meteo forecast request failed: {str(exc)}",
                "source": "open-meteo"
            }

    async def get_weather_timeline(
        self,
        lat: float,
        lon: float,
        forecast_days: int = 7,
        past_days: int = 7
    ) -> Dict[str, Any]:
        try:
            payload = await self._fetch_weather_bundle(
                lat,
                lon,
                forecast_days=forecast_days,
                past_days=past_days
            )
            daily = payload.get("daily", {})
            rows = self._build_daily_rows(daily, len(daily.get("time", [])))
            history = rows[:past_days]
            forecast = rows[past_days:past_days + forecast_days]

            return {
                "success": True,
                "history": history,
                "forecast": forecast,
                "source": "open-meteo"
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Open-Meteo timeline request failed: {str(exc)}",
                "source": "open-meteo"
            }

    async def _fetch_weather_bundle(
        self,
        lat: float,
        lon: float,
        forecast_days: int,
        past_days: int
    ) -> Dict[str, Any]:
        params = {
            "latitude": lat,
            "longitude": lon,
            "timezone": "auto",
            "forecast_days": forecast_days,
            "past_days": past_days,
            "current": ",".join([
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "pressure_msl",
                "weather_code",
                "wind_speed_10m",
                "visibility",
                "cloud_cover",
            ]),
            "daily": ",".join([
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "sunrise",
                "sunset",
            ]),
        }

        async with httpx.AsyncClient(trust_env=False, timeout=20.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()

    def _build_daily_rows(self, daily: Dict[str, List[Any]], count: int) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for i in range(count):
            max_temp = daily.get("temperature_2m_max", [0])[i]
            min_temp = daily.get("temperature_2m_min", [0])[i]
            avg_temp = ((max_temp or 0) + (min_temp or 0)) / 2
            rows.append({
                "date": daily.get("time", [None])[i],
                "temperature_c": avg_temp,
                "humidity_percent": 0,
                "weather": self._weather_code_to_text(daily.get("weather_code", [0])[i]),
                "wind_speed_ms": self._kmh_to_ms(daily.get("wind_speed_10m_max", [0])[i]),
                "rain_chance": float(daily.get("precipitation_probability_max", [0])[i] or 0),
                "precipitation_mm": float(daily.get("precipitation_sum", [0])[i] or 0),
                "temperature_max_c": max_temp,
                "temperature_min_c": min_temp,
            })
        return rows

    def _generate_farming_advice(
        self,
        temperature_c: float | None,
        humidity_percent: float | None,
        wind_speed_kmh: float | None,
        weather_code: int | None
    ) -> str:
        advice: List[str] = []

        if temperature_c is not None:
            if temperature_c > 35:
                advice.append("High temperature - ensure irrigation")
            elif temperature_c < 15:
                advice.append("Cool conditions - protect sensitive crops")

        if humidity_percent is not None:
            if humidity_percent > 80:
                advice.append("High humidity - watch for fungal disease")
            elif humidity_percent < 30:
                advice.append("Low humidity - monitor soil moisture")

        if wind_speed_kmh is not None and wind_speed_kmh > 20:
            advice.append("Windy conditions - delay spraying")

        if weather_code is not None and weather_code in {61, 63, 65, 80, 81, 82, 95, 96, 99}:
            advice.append("Rain likely - avoid spraying before showers")

        return " | ".join(advice) if advice else "Good weather conditions for farm work"

    def _generate_forecast_advice(self, forecasts: List[Dict[str, Any]]) -> str:
        rainy_days = sum(1 for day in forecasts if day.get("rain_chance", 0) >= 40 or day.get("precipitation_mm", 0) > 1)
        hot_days = sum(1 for day in forecasts if day.get("temperature_max_c", 0) > 35)

        advice: List[str] = []
        if rainy_days:
            advice.append(f"{rainy_days} rainy day(s) expected. Plan spraying around dry windows.")
        if hot_days:
            advice.append(f"{hot_days} hot day(s) ahead. Keep irrigation ready.")

        return " ".join(advice) if advice else "Stable weather expected. Good for field operations."

    def _weather_code_to_text(self, code: int | None) -> str:
        mapping = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "fog",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "drizzle",
            55: "dense drizzle",
            61: "light rain",
            63: "rain",
            65: "heavy rain",
            71: "light snow",
            73: "snow",
            75: "heavy snow",
            80: "rain showers",
            81: "rain showers",
            82: "heavy rain showers",
            95: "thunderstorm",
            96: "thunderstorm with hail",
            99: "severe thunderstorm with hail",
        }
        return mapping.get(code or 0, "weather update available")

    def _kmh_to_ms(self, speed_kmh: float | None) -> float:
        if speed_kmh is None:
            return 0.0
        return round(float(speed_kmh) / 3.6, 2)


weather_agent = WeatherAgent()
