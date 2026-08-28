"""
No-Soil-Report Crop Recommendation Service.

Coordinates real data retrieval:
1. Open-Meteo for real-time temperature and relative humidity
2. Open-Meteo ERA5-Land for real annual rainfall (previous complete calendar year)
3. SoilGrids (ISRIC) for real coordinate-based pH and sand/clay/silt texture (0-5cm depth)
4. EnvironmentalSuitabilityService for transparent, agronomic suitability assessment

CRITICAL CONSTRAINTS:
- NEVER calls the N/P/K ML model (since N/P/K are not available without a lab soil report).
- N, P, and K are strictly marked as UNAVAILABLE.
- Never fabricates numbers, defaults, or pseudo-ML probabilities.
"""
import logging
from typing import Dict, List, Optional

from app.schemas.crop_recommendation import (
    EnvironmentalCropRecommendation,
    NoSoilReportRequest,
    NoSoilReportResponse,
    ProvenanceField,
    ProvenanceLocation,
    ProvenanceNutrients,
    ProvenanceRainfall,
    ProvenanceSoil,
    ProvenanceWeather,
)
from app.services.environmental_suitability_service import environmental_suitability_service
from app.services.season_service import season_service
from app.services.soil_service import soil_service
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


def _display_name(lat: float, lon: float, state: Optional[str], location_name: Optional[str] = None) -> str:
    if location_name and location_name.strip():
        return location_name.strip()
    if state and state.strip():
        return f"{state.strip()} ({lat:.4f}° N, {lon:.4f}° E)"
    return f"{lat:.4f}° N, {lon:.4f}° E"


class NoSoilCropService:
    @staticmethod
    async def recommend(request: NoSoilReportRequest) -> NoSoilReportResponse:
        lat = request.latitude
        lon = request.longitude
        state = request.state
        location_name = request.location_name
        soil_type = request.farmer_selected_soil_type or request.soil_type

        warnings: List[str] = []

        # 1. SoilGrids ISRIC data (pH and texture fractions at 0-5cm depth)
        soil_res = await soil_service.get_soil_nutrients(lat, lon)
        for w in soil_res.get("warnings", []):
            warnings.append(w)

        soil_available = soil_res.get("soil_data_available", False)
        ph_val = soil_res.get("ph")
        texture_dict = soil_res.get("texture") or {}
        texture_class = soil_res.get("texture_class")

        sand_val = texture_dict.get("sand")
        clay_val = texture_dict.get("clay")
        silt_val = texture_dict.get("silt")

        # 2. Weather & ERA5-Land Annual Rainfall
        season = season_service.get_current_season()
        season_window = season_service.get_season_window(season)

        current_weather = await WeatherService.get_current_weather(lat, lon)
        annual_rainfall_res = await WeatherService.get_annual_rainfall(lat, lon)

        temp_val = current_weather.get("temperature_c") if current_weather.get("success") else None
        hum_val = current_weather.get("humidity_percent") if current_weather.get("success") else None
        weather_cond = current_weather.get("weather") if current_weather.get("success") else None

        annual_rain_val = annual_rainfall_res.get("annual_rainfall_mm") if annual_rainfall_res.get("success") else None
        rainfall_period = annual_rainfall_res.get("rainfall_period", "2025")
        rainfall_source = annual_rainfall_res.get("rainfall_source", "Open-Meteo ERA5-Land")

        if annual_rain_val is not None:
            warnings.append(f"Annual Rainfall: {annual_rain_val:.1f} mm from {rainfall_source} (Period: {rainfall_period}).")

        # 3. Transparent Environmental Suitability Assessment (No ML model invocation)
        suitability_results = environmental_suitability_service.evaluate(
            temperature_c=temp_val,
            humidity_percent=hum_val,
            annual_rainfall_mm=annual_rain_val,
            soil_type=soil_type,
            ph=ph_val,
            texture=texture_dict if texture_dict else None,
            season=season,
            state=state,
        )

        recommendations: List[EnvironmentalCropRecommendation] = [
            EnvironmentalCropRecommendation(
                crop_name=item["crop_name"],
                hindi_name=item.get("hindi_name"),
                suitability_level=item["suitability_level"],
                suitability_score=item["suitability_score"],
                season=item["season"],
                water_requirement=item.get("water_requirement"),
                contributing_factors=item["contributing_factors"],
                management_notes=item["management_notes"],
            )
            for item in suitability_results
        ]

        # 4. Build Structured Provenance Objects
        loc_display = _display_name(lat, lon, state, location_name)

        loc_prov = ProvenanceLocation(
            latitude=lat,
            longitude=lon,
            display_name=loc_display,
            state=state,
            source="Device GPS",
        )

        weather_prov = ProvenanceWeather(
            temperature=ProvenanceField(
                value=temp_val,
                unit="°C",
                source="Open-Meteo" if temp_val is not None else None,
                status="REAL" if temp_val is not None else "UNAVAILABLE",
            ),
            humidity=ProvenanceField(
                value=hum_val,
                unit="%",
                source="Open-Meteo" if hum_val is not None else None,
                status="REAL" if hum_val is not None else "UNAVAILABLE",
            ),
            current_conditions=weather_cond,
            weather_available=(temp_val is not None),
        )

        rainfall_prov = ProvenanceRainfall(
            annual_rainfall=ProvenanceField(
                value=annual_rain_val,
                unit="mm",
                source=rainfall_source if annual_rain_val is not None else None,
                status="REAL" if annual_rain_val is not None else "UNAVAILABLE",
                period=rainfall_period,
            ),
            period=rainfall_period,
            rainfall_available=(annual_rain_val is not None),
        )

        soil_prov = ProvenanceSoil(
            farmer_selected_type=soil_type,
            ph=ProvenanceField(
                value=ph_val,
                unit=None,
                source="SoilGrids (ISRIC)" if ph_val is not None else None,
                status="ESTIMATED" if ph_val is not None else "UNAVAILABLE",
                estimated=True if ph_val is not None else False,
                note="Estimated from SoilGrids topsoil (0-5cm depth)" if ph_val is not None else "Unavailable",
                depth="0-5cm",
            ),
            sand=ProvenanceField(
                value=sand_val,
                unit="%",
                source="SoilGrids (ISRIC)" if sand_val is not None else None,
                status="ESTIMATED" if sand_val is not None else "UNAVAILABLE",
                estimated=True if sand_val is not None else False,
                note="Estimated from SoilGrids topsoil (0-5cm depth)" if sand_val is not None else "Unavailable",
                depth="0-5cm",
            ),
            clay=ProvenanceField(
                value=clay_val,
                unit="%",
                source="SoilGrids (ISRIC)" if clay_val is not None else None,
                status="ESTIMATED" if clay_val is not None else "UNAVAILABLE",
                estimated=True if clay_val is not None else False,
                note="Estimated from SoilGrids topsoil (0-5cm depth)" if clay_val is not None else "Unavailable",
                depth="0-5cm",
            ),
            silt=ProvenanceField(
                value=silt_val,
                unit="%",
                source="SoilGrids (ISRIC)" if silt_val is not None else None,
                status="ESTIMATED" if silt_val is not None else "UNAVAILABLE",
                estimated=True if silt_val is not None else False,
                note="Estimated from SoilGrids topsoil (0-5cm depth)" if silt_val is not None else "Unavailable",
                depth="0-5cm",
            ),
            texture_class=texture_class,
            depth_used="0-5cm",
            soil_data_available=soil_available,
        )

        nutrients_prov = ProvenanceNutrients(
            nitrogen=ProvenanceField(
                value=None,
                unit="kg/ha",
                source=None,
                status="UNAVAILABLE",
                estimated=False,
                requires_soil_test=True,
                note="Unavailable — requires laboratory soil test (Soil Health Card)",
            ),
            phosphorus=ProvenanceField(
                value=None,
                unit="kg/ha",
                source=None,
                status="UNAVAILABLE",
                estimated=False,
                requires_soil_test=True,
                note="Unavailable — requires laboratory soil test (Soil Health Card)",
            ),
            potassium=ProvenanceField(
                value=None,
                unit="kg/ha",
                source=None,
                status="UNAVAILABLE",
                estimated=False,
                requires_soil_test=True,
                note="Unavailable — requires laboratory soil test (Soil Health Card)",
            ),
        )

        soil_params_dict = {
            "ph": {
                "value": ph_val,
                "available": ph_val is not None,
                "source": "SoilGrids (ISRIC)" if ph_val is not None else None,
                "estimated": True if ph_val is not None else False,
                "note": "Estimated from SoilGrids (0-5cm depth)" if ph_val is not None else "Unavailable — requires soil test",
            },
            "nitrogen": {
                "value": None,
                "available": False,
                "source": None,
                "estimated": False,
                "requires_soil_test": True,
                "note": "Unavailable — requires laboratory soil test",
            },
            "phosphorus": {
                "value": None,
                "available": False,
                "source": None,
                "estimated": False,
                "requires_soil_test": True,
                "note": "Unavailable — requires laboratory soil test",
            },
            "potassium": {
                "value": None,
                "available": False,
                "source": None,
                "estimated": False,
                "requires_soil_test": True,
                "note": "Unavailable — requires laboratory soil test",
            },
        }

        warnings.append("N/P/K soil nutrients are unavailable without a laboratory Soil Health Card. Recommendations are based strictly on environmental suitability.")

        # Client compatibility mapping
        top_crops_compat = [
            {
                "crop_name": r.crop_name,
                "hindi_name": r.hindi_name,
                "rank": idx + 1,
                "suitability_level": r.suitability_level,
                "suitability_score": r.suitability_score,
                "water_requirement": r.water_requirement,
                "contributing_factors": r.contributing_factors,
                "management_notes": r.management_notes,
            }
            for idx, r in enumerate(recommendations[:5])
        ]

        estimated_soil_compat = {
            "soil_data_available": soil_available,
            "ph": ph_val,
            "ph_source": "SoilGrids (ISRIC)" if ph_val is not None else None,
            "ph_status": "ESTIMATED" if ph_val is not None else "UNAVAILABLE",
            "ph_note": "Estimated from SoilGrids (0-5cm depth)" if ph_val is not None else "Unavailable",
            "texture": texture_dict if texture_dict else None,
            "texture_class": texture_class,
            "depth_used": "0-5cm",
            "farmer_selected_soil": soil_type,
            "N": {"value": None, "source": None, "status": "UNAVAILABLE", "note": "Requires laboratory soil test"},
            "P": {"value": None, "source": None, "status": "UNAVAILABLE", "note": "Requires laboratory soil test"},
            "K": {"value": None, "source": None, "status": "UNAVAILABLE", "note": "Requires laboratory soil test"},
        }

        ph_desc = f"SoilGrids estimated pH (~{ph_val:.1f})" if ph_val is not None else "farmer-selected soil"

        return NoSoilReportResponse(
            success=True,
            recommendation_available=len(recommendations) > 0,
            recommendation_mode="ENVIRONMENTAL_SUITABILITY",
            reason=None if len(recommendations) > 0 else "INSUFFICIENT_ENVIRONMENTAL_DATA",
            message="Environmental suitability assessed from real GPS, weather, and soil data." if len(recommendations) > 0 else "Insufficient environmental data to assess suitability.",
            location=loc_prov,
            weather=weather_prov,
            rainfall=rainfall_prov,
            soil=soil_prov,
            nutrients=nutrients_prov,
            soil_parameters=soil_params_dict,
            recommendations=recommendations[:6],
            top_crops=top_crops_compat,
            estimated_soil=estimated_soil_compat,
            season=season,
            season_window=season_window,
            soil_source="SoilGrids (ISRIC)" if soil_available else "Not Available",
            explanation=f"Based on real location ({loc_display}), current season ({season}), Open-Meteo weather (Temp: {temp_val or '--'}°C, Humidity: {hum_val or '--'}%), ERA5-Land rainfall ({annual_rain_val or '--'} mm), and {ph_desc}, the above crops are environmentally well-suited. (Note: N/P/K are unavailable without a soil test report).",
            warnings=warnings,
        )


# Module-level singleton
no_soil_crop_service = NoSoilCropService()
