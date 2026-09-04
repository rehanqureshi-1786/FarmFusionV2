"""
Weather API Routes
GET /api/v1/weather/current - Real-time physical weather
GET /api/v1/weather/forecast - 1-7 day physical forecast
GET /api/v1/weather/alerts - Deterministic agronomic weather alerts
GET /api/v1/weather/advisory - Actionable agricultural weather advisory
GET /api/v1/weather/farming - Comprehensive farming weather bundle
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from datetime import datetime, timezone

from app.core.language import get_language_context, LanguageContext
from app.services.weather_service import WeatherService
from app.schemas.weather import (
    WeatherCurrentResponse,
    WeatherForecastResponse,
    WeatherAlertsResponse,
    CurrentWeather,
    DailyForecastItem,
    WeatherAlertItem,
    AgriculturalAdvisory
)
from app.schemas.disaster import (
    DisasterRiskRequest,
    DisasterRiskResponse,
    DisasterPredictionItem,
    DisasterAlertInfo,
    DisasterModelMeta
)
from app.ml.disaster.inference import disaster_predictor
from app.services.disaster_alert_service import disaster_alert_service

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=WeatherCurrentResponse)
async def get_current_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    location_name: Optional[str] = Query(None, description="Optional farm/city/village location name"),
    language: Optional[str] = Query(None, description="Language code (hi, gu, mr, pa, bn, en)"),
    lang_ctx: LanguageContext = Depends(get_language_context)
):
    """
    Get current verified physical weather observations from Open-Meteo NWP.
    """
    req_lang = language or lang_ctx.canonical_code
    try:
        weather_dict = await WeatherService.get_current_weather(
            lat=lat,
            lon=lon,
            location_name=location_name,
            language=req_lang
        )
        if not weather_dict.get("success"):
            raise HTTPException(status_code=503, detail=weather_dict.get("error", "Weather service unavailable"))

        # Strip internal keys and map to CurrentWeather
        weather_dict.pop("success", None)
        if not weather_dict.get("weather"):
            weather_dict["weather"] = weather_dict.get("condition")
        if not weather_dict.get("location"):
            weather_dict["location"] = weather_dict.get("location_name") or location_name
        current_obj = CurrentWeather(**weather_dict)

        advisory_obj = await WeatherService.get_agricultural_advisory(
            lat=lat,
            lon=lon,
            language=req_lang
        )

        return WeatherCurrentResponse(
            success=True,
            data=current_obj,
            advisory=advisory_obj
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather: {str(e)}")


@router.get("/forecast", response_model=WeatherForecastResponse)
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=7, description="Number of forecast days (1-7)"),
    location_name: Optional[str] = Query(None, description="Optional farm/city/village location name"),
    language: Optional[str] = Query(None, description="Language code"),
    lang_ctx: LanguageContext = Depends(get_language_context)
):
    """
    Get 1 to 7-day physical weather forecast from Open-Meteo NWP.
    """
    req_lang = language or lang_ctx.canonical_code
    try:
        forecast_dict = await WeatherService.get_forecast(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            language=req_lang
        )
        if not forecast_dict.get("success"):
            raise HTTPException(status_code=503, detail=forecast_dict.get("error", "Forecast service unavailable"))

        items = [DailyForecastItem(**d) for d in forecast_dict.get("forecast", [])]
        legacy_data = {
            "location": forecast_dict.get("location_name") or location_name or "",
            "forecast": [
                {
                    "date": d.date,
                    "temperature_c": d.temperature_avg_c or d.temperature_max_c,
                    "temperature_max_c": d.temperature_max_c,
                    "temperature_min_c": d.temperature_min_c,
                    "humidity_percent": 0,
                    "weather": d.condition,
                    "wind_speed_ms": d.wind_speed_max_ms,
                    "rain_chance": float(d.precipitation_probability_percent)
                } for d in items
            ],
            "farming_advice": forecast_dict.get("farming_advice") or "",
            "source": "Open-Meteo"
        }

        return WeatherForecastResponse(
            success=True,
            latitude=lat,
            longitude=lon,
            location_name=forecast_dict.get("location_name") or location_name,
            location_source=forecast_dict.get("location_source", "coordinates_only"),
            forecast_days=forecast_dict.get("forecast_days", days),
            forecast=items,
            farming_advice=forecast_dict.get("farming_advice"),
            source="Open-Meteo",
            generated_at=forecast_dict.get("generated_at", datetime.now(timezone.utc).isoformat()),
            language=req_lang,
            data=legacy_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast: {str(e)}")


@router.get("/alerts", response_model=WeatherAlertsResponse)
async def get_weather_alerts(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=7, description="Number of forecast days to evaluate"),
    location_name: Optional[str] = Query(None, description="Optional location name"),
    language: Optional[str] = Query(None, description="Language code"),
    lang_ctx: LanguageContext = Depends(get_language_context)
):
    """
    Get deterministic agronomic weather alerts (Heavy Rain, Heatwave, Frost, High Wind, Thunderstorm).
    """
    req_lang = language or lang_ctx.canonical_code
    try:
        alerts = await WeatherService.get_weather_alerts(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            language=req_lang
        )
        return WeatherAlertsResponse(
            success=True,
            count=len(alerts),
            alerts=alerts,
            checked_at=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate weather alerts: {str(e)}")


@router.get("/advisory", response_model=AgriculturalAdvisory)
async def get_agricultural_advisory(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    crop_name: Optional[str] = Query(None, description="Optional crop name (e.g. Wheat, Mustard)"),
    growth_stage: Optional[str] = Query(None, description="Optional growth stage"),
    soil_type: Optional[str] = Query(None, description="Optional soil type"),
    language: Optional[str] = Query(None, description="Language code"),
    lang_ctx: LanguageContext = Depends(get_language_context)
):
    """
    Get actionable agricultural advisory based on 3-day weather forecast.
    """
    req_lang = language or lang_ctx.canonical_code
    try:
        return await WeatherService.get_agricultural_advisory(
            lat=lat,
            lon=lon,
            crop_name=crop_name,
            growth_stage=growth_stage,
            soil_type=soil_type,
            language=req_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate agricultural advisory: {str(e)}")


@router.get("/farming")
async def get_farming_weather(
    lat: float = Query(..., description="Latitude coordinate"),
    lon: float = Query(..., description="Longitude coordinate"),
    days: int = Query(7, ge=1, le=7, description="Number of days"),
    location_name: Optional[str] = Query(None, description="Location name"),
    language: Optional[str] = Query(None, description="Language code"),
    lang_ctx: LanguageContext = Depends(get_language_context)
):
    """
    Comprehensive bundle returning current, forecast, alerts, and farming summary.
    """
    req_lang = language or lang_ctx.canonical_code
    try:
        weather = await WeatherService.get_farming_weather(
            lat=lat,
            lon=lon,
            days=days,
            location_name=location_name,
            language=req_lang
        )
        if not weather.get("success"):
            raise HTTPException(status_code=503, detail=weather.get("error", "Farming weather service unavailable"))
        return {
            "success": True,
            "data": weather
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get farming weather: {str(e)}")


@router.get("/test")
async def test_weather_api():
    """Test endpoint for weather API."""
    return {
        "success": True,
        "message": "FarmFusion Weather API is fully operational with Open-Meteo NWP & Deterministic Alert Engine.",
        "endpoints": {
            "current": "GET /api/v1/weather/current?lat=26.9124&lon=75.7873&location_name=Jaipur",
            "forecast": "GET /api/v1/weather/forecast?lat=26.9124&lon=75.7873&days=7",
            "alerts": "GET /api/v1/weather/alerts?lat=26.9124&lon=75.7873",
            "advisory": "GET /api/v1/weather/advisory?lat=26.9124&lon=75.7873&crop_name=Wheat",
            "farming": "GET /api/v1/weather/farming?lat=26.9124&lon=75.7873&days=7",
            "disaster_risk": "POST /api/v1/weather/disaster-risk"
        }
    }


@router.post("/disaster-risk", response_model=DisasterRiskResponse)
async def analyze_disaster_risk(
    body: DisasterRiskRequest,
    background_tasks: BackgroundTasks,
    lang_ctx: LanguageContext = Depends(get_language_context)
):
    """
    Evaluates disaster risk (Flood, Cyclone, Drought, Low Risk) using the DisasterPredictorAI ensemble.
    Reuses existing FarmFusion Weather Agent / Open-Meteo pipeline to avoid duplicate weather fetches.
    Triggers the existing Vobiz calling agent asynchronously if risk is HIGH or CRITICAL.
    """
    req_lang = body.language or lang_ctx.canonical_code

    # 1. Obtain weather parameters (either from explicit override or existing WeatherService)
    temperature = body.temperature
    humidity = body.humidity
    rainfall = body.rainfall
    wind_speed = body.wind_speed
    pressure = body.pressure

    resolved_location_name = body.location_name or "Farm"

    if any(param is None for param in [temperature, humidity, rainfall, wind_speed, pressure]):
        if body.lat is None or body.lon is None:
            raise HTTPException(
                status_code=400,
                detail="Either full meteorological parameters (temperature, humidity, rainfall, wind_speed, pressure) or GPS coordinates (lat, lon) must be provided."
            )

        try:
            # Fetch current physical weather
            current_weather = await WeatherService.get_current_weather(
                lat=body.lat,
                lon=body.lon,
                location_name=body.location_name,
                language=req_lang
            )
            # Fetch 2-day forecast to capture 24-48h cumulative rainfall and max wind
            forecast_data = await WeatherService.get_forecast(
                lat=body.lat,
                lon=body.lon,
                days=2,
                location_name=body.location_name,
                language=req_lang
            )

            resolved_location_name = (
                current_weather.get("location") or 
                body.location_name or 
                f"Lat {body.lat:.2f}, Lon {body.lon:.2f}"
            )

            if temperature is None:
                temperature = float(current_weather.get("temperature_c", 25.0))
            if humidity is None:
                humidity = float(current_weather.get("humidity_percent", 50.0))
            if pressure is None:
                pressure = float(current_weather.get("pressure_hpa", 1013.0))

            forecast_list = forecast_data.get("forecast", [])
            if rainfall is None:
                if forecast_list:
                    # 24-hour expected precipitation for the current day
                    rainfall = float(forecast_list[0].get("precipitation_mm", 0.0))
                else:
                    rainfall = float(current_weather.get("precipitation_mm", 0.0))

            if wind_speed is None:
                curr_wind = float(current_weather.get("wind_speed_kmh", 0.0))
                forecast_wind = max([float(day.get("wind_speed_max_kmh", 0.0)) for day in forecast_list], default=0.0)
                wind_speed = max(curr_wind, forecast_wind)

        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to retrieve weather context from Open-Meteo Weather Agent: {str(exc)}"
            )

    # 2. Run DisasterPredictorAI ML Inference
    try:
        prediction_result = disaster_predictor.predict(
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            wind_speed=wind_speed,
            pressure=pressure,
            crop_name=body.crop_name
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Disaster prediction model inference failed: {str(exc)}"
        )

    # 3. Evaluate Deterministic Alert Decision
    alert_decision = disaster_alert_service.evaluate_alert_decision(
        prediction=prediction_result,
        farmer_phone=body.farmer_phone,
        farmer_name=body.farmer_name or "Farmer",
        location_name=resolved_location_name,
        language=req_lang
    )

    # 4. Asynchronously Dispatch Vobiz Call if qualified
    call_id = None
    alert_status = alert_decision["alert_status"]
    if alert_decision["should_alert"]:
        alert_status = "TRIGGERED"
        background_tasks.add_task(
            disaster_alert_service.dispatch_vobiz_alert_async,
            decision=alert_decision,
            farmer_name=body.farmer_name or "Farmer",
            location_name=resolved_location_name,
            crop_name=body.crop_name,
            language=req_lang
        )

    # 5. Assemble Response
    pred_item = DisasterPredictionItem(
        disaster_type=prediction_result["disaster_type"],
        risk_level=prediction_result["risk_level"],
        risk_score=prediction_result["risk_score"],
        probability=prediction_result["probability"],
        confidence=prediction_result["confidence"],
        prediction_horizon=prediction_result["prediction_horizon"],
        trigger_factors=prediction_result["trigger_factors"],
        recommendations=prediction_result["recommendations"],
        probabilities=prediction_result["probabilities"],
        xgboost=prediction_result.get("xgboost")
    )

    alert_info = DisasterAlertInfo(
        should_alert=alert_decision["should_alert"],
        severity=alert_decision["severity"],
        reason=alert_decision["reason"],
        alert_status=alert_status,
        call_id=call_id,
        alert_message=alert_decision.get("alert_message"),
        cooldown_remaining_seconds=alert_decision.get("cooldown_remaining_seconds")
    )

    return DisasterRiskResponse(
        location={
            "name": resolved_location_name,
            "lat": body.lat if body.lat is not None else 0.0,
            "lon": body.lon if body.lon is not None else 0.0
        },
        weather_metrics={
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "wind_speed": round(wind_speed, 1),
            "pressure": round(pressure, 1)
        },
        predictions=[pred_item],
        alert=alert_info,
        model=DisasterModelMeta(),
        generated_at=datetime.now(timezone.utc).isoformat()
    )
