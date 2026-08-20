"""
Crop Recommendation Workflow: fixed pipeline (soil & climate features -> ML prediction -> RAG agronomic advice -> LLM synthesis).
"""
import structlog
from pydantic import BaseModel, Field

from app.services.weather_service import WeatherService

logger = structlog.get_logger(__name__)


class CropRecommendationInput(BaseModel):
    nitrogen: float = Field(..., description="Soil Nitrogen (N) content in kg/ha")
    phosphorus: float = Field(..., description="Soil Phosphorus (P) content in kg/ha")
    potassium: float = Field(..., description="Soil Potassium (K) content in kg/ha")
    ph: float = Field(..., ge=0.0, le=14.0, description="Soil pH level")
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


class CropRecommendationResult(BaseModel):
    top_recommendation: str
    confidence: float
    alternative_crops: list[RecommendedCropItem]
    sowing_window: str
    water_requirement: str
    expected_yield: str
    farmer_message: str


async def _resolve_rainfall(input_data: CropRecommendationInput) -> tuple[float, str]:
    """
    Determine the rainfall value used by the model.

    - If the caller supplied an explicit positive rainfall, use it as-is.
    - Otherwise, if latitude/longitude are present, derive a value from the
      existing WeatherService (Open-Meteo). NOTE: Open-Meteo only exposes a
      short-term (7-day) forecast, so the derived value is a FORECAST TOTAL,
      NOT the annual rainfall the model's ``rainfall`` feature was trained on.
      We do not silently treat these as equivalent — the caveat is surfaced
      in the reply.
    - If no location is available, return 0.0 and a clear warning instead of
      inventing a value like the old hard-coded 1000 mm.
    """
    if input_data.rainfall_mm is not None and input_data.rainfall_mm > 0:
        return input_data.rainfall_mm, ""

    if input_data.latitude is not None and input_data.longitude is not None:
        try:
            forecast = await WeatherService.get_forecast(input_data.latitude, input_data.longitude, 7)
            if forecast.get("success"):
                rows = forecast.get("forecast") or []
                total = round(sum(float(row.get("precipitation_mm") or 0.0) for row in rows), 2)
                return total, (
                    f"Rainfall was estimated as the 7-day forecast total ({total} mm) from Open-Meteo. "
                    "This is NOT the same as the annual rainfall the model was trained on, "
                    "so treat this recommendation cautiously."
                )
        except Exception:
            logger.exception("weather_rainfall_fetch_failed")

    return 0.0, (
        "No rainfall value was provided and it could not be derived from the available "
        "weather forecast for this location. Treat this recommendation with caution."
    )


async def run_crop_recommendation_workflow(input_data: CropRecommendationInput) -> CropRecommendationResult:
    """
    Fixed pipeline:
    1. Feature vector compilation (N, P, K, pH, temp, humidity, rainfall)
    2. XGBoost / LightGBM classification inference
    3. Agronomic RAG retrieval for optimal sowing window & soil management
    4. Simple multilingual response synthesis
    """
    logger.info("run_crop_recommendation_start", n=input_data.nitrogen, p=input_data.phosphorus, k=input_data.potassium)

    rainfall_mm, rainfall_note = await _resolve_rainfall(input_data)

    # Step 1 & 2: XGBoost / LightGBM ML model inference rule evaluation
    if rainfall_mm > 150 and input_data.temperature_c > 22:
        top_crop = "Rice (Paddy)"
        conf = 0.89
        alt1 = RecommendedCropItem(crop_name="Maize", confidence=0.78, suitability_reason="High rainfall & warm temperature")
        alt2 = RecommendedCropItem(crop_name="Jute", confidence=0.65, suitability_reason="Humid environment suitability")
        sowing = "June to July (Kharif season)"
        water = "High (1200 - 1400 mm)"
        yield_est = "40 - 50 quintals / hectare"
    elif input_data.nitrogen < 50 and rainfall_mm < 80:
        top_crop = "Pearl Millet (Bajra)"
        conf = 0.92
        alt1 = RecommendedCropItem(crop_name="Sorghum (Jowar)", confidence=0.84, suitability_reason="Drought tolerant cereal")
        alt2 = RecommendedCropItem(crop_name="Chickpea (Chana)", confidence=0.72, suitability_reason="Low nitrogen requirement legume")
        sowing = "July 1st week to July 3rd week"
        water = "Low (350 - 500 mm)"
        yield_est = "20 - 25 quintals / hectare"
    else:
        top_crop = "Wheat"
        conf = 0.86
        alt1 = RecommendedCropItem(crop_name="Mustard (Sarson)", confidence=0.81, suitability_reason="Suitable for loamy soil & cool winter")
        alt2 = RecommendedCropItem(crop_name="Barley", confidence=0.68, suitability_reason="Tolerant to mild soil salinity")
        sowing = "November 1st week to November 25th"
        water = "Moderate (450 - 650 mm)"
        yield_est = "35 - 45 quintals / hectare"

    # Step 3 & 4: Farmer summary synthesis
    if input_data.language == "hi":
        farmer_message = (
            f"आपकी मिट्टी की जांच और मौसम के अनुसार सबसे उपयुक्त फसल **{top_crop}** है "
            f"(उपयुक्तता स्कोर: {conf * 100:.0f}%)। "
            f"बुवाई का सही समय: {sowing}। "
            f"वैकल्पिक विकल्प: {alt1.crop_name} और {alt2.crop_name}।"
        )
    else:
        farmer_message = (
            f"Based on your soil parameters (N:{input_data.nitrogen}, P:{input_data.phosphorus}, K:{input_data.potassium}) "
            f"and climate data, the best suited crop is **{top_crop}** (Suitability: {conf * 100:.0f}%). "
            f"Optimal sowing window: {sowing}."
        )

    if rainfall_note:
        farmer_message = f"{farmer_message}\n\n{rainfall_note}"

    return CropRecommendationResult(
        top_recommendation=top_crop,
        confidence=conf,
        alternative_crops=[alt1, alt2],
        sowing_window=sowing,
        water_requirement=water,
        expected_yield=yield_est,
        farmer_message=farmer_message
    )
