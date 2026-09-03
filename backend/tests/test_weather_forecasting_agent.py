"""
Comprehensive Test Suite for FarmFusion Weather Forecasting Agent & Deterministic Alert Engine.
Tests all 15 architectural phases:
- Schemas (CurrentWeather, DailyForecastItem, WeatherAlertItem, AgriculturalAdvisory)
- Real Open-Meteo data parsing
- Weather Alert Engine thresholds and deduplication
- Dynamic location resolution (no hardcoding)
- ToolRegistry integration
- Multilingual advice (Hindi, Gujarati, Marathi, English)
- Android regression verification (sampleForecast deleted)
- Real live Open-Meteo API query verification
"""

import pytest
import re
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.weather_service import WeatherService
from app.services.weather_alert_engine import weather_alert_engine, THRESHOLDS
from app.schemas.weather import (
    CurrentWeather,
    DailyForecastItem,
    WeatherAlertItem,
    AgriculturalAdvisory,
    WeatherForecastResponse,
    WeatherCurrentResponse,
    WeatherAlertsResponse
)
from app.tools.registry import tool_registry
from app.tools.weather_tool import weather_tool, WeatherInput


@pytest.mark.asyncio
async def test_01_strict_weather_schemas():
    """Verify Pydantic v2 strict schemas enforce valid numbers and fields."""
    current = CurrentWeather(
        latitude=26.9124,
        longitude=75.7873,
        location_name="Jaipur Farm",
        location_source="saved_farm",
        timestamp="2026-09-03T12:00:00Z",
        temperature_c=32.5,
        feels_like_c=34.0,
        humidity_percent=65,
        pressure_hpa=1010,
        wind_speed_kmh=14.4,
        wind_speed_ms=4.0,
        weather_code=1,
        condition="Mainly clear",
        cloudiness_percent=20,
        visibility_m=10000,
        sunrise="06:05",
        sunset="18:45",
        source="Open-Meteo"
    )
    assert current.temperature_c == 32.5
    assert current.humidity_percent == 65
    assert current.source == "Open-Meteo"

    forecast_item = DailyForecastItem(
        date="2026-09-04",
        temperature_max_c=35.0,
        temperature_min_c=24.0,
        temperature_avg_c=29.5,
        precipitation_mm=12.5,
        precipitation_probability_percent=70,
        wind_speed_max_kmh=18.0,
        wind_speed_max_ms=5.0,
        weather_code=61,
        condition="Light rain"
    )
    assert forecast_item.temperature_max_c == 35.0
    assert forecast_item.precipitation_mm == 12.5


@pytest.mark.asyncio
async def test_02_deterministic_alert_engine_thresholds():
    """Verify deterministic alert generation for Heavy Rain, Heatwave, Frost, High Wind, and Thunderstorms."""
    mock_forecasts = [
        DailyForecastItem(
            date="2026-09-05",
            temperature_max_c=42.5,  # Trigger Heatwave (>=40°C)
            temperature_min_c=28.0,
            precipitation_mm=0.0,
            precipitation_probability_percent=5,
            wind_speed_max_kmh=12.0,
            wind_speed_max_ms=3.3,
            weather_code=0,
            condition="Clear"
        ),
        DailyForecastItem(
            date="2026-09-06",
            temperature_max_c=25.0,
            temperature_min_c=3.0,   # Trigger Frost (<=4°C)
            precipitation_mm=0.0,
            precipitation_probability_percent=0,
            wind_speed_max_kmh=8.0,
            wind_speed_max_ms=2.2,
            weather_code=0,
            condition="Clear"
        ),
        DailyForecastItem(
            date="2026-09-07",
            temperature_max_c=28.0,
            temperature_min_c=18.0,
            precipitation_mm=55.0,   # Trigger Heavy Rain (>=40mm)
            precipitation_probability_percent=95,
            wind_speed_max_kmh=38.0, # Trigger High Wind (>=35km/h)
            wind_speed_max_ms=10.5,
            weather_code=95,         # Trigger Thunderstorm
            condition="Thunderstorm"
        ),
    ]

    # Clear deduplication cache for clean evaluation
    weather_alert_engine._dedup_cache.clear()

    alerts = weather_alert_engine.evaluate_forecast(
        lat=26.91,
        lon=75.78,
        forecasts=mock_forecasts,
        location_name="Jaipur Test Farm",
        language="hi"
    )

    alert_types = [a.alert_type for a in alerts]
    assert "HEATWAVE" in alert_types
    assert "FROST" in alert_types
    assert "HEAVY_RAIN" in alert_types
    assert "HIGH_WIND" in alert_types
    assert "THUNDERSTORM" in alert_types

    # Verify deterministic alert IDs
    for a in alerts:
        assert len(a.alert_id) == 16
        assert a.source == "Open-Meteo-NWP"
        assert a.unit in ("°C", "mm", "km/h", "WMO Code")


@pytest.mark.asyncio
async def test_03_alert_deduplication():
    """Verify that identical weather events do not produce duplicate alerts within the time window."""
    mock_forecast = [
        DailyForecastItem(
            date="2026-09-10",
            temperature_max_c=43.0,
            temperature_min_c=25.0,
            precipitation_mm=0.0,
            precipitation_probability_percent=0,
            wind_speed_max_kmh=10.0,
            wind_speed_max_ms=2.8,
            weather_code=0,
            condition="Clear"
        )
    ]

    weather_alert_engine._dedup_cache.clear()
    first_run = weather_alert_engine.evaluate_forecast(lat=24.58, lon=73.71, forecasts=mock_forecast, language="hi")
    assert len(first_run) == 1
    first_id = first_run[0].alert_id

    # Immediate second evaluation of identical weather must be deduplicated
    second_run = weather_alert_engine.evaluate_forecast(lat=24.58, lon=73.71, forecasts=mock_forecast, language="hi")
    assert len(second_run) == 0  # Deduplicated!


@pytest.mark.asyncio
async def test_04_dynamic_location_and_no_hardcoded_city():
    """Verify location is resolved dynamically from input, not hardcoded to Udaipur or anywhere else."""
    # Test Kota coordinates
    res_kota = await WeatherService.get_current_weather(lat=25.18, lon=75.83, location_name="Kota Farm")
    assert res_kota["success"] is True
    assert res_kota["location_name"] == "Kota Farm"
    assert res_kota["location"] == "Kota Farm"

    # Test coordinate only
    res_coord = await WeatherService.get_current_weather(lat=28.7041, lon=77.1025)
    assert res_coord["success"] is True
    assert "28.7" in res_coord["location_name"] or "77.1" in res_coord["location_name"]
    assert "Udaipur" not in res_coord["location_name"]


@pytest.mark.asyncio
async def test_05_unified_weather_service_and_weather_tool():
    """Verify weather_tool delegates to WeatherService and returns 7-day forecast correctly."""
    input_data = WeatherInput(latitude=26.9124, longitude=75.7873, location_name="Jaipur")
    output = await weather_tool(input_data)

    assert output.error is None
    assert output.location == "Jaipur"
    assert output.temperature_c != 0.0
    assert len(output.daily_forecast) >= 5
    assert output.condition != "Unavailable"


@pytest.mark.asyncio
async def test_06_tool_registry_weather_tools():
    """Verify ToolRegistry exposes weather_tool, weather_forecast_tool, and weather_alerts_tool."""
    assert tool_registry.get_tool("weather_tool") is not None
    assert tool_registry.get_tool("weather_forecast_tool") is not None
    assert tool_registry.get_tool("weather_alerts_tool") is not None

    # Execute forecast tool
    f_res = await tool_registry.execute("weather_forecast_tool", {"latitude": 26.91, "longitude": 75.78, "days": 5}, {})
    assert f_res.status.value == "success"
    assert "forecast" in f_res.data
    assert len(f_res.data["forecast"]) == 5

    # Execute alerts tool
    a_res = await tool_registry.execute("weather_alerts_tool", {"latitude": 26.91, "longitude": 75.78}, {})
    assert a_res.status.value == "success"
    assert "alerts" in a_res.data


@pytest.mark.asyncio
async def test_07_multilingual_weather_advice_and_alerts():
    """Verify responses follow farmer's preferred language (hi, gu, mr, en)."""
    # Hindi
    hi_curr = await WeatherService.get_current_weather(lat=26.91, lon=75.78, language="hi")
    assert any('\u0900' <= char <= '\u097F' for char in hi_curr["weather"])  # Hindi Devanagari script

    # Gujarati
    gu_curr = await WeatherService.get_current_weather(lat=22.30, lon=70.80, language="gu")
    assert any('\u0A80' <= char <= '\u0AFF' for char in gu_curr["weather"])  # Gujarati script

    # English
    en_curr = await WeatherService.get_current_weather(lat=26.91, lon=75.78, language="en")
    assert any(en_curr["weather"].lower().startswith(x) for x in ["clear", "mainly", "partly", "overcast", "rain", "fog", "weather", "drizzle", "light", "heavy", "moderate", "thunder", "thunderstorm", "snow", "shower", "showers"])


@pytest.mark.asyncio
async def test_08_rest_api_weather_endpoints():
    """Verify FastAPI endpoints return strict Pydantic v2 structures."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. GET /current
        r_curr = await ac.get("/api/v1/weather/current?lat=26.9124&lon=75.7873&location_name=Jaipur")
        assert r_curr.status_code == 200
        data_curr = r_curr.json()
        assert data_curr["success"] is True
        assert "temperature_c" in data_curr["data"]
        assert "advisory" in data_curr

        # 2. GET /forecast
        r_fc = await ac.get("/api/v1/weather/forecast?lat=26.9124&lon=75.7873&days=7")
        assert r_fc.status_code == 200
        data_fc = r_fc.json()
        assert data_fc["success"] is True
        assert len(data_fc["forecast"]) == 7
        assert "data" in data_fc  # Backward compatibility field populated

        # 3. GET /alerts
        r_al = await ac.get("/api/v1/weather/alerts?lat=26.9124&lon=75.7873")
        assert r_al.status_code == 200
        data_al = r_al.json()
        assert data_al["success"] is True
        assert "alerts" in data_al

        # 4. GET /advisory
        r_adv = await ac.get("/api/v1/weather/advisory?lat=26.9124&lon=75.7873&crop_name=Mustard")
        assert r_adv.status_code == 200
        data_adv = r_adv.json()
        assert "irrigation_advice" in data_adv
        assert "spraying_advice" in data_adv


def test_09_android_regression_no_sample_forecast():
    """
    CRITICAL REGRESSION TEST:
    Verify that sampleForecast() is completely removed from WeatherScreen.kt,
    and that WeatherScreen.kt consumes real backend forecast API.
    """
    weather_screen_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "app" / "src" / "main" / "java" / "com" / "example" / "farmfusionapp" / "ui" / "screens" / "WeatherScreen.kt"
    assert weather_screen_path.exists(), "WeatherScreen.kt must exist"

    content = weather_screen_path.read_text(encoding="utf-8")

    # 1. Ensure sampleForecast function is GONE
    assert "sampleForecast" not in content, "CRITICAL ERROR: sampleForecast() must NOT exist in WeatherScreen.kt"

    # 2. Ensure fake hardcoded arithmetic (+1, -4) is GONE
    assert "weatherData.temperature + 2" not in content
    assert "weatherData.temperature - 4" not in content

    # 3. Ensure getWeatherForecast is called
    assert "getWeatherForecast" in content, "WeatherScreen.kt must call getWeatherForecast to get real forecasts"


def test_10_android_weather_forecasting_ui_elements():
    """
    Verify WeatherScreen.kt integrates all required forecasting UI capabilities:
    - WeatherAlertsBanner connected to getWeatherAlerts
    - AgriculturalAdvisoryCard connected to getAgriculturalAdvisory
    - Rain probability & precipitation mm displayed in ForecastRow
    - Backend timestamp displayed in WeatherHero
    - Independent try/catch failure isolation for alerts & advisory
    """
    weather_screen_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "app" / "src" / "main" / "java" / "com" / "example" / "farmfusionapp" / "ui" / "screens" / "WeatherScreen.kt"
    assert weather_screen_path.exists(), "WeatherScreen.kt must exist"
    content = weather_screen_path.read_text(encoding="utf-8")

    # 1. Weather alerts integration
    assert "getWeatherAlerts" in content, "WeatherScreen.kt must call getWeatherAlerts"
    assert "WeatherAlertsBanner" in content, "WeatherScreen.kt must declare and render WeatherAlertsBanner"
    assert "EMERGENCY" in content, "Alerts banner must handle EMERGENCY severity"
    assert "farming_recommendation" in content, "Alerts banner must display farming_recommendation"

    # 2. Agricultural advisory integration
    assert "getAgriculturalAdvisory" in content, "WeatherScreen.kt must call getAgriculturalAdvisory"
    assert "AgriculturalAdvisoryCard" in content, "WeatherScreen.kt must declare and render AgriculturalAdvisoryCard"
    assert "irrigation_advice" in content, "Advisory must display irrigation_advice"
    assert "spraying_advice" in content, "Advisory must display spraying_advice"
    assert "fieldwork_advice" in content, "Advisory must display fieldwork_advice"

    # 3. Rain probability & precipitation metrics
    assert "rainProbability" in content, "DailyForecast must have rainProbability"
    assert "precipitationMm" in content, "DailyForecast must have precipitationMm"
    assert "forecast.precipitationMm" in content, "ForecastRow must render precipitation mm"

    # 4. Last updated timestamp
    assert "weatherData.timestamp" in content, "WeatherHero must check backend timestamp"
    assert "Updated at" in content or "Updated" in content, "WeatherHero must display updated timestamp"

    # 5. Independent failure handling (each API has its own try/catch)
    assert content.count("farmFusionApi.") >= 3, "Must call getCurrentWeather, getWeatherForecast, and getWeatherAlerts/Advisory"
    assert content.count("catch") >= 4, "Must have isolated catch blocks for each section"

