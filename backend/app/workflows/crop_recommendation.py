"""
Crop Recommendation Workflow: fixed pipeline (soil & climate features -> ML prediction -> regional validation -> synthesis).

Mode A — "I Have Soil Report" path.
Requires real N/P/K/pH from a verified soil test report (OCR + farmer confirmation).

CRITICAL RULES:
- N/P/K/pH must come from a real lab soil test report. Never fabricated.
- Temperature/humidity from Open-Meteo. Never fabricated.
- Annual rainfall from Open-Meteo ERA5-Land (previous complete calendar year). Never fabricated.
- The ML model is the existing XGBoost classifier trained on 22 crop classes.
- Regional validation re-ranks ML output by state-level agronomic preferences.
- Rainfall > 300 mm triggers a training distribution warning (model was trained on 20–300 mm range).
"""
import structlog
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.ml_service import crop_ml_service
from app.services.regional_validation import apply as apply_regional_validation
from app.services.season_service import season_service
from app.services.weather_service import WeatherService

logger = structlog.get_logger(__name__)


class CropRecommendationInput(BaseModel):
    nitrogen: float | None = Field(default=None, description="Soil Nitrogen (N) content in kg/ha (from soil report or manual entry)")
    phosphorus: float | None = Field(default=None, description="Soil Phosphorus (P) content in kg/ha (from soil report or manual entry)")
    potassium: float | None = Field(default=None, description="Soil Potassium (K) content in kg/ha (from soil report or manual entry)")
    ph: float | None = Field(default=None, ge=0.0, le=14.0, description="Soil pH level (from soil report or manual entry)")
    temperature_c: float = Field(..., description="Average temperature in Celsius")
    humidity_pct: float = Field(..., ge=0.0, le=100.0, description="Average humidity percentage")
    rainfall_mm: float | None = Field(default=None, ge=-1.0, description="Annual rainfall in mm. Values <= 0 mean 'derive from weather'.")
    latitude: float | None = Field(default=None, description="Latitude used to derive weather-based rainfall")
    longitude: float | None = Field(default=None, description="Longitude used to derive weather-based rainfall")
    state: str | None = Field(default=None, description="State (e.g. Rajasthan)")
    language: str = Field(default="hi", description="Response language (hi, en)")


class RecommendedCropItem(BaseModel):
    crop_name: str
    confidence: float
    suitability_reason: str
    model_probability: float | None = None
    regional_score: float | None = None


class CropRecommendationResult(BaseModel):
    top_recommendation: str
    confidence: float
    alternative_crops: list[RecommendedCropItem]
    sowing_window: str
    water_requirement: str
    expected_yield: str
    farmer_message: str
    rainfall_outside_training_distribution: bool = False
    model_used: str = "XGBoost"
    data_sources: dict = {}


async def _resolve_rainfall(input_data: CropRecommendationInput) -> tuple[float, str]:
    """
    Determine the annual rainfall value used by the model.

    - If the caller supplied an explicit positive rainfall, use it as-is.
    - Otherwise, if latitude/longitude are present, derive annual rainfall from
      Open-Meteo ERA5-Land historical data for the previous complete calendar year.
    - If no location is available, return 0.0 with a warning.
    """
    if input_data.rainfall_mm is not None and input_data.rainfall_mm > 0:
        return input_data.rainfall_mm, ""

    if input_data.latitude is not None and input_data.longitude is not None:
        try:
            annual = await WeatherService.get_annual_rainfall(input_data.latitude, input_data.longitude)
            if annual.get("success"):
                total = float(annual.get("annual_rainfall_mm", annual.get("total_precipitation_mm", 0.0)))
                period = annual.get("rainfall_period", "previous year")
                return total, (
                    f"Rainfall was derived as {total:.1f} mm annual precipitation ({period}) "
                    "from Open-Meteo ERA5-Land historical reanalysis."
                )
        except Exception:
            logger.exception("weather_annual_rainfall_fetch_failed")

    return 0.0, (
        "No rainfall value was provided and annual rainfall could not be fetched for this location."
    )


# Sowing window and water requirement lookup from agronomic knowledge
_CROP_AGRO_INFO = {
    "rice": {"sowing": "June to July (Kharif season)", "water": "High (1200 - 1500 mm)", "yield": "40 - 50 quintals/hectare"},
    "maize": {"sowing": "June to July (Kharif) or Nov-Dec (Rabi)", "water": "Moderate (500 - 750 mm)", "yield": "30 - 45 quintals/hectare"},
    "chickpea": {"sowing": "October to November (Rabi)", "water": "Low (250 - 400 mm)", "yield": "15 - 20 quintals/hectare"},
    "kidneybeans": {"sowing": "June to July (Kharif)", "water": "Moderate (400 - 600 mm)", "yield": "10 - 15 quintals/hectare"},
    "pigeonpeas": {"sowing": "June to July (Kharif)", "water": "Moderate (500 - 650 mm)", "yield": "12 - 18 quintals/hectare"},
    "mothbeans": {"sowing": "July to August (Kharif)", "water": "Low (200 - 350 mm)", "yield": "5 - 8 quintals/hectare"},
    "mungbean": {"sowing": "March to April (Zaid) or July (Kharif)", "water": "Low (300 - 450 mm)", "yield": "8 - 12 quintals/hectare"},
    "blackgram": {"sowing": "June to July (Kharif)", "water": "Low (300 - 500 mm)", "yield": "8 - 12 quintals/hectare"},
    "lentil": {"sowing": "October to November (Rabi)", "water": "Low (300 - 400 mm)", "yield": "10 - 15 quintals/hectare"},
    "pomegranate": {"sowing": "February to March or June to July", "water": "Moderate (500 - 700 mm)", "yield": "100 - 150 quintals/hectare"},
    "banana": {"sowing": "June to August", "water": "High (1200 - 1800 mm)", "yield": "250 - 400 quintals/hectare"},
    "mango": {"sowing": "July to August (seedling)", "water": "Moderate (600 - 1000 mm)", "yield": "80 - 120 quintals/hectare"},
    "grapes": {"sowing": "January to February", "water": "Moderate (500 - 700 mm)", "yield": "150 - 250 quintals/hectare"},
    "watermelon": {"sowing": "February to March (Zaid)", "water": "Moderate (400 - 600 mm)", "yield": "200 - 300 quintals/hectare"},
    "muskmelon": {"sowing": "February to March (Zaid)", "water": "Moderate (400 - 600 mm)", "yield": "150 - 200 quintals/hectare"},
    "apple": {"sowing": "December to February (planting)", "water": "Moderate (600 - 800 mm)", "yield": "80 - 120 quintals/hectare"},
    "orange": {"sowing": "July to August", "water": "Moderate (600 - 900 mm)", "yield": "100 - 150 quintals/hectare"},
    "papaya": {"sowing": "June to September", "water": "Moderate (600 - 1000 mm)", "yield": "300 - 500 quintals/hectare"},
    "coconut": {"sowing": "June to September", "water": "High (1000 - 2000 mm)", "yield": "80 - 120 nuts/palm/year"},
    "cotton": {"sowing": "April to May (Kharif)", "water": "Moderate (650 - 900 mm)", "yield": "15 - 25 quintals/hectare"},
    "jute": {"sowing": "March to May", "water": "High (1200 - 1500 mm)", "yield": "20 - 30 quintals/hectare"},
    "coffee": {"sowing": "June to July (planting)", "water": "High (1000 - 2000 mm)", "yield": "8 - 12 quintals/hectare"},
}


def _get_agro_info(crop_name: str) -> dict:
    """Look up agronomic info for a crop, falling back to generic values."""
    key = crop_name.lower().strip()
    return _CROP_AGRO_INFO.get(key, {
        "sowing": "Varies by region and season",
        "water": "Moderate",
        "yield": "Varies by region",
    })


async def run_crop_recommendation_workflow(input_data: CropRecommendationInput) -> CropRecommendationResult:
    """
    Fixed pipeline:
    1. Validate real soil report values (N, P, K, pH are required)
    2. Resolve rainfall from ERA5-Land if not provided
    3. Run ML prediction using the trained XGBoost model
    4. Apply regional validation layer (state-level re-ranking)
    5. Build transparent response with data provenance
    """
    logger.info("run_crop_recommendation_start",
                n=input_data.nitrogen, p=input_data.phosphorus, k=input_data.potassium, ph=input_data.ph)

    # Step 1: Validate — soil report values are required for Mode A
    if input_data.nitrogen is None or input_data.phosphorus is None or input_data.potassium is None or input_data.ph is None:
        raise ValueError("Soil N/P/K and pH values are required from a soil test report to run crop recommendation.")

    nitrogen = input_data.nitrogen
    phosphorus = input_data.phosphorus
    potassium = input_data.potassium
    ph = input_data.ph

    # Step 2: Resolve rainfall
    rainfall_mm, rainfall_note = await _resolve_rainfall(input_data)

    # Step 3: ML model prediction using the REAL trained XGBoost model
    if not crop_ml_service.is_available():
        raise RuntimeError("Crop ML model is not available. Cannot generate recommendation.")

    ml_candidates = crop_ml_service.predict_top_candidates(
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        temperature=input_data.temperature_c,
        humidity=input_data.humidity_pct,
        ph=ph,
        rainfall=rainfall_mm,
        top_k=5,
    )

    logger.info("ml_prediction_complete",
                top_crop=ml_candidates[0]["crop_name"] if ml_candidates else "none",
                top_prob=ml_candidates[0]["probability"] if ml_candidates else 0.0,
                n_candidates=len(ml_candidates))

    # Step 4: Regional validation re-ranking
    season = season_service.get_current_season()
    ranked_candidates, regional_warnings = apply_regional_validation(
        state=input_data.state or "",
        candidates=ml_candidates,
        season=season,
    )

    if not ranked_candidates:
        raise RuntimeError("ML model returned no candidates. This should not happen with a valid feature vector.")

    # Step 5: Build response from real ML results
    top = ranked_candidates[0]
    top_crop_name = top["crop_name"]
    top_confidence = top["final_score"]
    top_agro = _get_agro_info(top_crop_name)

    alternative_crops = []
    for cand in ranked_candidates[1:4]:  # Next 3 alternatives
        agro = _get_agro_info(cand["crop_name"])
        reason_parts = [f"ML probability: {cand['model_probability']:.1%}"]
        if cand["regional_score"] != 1.0:
            reason_parts.append(f"Regional adjustment: {cand['regional_score']:.2f}x")
        alternative_crops.append(RecommendedCropItem(
            crop_name=cand["crop_name"],
            confidence=cand["final_score"],
            suitability_reason=". ".join(reason_parts),
            model_probability=cand["model_probability"],
            regional_score=cand["regional_score"],
        ))

    # Rainfall training distribution check
    outside_dist = rainfall_mm > 300.0

    # Build farmer message
    data_sources = {
        "N": f"{nitrogen} kg/ha (Soil Report)",
        "P": f"{phosphorus} kg/ha (Soil Report)",
        "K": f"{potassium} kg/ha (Soil Report)",
        "pH": f"{ph} (Soil Report)",
        "temperature": f"{input_data.temperature_c}°C",
        "humidity": f"{input_data.humidity_pct}%",
        "rainfall": f"{rainfall_mm:.1f} mm",
        "model": "XGBoost (22 crop classes)",
        "season": season,
    }

    if input_data.language == "hi":
        farmer_message = (
            f"आपकी मिट्टी की जांच (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"और मौसम के अनुसार सबसे उपयुक्त फसल **{top_crop_name}** है "
            f"(ML स्कोर: {top_confidence * 100:.0f}%)। "
            f"बुवाई का सही समय: {top_agro['sowing']}। "
            f"वैकल्पिक विकल्प: {', '.join(c.crop_name for c in alternative_crops[:2])}।"
        )
    else:
        farmer_message = (
            f"Based on your soil report (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"and climate data, the ML model recommends **{top_crop_name}** "
            f"(Score: {top_confidence * 100:.0f}%). "
            f"Optimal sowing: {top_agro['sowing']}."
        )

    if outside_dist:
        calibration_note = (
            f"Note: Annual rainfall ({rainfall_mm:.1f} mm) exceeds the ML model's dense training range (20-300 mm). "
            "The model was trained on seasonal/monthly rainfall values. Results should be interpreted with caution."
        )
        farmer_message = f"{farmer_message}\n\n{calibration_note}"

    if rainfall_note:
        farmer_message = f"{farmer_message}\n\n{rainfall_note}"

    for w in regional_warnings:
        farmer_message = f"{farmer_message}\n\n{w}"

    return CropRecommendationResult(
        top_recommendation=top_crop_name,
        confidence=top_confidence,
        alternative_crops=alternative_crops,
        sowing_window=top_agro["sowing"],
        water_requirement=top_agro["water"],
        expected_yield=top_agro["yield"],
        farmer_message=farmer_message,
        rainfall_outside_training_distribution=outside_dist,
        model_used="XGBoost",
        data_sources=data_sources,
    )
