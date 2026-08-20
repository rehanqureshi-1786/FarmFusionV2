"""
No-Soil-Report Crop Recommendation Service (orchestrator).

Pipeline:
    FARMER -> No Soil Report -> Location (lat/lon) ->
    Soil Data Service (SoilGrids/ISRIC) -> Weather Service (Open-Meteo Historical) ->
    Season Engine -> XGBoost Model (top-5 proba) ->
    Regional Validation (separate layer) -> crop_agent explanation -> top 3.

Reuses existing FarmFusion components:
    - WeatherService (app/services/weather_service.py -> weather_agent)
    - CropRecommendationAgent (app/agents/crop_agent.py) for the final LLM
      explanation of the *structured* ML candidates.

Key changes from SIS India implementation:
- SoilGrids provides pH and texture (clay/sand/silt) but NOT scientifically
  compatible N/P/K (concentration vs. stock units). N/P/K from SoilGrids
  are NOT used as model inputs.
- Historical ANNUAL rainfall from Open-Meteo ERA5-Land replaces 7-day forecast.
  This matches the Kaggle Crop Recommendation Dataset training feature.
- If N/P/K cannot be obtained from a compatible source, the flow fails
  gracefully with HTTP 503 rather than fabricating values.
"""
from __future__ import annotations

import logging
from typing import Dict, List

from fastapi import HTTPException

from app.agents.crop_agent import crop_agent
from app.schemas.crop_recommendation import (
    CropCandidate,
    NoSoilReportLocation,
    NoSoilReportRequest,
    NoSoilReportResponse,
)
from app.services.ml_service import crop_ml_service
from app.services.season_service import season_service
from app.services.soil_service import soil_service
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


def _display_name(lat: float, lon: float, state) -> str:
    if state:
        return f"{state} (lat {lat:.4f}, lon {lon:.4f})"
    return f"lat {lat:.4f}, lon {lon:.4f}"


async def _resolve_weather(lat: float, lon: float, season: str) -> Dict:
    """
    Fetch temperature/humidity from current weather, and ANNUAL rainfall
    from historical reanalysis data (ERA5-Land via Open-Meteo Historical API).

    This matches the model's training feature (annual rainfall in mm)
    from the Kaggle Crop Recommendation Dataset (range ~20-298 mm).
    """
    current = await WeatherService.get_current_weather(lat, lon)
    if not current.get("success"):
        raise HTTPException(
            status_code=503,
            detail=f"Weather service unavailable: {current.get('error', 'unknown error')}",
        )

    # Get ANNUAL rainfall from historical data (previous complete calendar year)
    # This matches the Kaggle dataset's "rainfall" feature semantics
    annual_rainfall = await WeatherService.get_annual_rainfall(lat, lon)
    if not annual_rainfall.get("success"):
        raise HTTPException(
            status_code=503,
            detail=f"Historical annual rainfall unavailable: {annual_rainfall.get('error', 'unknown error')}",
        )
    rainfall = annual_rainfall.get("total_precipitation_mm", 0.0)
    rainfall_source = "Open-Meteo ERA5-Land (annual, previous calendar year)"

    temperature = current.get("temperature_c")
    humidity = current.get("humidity_percent")

    if temperature is None or humidity is None or rainfall is None:
        raise HTTPException(
            status_code=503,
            detail="Weather data is missing required fields (temperature/humidity/rainfall); cannot run the model.",
        )

    return {
        "temperature_c": float(temperature),
        "humidity_percent": float(humidity),
        "rainfall_mm": float(rainfall),
        "rainfall_source": rainfall_source,
        "current_conditions": current.get("weather"),
        "source": "open-meteo",
    }


class NoSoilCropService:
    @staticmethod
    async def recommend(request: NoSoilReportRequest) -> NoSoilReportResponse:
        lat = request.latitude
        lon = request.longitude
        state = request.state

        warnings: List[str] = []

        # 1. Soil data service (SoilGrids/ISRIC) -> pH, texture
        soil = await soil_service.get_soil_nutrients(lat, lon)
        if not soil.get("success"):
            raise HTTPException(
                status_code=503,
                detail=f"Soil information unavailable: {soil.get('error', 'unknown error')}",
            )

        # Check if N/P/K are available (they won't be with current implementation)
        if not soil.get("npk_available", False):
            # No scientifically compatible N/P/K source available via lat/lon
            # We cannot fabricate values - fail gracefully
            raise HTTPException(
                status_code=503,
                detail=(
                    "Soil nutrient data (N/P/K) is not available for this location. "
                    "The crop recommendation model requires plant-available N/P/K in kg/ha, "
                    "which cannot be reliably derived from global mapped datasets (SoilGrids) "
                    "without ground-truth calibration. "
                    "Please use the 'I Have Soil Report' flow with lab-tested values."
                ),
            )

        # 2. Add soil service warnings to response
        for w in soil.get("warnings", []):
            warnings.append(w)

        # 3. Weather service -> temperature / humidity / ANNUAL rainfall
        season = season_service.get_current_season()
        weather = await _resolve_weather(lat, lon, season)
        rainfall = weather["rainfall_mm"]

        # Using annual historical rainfall (matches training feature)
        warnings.append(
            f"Rainfall is {weather.get('rainfall_source', 'historical')} total (mm); "
            "model was trained on annual rainfall, results are indicative."
        )

        # 4. Season engine
        season_window = season_service.get_season_window(season)

        # 5. XGBoost model -> top-5 internal candidates
        if not crop_ml_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Crop recommendation ML model is not available on the server.",
            )
        candidates = crop_ml_service.predict_top_candidates(
            nitrogen=soil["N"],
            phosphorus=soil["P"],
            potassium=soil["K"],
            temperature=weather["temperature_c"],
            humidity=weather["humidity_percent"],
            ph=soil["ph"],
            rainfall=rainfall,
            top_k=5,
        )

        # 6. Regional validation (separate layer, re-ranks -> top 3)
        from app.services import regional_validation

        ranked, reg_warnings = regional_validation.apply(state, candidates, season)
        warnings.extend(reg_warnings)
        top_three = ranked[:3]

        # Build final candidate objects
        top_crops = [
            CropCandidate(
                crop_name=c["crop_name"],
                rank=c["rank"],
                model_probability=c["model_probability"],
                regional_score=c["regional_score"],
                final_score=c["final_score"],
            )
            for c in top_three
        ]

        # 7. Reuse crop_agent for the final explanation of structured candidates
        context = {
            "location": _display_name(lat, lon, state),
            "state": state,
            "season": season,
            "soil": {
                "N": soil["N"], "P": soil["P"], "K": soil["K"], "ph": soil["ph"],
            },
            "weather": {
                "temperature_c": weather["temperature_c"],
                "humidity_percent": weather["humidity_percent"],
                "rainfall_mm": rainfall,
            },
        }
        explanation = await crop_agent.explain_structured_recommendations(
            candidates=[dict(c) for c in top_crops],
            context=context,
            language="en",
        )

        # Build estimated soil response including texture info
        estimated_soil = {
            "N": soil["N"],
            "P": soil["P"],
            "K": soil["K"],
            "ph": soil["ph"],
        }
        if soil.get("texture"):
            estimated_soil["texture"] = soil["texture"]
        if soil.get("texture_class"):
            estimated_soil["texture_class"] = soil["texture_class"]
        if soil.get("depth_used"):
            estimated_soil["depth_used"] = soil["depth_used"]

        return NoSoilReportResponse(
            success=True,
            location=NoSoilReportLocation(
                latitude=lat,
                longitude=lon,
                state=state,
                display_name=_display_name(lat, lon, state),
            ),
            season=season,
            season_window=season_window,
            estimated_soil=estimated_soil,
            soil_source=soil["source"],
            weather=weather,
            top_crops=top_crops,
            explanation=explanation,
            warnings=warnings,
        )


# Module-level singleton.
no_soil_crop_service = NoSoilCropService()
