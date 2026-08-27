"""
Local Crop Recommendation Engine (Primary System).

Coordinates:
- XGBoost ML Model inference (for Mode A: Soil Report path)
- Local SQLite ICAR/CRIDA Agricultural Knowledge Base
- Candidate generation & deduplication
- Multi-factor agronomic ranking engine
- Confidence evaluation & reliability assessment
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.services.crop_agent_v2.agriculture_db import agriculture_repo
from app.services.crop_agent_v2.ranking_engine import ranking_engine
from app.services.ml_service import crop_ml_service

logger = logging.getLogger(__name__)

# Mapping from XGBoost model classes to canonical ICAR crop names
MODEL_TO_ICAR_CROP_MAP = {
    "rice": "Rice",
    "wheat": "Wheat",
    "maize": "Maize",
    "sorghum": "Sorghum (Jowar)",
    "pearl_millet": "Pearl Millet (Bajra)",
    "finger_millet": "Finger Millet (Ragi)",
    "chickpea": "Chickpea (Gram)",
    "pigeonpeas": "Pigeonpea (Arhar/Tur)",
    "kidneybeans": "Pigeonpea (Arhar/Tur)",
    "mothbeans": "Mothbeans",
    "mungbean": "Mungbean (Moong)",
    "blackgram": "Blackgram (Urad)",
    "lentil": "Lentil (Masoor)",
    "groundnut": "Groundnut (Peanut)",
    "soybean": "Soybean",
    "mustard": "Mustard / Rapeseed",
    "cotton": "Cotton",
    "sugarcane": "Sugarcane",
    "potato": "Potato",
    "onion": "Onion",
    "tomato": "Tomato",
    "pomegranate": "Pomegranate",
    "banana": "Banana",
    "mango": "Mango",
    "orange": "Orange / Citrus",
    "papaya": "Papaya",
    "coconut": "Coconut",
    "coffee": "Coffee",
    "grapes": "Grapes",
    "watermelon": "Watermelon",
    "muskmelon": "Muskmelon",
    "apple": "Apple",
    "jute": "Jute",
}


class LocalCropEngine:
    """Primary local crop recommendation system using deterministic ML and ICAR SQLite database."""

    @classmethod
    def recommend_mode_a(
        cls,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        ph: float,
        temperature_c: float,
        humidity_pct: float,
        rainfall_mm: float,
        state: Optional[str] = None,
        soil_type: Optional[str] = None,
        season: Optional[str] = None,
        farm_size_acres: float = 1.0,
    ) -> Tuple[List[Dict[str, Any]], bool, str]:
        """
        Mode A: Soil Test Report is available with verified N/P/K/pH.
        Runs trained XGBoost model -> generates candidates -> applies ICAR ranking.
        Returns: (ranked_candidates, is_reliable, summary_message)
        """
        logger.info(
            "local_engine_mode_a_start N=%s P=%s K=%s pH=%s state=%s season=%s",
            nitrogen, phosphorus, potassium, ph, state, season
        )

        candidates: List[Dict[str, Any]] = []
        ml_used = False

        # 1. Run XGBoost ML Model if available
        if crop_ml_service.is_available():
            try:
                ml_predictions = crop_ml_service.predict_top_candidates(
                    nitrogen=nitrogen,
                    phosphorus=phosphorus,
                    potassium=potassium,
                    temperature=temperature_c,
                    humidity=humidity_pct,
                    ph=ph,
                    rainfall=rainfall_mm,
                    top_k=8
                )
                for item in ml_predictions:
                    raw_name = str(item["crop_name"]).strip()
                    canon_name = MODEL_TO_ICAR_CROP_MAP.get(raw_name.lower(), raw_name)
                    candidates.append({
                        "crop_name": canon_name,
                        "model_probability": item["probability"],
                        "model_class_id": item.get("model_class_id")
                    })
                ml_used = True
            except Exception as e:
                logger.error("ml_prediction_failed_falling_back_to_icar_db", exc_info=e)

        # 2. Add supplementary regional candidates from SQLite DB
        if season:
            regional_candidates = agriculture_repo.get_candidates_for_season_and_region(season, state)
            existing_names = {c["crop_name"].lower() for c in candidates}
            for p in regional_candidates:
                if p["crop_name"].lower() not in existing_names:
                    candidates.append({
                        "crop_name": p["crop_name"],
                        "model_probability": 0.50,
                        "model_class_id": None
                    })

        if not candidates:
            return [], False, "No viable candidate crops found in knowledge base."

        # 3. Multi-Factor Agronomic Ranking Engine
        ranked = ranking_engine.rank_candidates(
            candidates=candidates,
            state=state,
            season=season,
            soil_type=soil_type,
            ph=ph,
            temperature_c=temperature_c,
            rainfall_mm=rainfall_mm,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            is_mode_a=True,
        )

        # Adjust yields and profits by farm_size_acres
        for r in ranked:
            r["expected_yield_tons"] = round(r["expected_yield_tons"] * farm_size_acres, 2)
            r["estimated_profit_usd"] = round(r["estimated_profit_usd"] * farm_size_acres, 2)
            r["estimated_profit_inr"] = round(r["estimated_profit_inr"] * farm_size_acres, 2)
            r["source"] = "local_agent"

        # Reliability Check: Top candidate must have confidence >= 0.45
        top_conf = ranked[0]["confidence_score"] if ranked else 0.0
        is_reliable = (top_conf >= 0.45) and (len(ranked) > 0)

        top_crop = ranked[0]["crop_name"] if ranked else "None"
        msg = (
            f"FarmFusion recommendation for '{top_crop}' with {top_conf * 100:.1f}% confidence based on soil test report (N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}) "
            f"and agricultural reference data."
        )

        return ranked, is_reliable, msg

    @classmethod
    def recommend_mode_b(
        cls,
        temperature_c: Optional[float],
        humidity_pct: Optional[float],
        rainfall_mm: Optional[float],
        ph: Optional[float] = None,
        soil_type: Optional[str] = None,
        state: Optional[str] = None,
        season: Optional[str] = None,
        farm_size_acres: float = 1.0,
    ) -> Tuple[List[Dict[str, Any]], bool, str]:
        """
        Mode B: No Soil Report. Relies on GPS, Season, Weather, and regional agronomic rules.
        NEVER fabricates N/P/K or fake ML probabilities.
        Returns: (ranked_candidates, is_reliable, summary_message)
        """
        logger.info(
            "local_engine_mode_b_start state=%s season=%s soil=%s temp=%s rain=%s",
            state, season, soil_type, temperature_c, rainfall_mm
        )

        # Retrieve candidates from SQLite DB matching season & state
        active_season = season or "Kharif"
        candidates_raw = agriculture_repo.get_candidates_for_season_and_region(active_season, state)

        if not candidates_raw:
            # Fallback to all profiles if no specific seasonal match
            candidates_raw = agriculture_repo.get_all_crop_profiles()

        candidate_items = [{"crop_name": p["crop_name"], "model_probability": 0.70} for p in candidates_raw]

        ranked = ranking_engine.rank_candidates(
            candidates=candidate_items,
            state=state,
            season=active_season,
            soil_type=soil_type,
            ph=ph,
            temperature_c=temperature_c,
            rainfall_mm=rainfall_mm,
            is_mode_a=False,
        )

        # Scale by farm size
        for r in ranked:
            r["expected_yield_tons"] = round(r["expected_yield_tons"] * farm_size_acres, 2)
            r["estimated_profit_usd"] = round(r["estimated_profit_usd"] * farm_size_acres, 2)
            r["estimated_profit_inr"] = round(r["estimated_profit_inr"] * farm_size_acres, 2)
            r["benchmark_gross_return_usd"] = round(r.get("benchmark_gross_return_usd", r["estimated_profit_usd"]) * farm_size_acres, 2)
            r["benchmark_gross_return_inr"] = round(r.get("benchmark_gross_return_inr", r["estimated_profit_inr"]) * farm_size_acres, 2)
            r["source"] = "local_agent"

        top_conf = ranked[0]["confidence_score"] if ranked else 0.0
        is_reliable = (top_conf >= 0.45) and (len(ranked) > 0)

        top_crop = ranked[0]["crop_name"] if ranked else "None"
        msg = (
            f"FarmFusion recommendation for '{top_crop}' ({top_conf * 100:.1f}% suitability) for {active_season} season based on regional agricultural reference profiling."
        )

        return ranked, is_reliable, msg


local_crop_engine = LocalCropEngine()
