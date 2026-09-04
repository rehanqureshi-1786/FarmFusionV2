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

    lang = input_data.language.lower() if input_data.language else "hi"
    if lang == "od":
        lang = "or"

    # Crop names dictionary for 14 languages
    crop_names_map = {
        "rice": {"hi": "धान / चावल", "mr": "भात", "gu": "ડાંગર", "pa": "ਝੋਨਾ", "bn": "ধান", "ta": "நெல்", "te": "వరి", "kn": "ಭತ್ತ", "ml": "നെല്ല്", "or": "ଧାନ", "as": "ধান", "ur": "دھان", "mai": "धान"},
        "maize": {"hi": "मक्का", "mr": "मका", "gu": "મકાઈ", "pa": "ਮੱਕੀ", "bn": "ভুট্টা", "ta": "மக்காச்சோளம்", "te": "మొక్కజొన్న", "kn": "ಮೆಕ್ಕೆಜೋಳ", "ml": "ചോളം", "or": "ମକା", "as": "মাকৈ", "ur": "مکئی", "mai": "मकई"},
        "chickpea": {"hi": "चना", "mr": "हरभरा", "gu": "ચણા", "pa": "ਛੋਲੇ", "bn": "ছোলা", "ta": "கொண்டைக்கடலை", "te": "శనగలు", "kn": "ಕಡಲೆ", "ml": "കടല", "or": "ବୁଟ", "as": "বুট", "ur": "چنا", "mai": "चना"},
        "kidneybeans": {"hi": "राजमा", "mr": "राजमा", "gu": "રાજમા", "pa": "ਰਾਜਮਾਂਹ", "bn": "রাজমা", "ta": "ராஜ்மா", "te": "రాజ్మా", "kn": "ರಾಜ್ಮಾ", "ml": "രാജ്മ", "or": "ରାଜମା", "as": "ৰাজমাহ", "ur": "ਰਾਜਮਾ", "mai": "राजमा"},
        "pigeonpeas": {"hi": "अरहर / तुअर", "mr": "तूर", "gu": "તુવેર", "pa": "ਅਰਹਰ", "bn": "অড়হর", "ta": "துவரை", "te": "కందులు", "kn": "ತೊಗರಿ", "ml": "തുവര", "or": "ହରଡ଼", "as": "অৰহৰ", "ur": "ارہر", "mai": "रहरी"},
        "mothbeans": {"hi": "मोठ", "mr": "मटकी", "gu": "મઠ", "pa": "ਮੋਠ", "bn": "মঠ কলাই", "ta": "நரிப்பயறு", "te": "బొబ్బర్లు", "kn": "ಮಡಿಕೆ ಕಾಳು", "ml": "മോത്ത് ബീൻസ്", "or": "କାନି ମୁଗ", "as": "মথ মাহ", "ur": "موٹھ", "mai": "मोठ"},
        "mungbean": {"hi": "मूंग", "mr": "मूग", "gu": "મગ", "pa": "ਮੂੰਗੀ", "bn": "মুগ", "ta": "பாசிப்பயறு", "te": "పెసలు", "kn": "ಹೆಸರು ಕಾಳು", "ml": "ചെറുപയർ", "or": "ମୁଗ", "as": "মগু মাহ", "ur": "مونگ", "mai": "मूंग"},
        "blackgram": {"hi": "उड़द", "mr": "उडीद", "gu": "અડદ", "pa": "ਮਾਂਹ", "bn": "মাষকলাই", "ta": "உளுந்து", "te": "మినుములు", "kn": "ಉದ್ದು", "ml": "ഉഴുന്ന്", "or": "ବିରି", "as": "মাটি মাহ", "ur": "ماش", "mai": "उड़िद"},
        "lentil": {"hi": "मसूर", "mr": "मसूर", "gu": "મસૂર", "pa": "ਮਸਰ", "bn": "মসুর", "ta": "மைசூர் பருப்பு", "te": "మసూర్ పప్పు", "kn": "ಮಸೂರ", "ml": "മസൂർ പരിപ്പ്", "or": "ମସୁର", "as": "মচুৰ মাহ", "ur": "مسور", "mai": "मंसूर"},
        "pomegranate": {"hi": "अनार", "mr": "डाळिंब", "gu": "દાડમ", "pa": "ਅਨਾਰ", "bn": "ডালিম", "ta": "மாதுளை", "te": "దానిమ్మ", "kn": "ದಾಳಿಂಬೆ", "ml": "മാതളനാരങ്ങ", "or": "ଡାଳିମ୍ବ", "as": "ডালিম", "ur": "انار", "mai": "अनार"},
        "banana": {"hi": "केला", "mr": "केळी", "gu": "કેળાં", "pa": "ਕੇਲਾ", "bn": "কলা", "ta": "வாழை", "te": "అరటి", "kn": "ಬಾಳೆಹಣ್ಣು", "ml": "വാഴ", "or": "କଦଳୀ", "as": "কল", "ur": "کیلا", "mai": "केरा"},
        "mango": {"hi": "आम", "mr": "आंबा", "gu": "કેરી", "pa": "ਅੰਬ", "bn": "আম", "ta": "மாம்பழம்", "te": "మామిడి", "kn": "ಮಾವು", "ml": "മാങ്ങ", "or": "ଆମ୍ବ", "as": "আম", "ur": "آم", "mai": "आम"},
        "grapes": {"hi": "अंगूर", "mr": "द्राक्षे", "gu": "દ્રાક્ષ", "pa": "ਅੰਗੂਰ", "bn": "আঙ্গুর", "ta": "திராட்சை", "te": "ద్రాక్ష", "kn": "ದ್ರಾಕ್ಷಿ", "ml": "മുന്തിരി", "or": "ଅଙ୍ଗୁର", "as": "আঙুৰ", "ur": "انگور", "mai": "अंगूर"},
        "watermelon": {"hi": "तरबूज", "mr": "कलिंगड", "gu": "તરબૂચ", "pa": "ਤਰਬੂਜ਼", "bn": "তরমুজ", "ta": "தர்பூசணி", "te": "పుచ్చకాయ", "kn": "ಕಲ್ಲಂಗಡಿ", "ml": "തണ്ണിമത്തൻ", "or": "ତରଭୁଜ", "as": "তৰমুজ", "ur": "تربوز", "mai": "तरबूज"},
        "muskmelon": {"hi": "खरबूजा", "mr": "खरबूज", "gu": "શક્કરટેટી", "pa": "ਖਰਬੂਜ਼ਾ", "bn": "ফুটি", "ta": "முலாம் பழம்", "te": "కర్బూజ", "kn": "ಖರಬೂಜ", "ml": "തയ്ക്കുമ്പളം", "or": "ଖରଭୁଜ", "as": "খাৰমুজা", "ur": "خربوزہ", "mai": "खरबूजा"},
        "apple": {"hi": "सेब", "mr": "सफरचंद", "gu": "સફરજન", "pa": "ਸੇਬ", "bn": "আপেল", "ta": "ஆப்பிள்", "te": "ఆపిల్", "kn": "ಸೇಬು", "ml": "ആപ്പിൾ", "or": "ସେଓ", "as": "আপেল", "ur": "سیب", "mai": "सेब"},
        "orange": {"hi": "संतरा", "mr": "संत्री", "gu": "સંતરાં", "pa": "ਸੰਤਰਾ", "bn": "কমলাเลবু", "ta": "ஆரஞ்சு", "te": "నారింజ", "kn": "ಕಿತ್ತಳೆ", "ml": "ഓറഞ്ച്", "or": "କମଳା", "as": "কমলা", "ur": "سنترا", "mai": "संतरा"},
        "papaya": {"hi": "पपीता", "mr": "पपई", "gu": "પપૈયું", "pa": "ਪਪੀਤਾ", "bn": "পেঁপে", "ta": "பப்பாளி", "te": "బొప్పాయి", "kn": "ಪಪ್ಪಾಯಿ", "ml": "പപ്പായ", "or": "ଅମୃତଭଣ୍ଡା", "as": "অমিতা", "ur": "پپیتا", "mai": "पपीता"},
        "coconut": {"hi": "नारियल", "mr": "नारळ", "gu": "નાળિયેર", "pa": "ਨਾਰੀਅਲ", "bn": "নারকেল", "ta": "தேங்காய்", "te": "కొబ్బరి", "kn": "ತೆಂಗಿನಕಾಯಿ", "ml": "തേങ്ങ", "or": "ନଡ଼ିଆ", "as": "নাৰিকল", "ur": "ناریل", "mai": "नारियर"},
        "cotton": {"hi": "कपास", "mr": "कापूस", "gu": "કપાસ", "pa": "ਕਪਾਹ", "bn": "তুলা", "ta": "பருத்தி", "te": "ప్రత్తి", "kn": "ಹತ್ತಿ", "ml": "പരുത്തി", "or": "କପା", "as": "কপাহ", "ur": "کپاس", "mai": "कपास"},
        "jute": {"hi": "जूट", "mr": "ताग", "gu": "શણ", "pa": "ਪਟਸਨ", "bn": "পাট", "ta": "சணல்", "te": "జనపనార", "kn": "ಸೆಣಬು", "ml": "ചണം", "or": "ଝୋଟ", "as": "মৰাপাট", "ur": "پٹ سن", "mai": "पटुआ"},
        "coffee": {"hi": "कॉफी", "mr": "कॉफी", "gu": "કોફી", "pa": "ਕੌਫੀ", "bn": "কফি", "ta": "காபி", "te": "కాఫీ", "kn": "ಕಾಫಿ", "ml": "കാപ്പി", "or": "କଫି", "as": "কফি", "ur": "کافی", "mai": "कॉफी"}
    }

    def _loc_crop(c_name: str) -> str:
        key = c_name.lower().strip()
        trans = crop_names_map.get(key, {})
        return trans.get(lang, trans.get("hi", c_name))

    localized_top_crop = _loc_crop(top_crop_name)
    localized_alt_crops = [_loc_crop(c.crop_name) for c in alternative_crops[:2]]

    if lang == "mr":
        farmer_message = (
            f"तुमच्या माती परीक्षणानुसार (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"आणि हवामानानुसार सर्वात योग्य पीक **{localized_top_crop}** आहे "
            f"(ML अचूकता: {top_confidence * 100:.0f}%)। "
            f"पेरणीची योग्य वेळ: {top_agro['sowing']}। "
            f"पर्यायी पिके: {', '.join(localized_alt_crops)}."
        )
    elif lang == "gu":
        farmer_message = (
            f"તમારા સોઇલ રિપોર્ટ (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"અને હવામાન મુજબ સૌથી શ્રેષ્ઠ પાક **{localized_top_crop}** છે "
            f"(ML સ્કોર: {top_confidence * 100:.0f}%)। "
            f"વાવણીનો યોગ્ય સમય: {top_agro['sowing']}। "
            f"વૈકલ્પિક પાક: {', '.join(localized_alt_crops)}."
        )
    elif lang == "pa":
        farmer_message = (
            f"ਤੁਹਾਡੀ ਮਿੱਟੀ ਰਿਪੋਰਟ (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"ਅਤੇ ਮੌਸਮ ਅਨੁਸਾਰ ਸਭ ਤੋਂ ਵਧੀਆ ਫਸਲ **{localized_top_crop}** ਹੈ "
            f"(ML ਸਕੋਰ: {top_confidence * 100:.0f}%)। "
            f"ਬਿਜਾਈ ਦਾ ਸਮਾਂ: {top_agro['sowing']}। "
            f"ਹੋਰ ਵਿਕਲਪ: {', '.join(localized_alt_crops)}."
        )
    elif lang == "bn":
        farmer_message = (
            f"আপনার মাটির রিপোর্ট (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"এবং আবহাওয়ার ওপর ভিত্তি করে সবচেয়ে উপযুক্ত ফসল **{localized_top_crop}** "
            f"(ML স্কোর: {top_confidence * 100:.0f}%)। "
            f"বপনের উপযুক্ত সময়: {top_agro['sowing']}। "
            f"বিকল্প ফসল: {', '.join(localized_alt_crops)}."
        )
    elif lang == "ta":
        farmer_message = (
            f"உங்கள் மண் பரிசோதனை (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"மற்றும் காலநிலைக்கு மிகவும் ஏற்ற பயிர் **{localized_top_crop}** ஆகும் "
            f"(பொருத்தம்: {top_confidence * 100:.0f}%). "
            f"விதைப்பு காலம்: {top_agro['sowing']}. "
            f"மாற்று பயிர்கள்: {', '.join(localized_alt_crops)}."
        )
    elif lang == "te":
        farmer_message = (
            f"మీ నేల పరీక్ష నివేదిక (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"మరియు వాతావరణం ప్రకారం అత్యంత అనుకూలమైన పంట **{localized_top_crop}** "
            f"(స్కోరు: {top_confidence * 100:.0f}%). "
            f"విత్తే సమయం: {top_agro['sowing']}. "
            f"ప్రత్యామ్నాయ పంటలు: {', '.join(localized_alt_crops)}."
        )
    elif lang == "kn":
        farmer_message = (
            f"ನಿಮ್ಮ ಮಣ್ಣಿನ ವರದಿ (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"ಮತ್ತು ಹವಾಮಾನದ ಪ್ರಕಾರ ಅತ್ಯಂತ ಸೂಕ್ತವಾದ ಬೆಳೆ **{localized_top_crop}** "
            f"(ಸ್ಕೋರ್: {top_confidence * 100:.0f}%). "
            f"ಬಿತ್ತನೆ ಸಮಯ: {top_agro['sowing']}. "
            f"ಪರ್ಯಾಯ ಬೆಳೆಗಳು: {', '.join(localized_alt_crops)}."
        )
    elif lang == "ml":
        farmer_message = (
            f"നിങ്ങളുടെ മണ്ണ് പരിശോധന (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"കാലാവസ്ഥ എന്നിവയ്ക്ക് ഏറ്റവും അനുയോജ്യമായ വിള **{localized_top_crop}** ആണ് "
            f"(സ്കോർ: {top_confidence * 100:.0f}%). "
            f"നടീൽ സമയം: {top_agro['sowing']}. "
            f"മറ്റ് വിളകൾ: {', '.join(localized_alt_crops)}."
        )
    elif lang == "or":
        farmer_message = (
            f"ଆପଣଙ୍କ ମାଟି ପରୀକ୍ଷା (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"ଓ ପାଣିପାଗ ଅନୁସାରେ ସର୍ବୋତ୍ତମ ଫସଲ **{localized_top_crop}** "
            f"(ସ୍କୋର: {top_confidence * 100:.0f}% )। "
            f"ବୁଣିବା ସମୟ: {top_agro['sowing']}। "
            f"ବିକଳ୍ପ ଫସଲ: {', '.join(localized_alt_crops)}."
        )
    elif lang == "as":
        farmer_message = (
            f"আপোনাৰ মাটি পৰীক্ষা (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"আৰু বতৰৰ ওপৰত ভিত্তি কৰি আটাইতকৈ উপযোগী শস্য **{localized_top_crop}** "
            f"(স্ক'ৰ: {top_confidence * 100:.0f}%)। "
            f"বীজ সিঁচাৰ সময়: {top_agro['sowing']}। "
            f"বিকল্প শস্য: {', '.join(localized_alt_crops)}."
        )
    elif lang == "ur":
        farmer_message = (
            f"آپ کی مٹی کی رپورٹ (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"اور موسم کے مطابق بہترین فصل **{localized_top_crop}** ہے "
            f"(اسکور: {top_confidence * 100:.0f}%)۔ "
            f"بوائی کا بہترین وقت: {top_agro['sowing']}۔ "
            f"متبادل فصلیں: {', '.join(localized_alt_crops)}."
        )
    elif lang == "mai":
        farmer_message = (
            f"अहाँक माटी केर जांच (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"आ मौसमक अनुसार सभ सं उपयुक्त फसल **{localized_top_crop}** अछि "
            f"(ML स्कोर: {top_confidence * 100:.0f}%)। "
            f"बोआई केर सही समय: {top_agro['sowing']}। "
            f"वैकल्पिक फसल: {', '.join(localized_alt_crops)}."
        )
    elif lang == "en":
        farmer_message = (
            f"Based on your soil report (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"and climate data, the ML model recommends **{top_crop_name}** "
            f"(Score: {top_confidence * 100:.0f}%). "
            f"Optimal sowing: {top_agro['sowing']}. "
            f"Alternative options: {', '.join(c.crop_name for c in alternative_crops[:2])}."
        )
    else:
        # Default Hindi
        farmer_message = (
            f"आपकी मिट्टी की जांच (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"और मौसम के अनुसार सबसे उपयुक्त फसल **{localized_top_crop}** है "
            f"(ML स्कोर: {top_confidence * 100:.0f}%)। "
            f"बुवाई का सही समय: {top_agro['sowing']}। "
            f"वैकल्पिक विकल्प: {', '.join(localized_alt_crops)}."
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
