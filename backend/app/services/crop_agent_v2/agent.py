"""
FarmFusion Crop Recommendation Agent V2 (Master Orchestrator).

THE LOCAL CROP RECOMMENDATION AGENT IS THE PRIMARY SYSTEM.
GROQ IS STRICTLY A FALLBACK.

Flow:
1. Resolve location, seasonal window, and meteorological parameters.
2. Mode A (Soil Test Report) -> Local XGBoost + ICAR SQLite DB ranking.
   Mode B (No Soil Report)   -> Local ICAR Agro-climatic regional ranking.
3. Assess Confidence and Reliability:
   - If confidence >= 0.45 and candidates valid -> RETURN LOCAL RESULT (fallback_used=False).
   - If confidence < 0.45 or unhandled anomaly -> TRIGGER GROQ FALLBACK (fallback_used=True).
4. Package response with transparent data provenance.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import CropRecommendation
from app.services.crop_agent_v2.fallback_engine import fallback_engine
from app.services.crop_agent_v2.local_engine import local_crop_engine
from app.services.season_service import season_service
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


class CropRecommendationAgentV2:
    """Master agent coordinating local deterministic agronomic inference with fallback safety."""

    def __init__(self):
        self.agent_version = "2.0.0"

    async def get_recommendations(
        self,
        location: str = "Unknown Location",
        soil_type: Optional[str] = None,
        rainfall_mm: Optional[float] = None,
        temperature_c: Optional[float] = None,
        humidity_pct: Optional[float] = None,
        farm_size_acres: float = 1.0,
        budget_usd: Optional[float] = None,
        language: str = "en",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        state: Optional[str] = None,
        nitrogen: Optional[float] = None,
        phosphorus: Optional[float] = None,
        potassium: Optional[float] = None,
        ph: Optional[float] = None,
        force_fallback: bool = False,
    ) -> Tuple[List[CropRecommendation], str, Dict[str, Any]]:
        """
        Unified entrypoint for crop recommendation.

        Returns:
            (recommendations_list, insights_message, metadata_dict)
        """
        logger.info(
            "crop_agent_v2_recommend_start location=%s state=%s N=%s P=%s K=%s pH=%s temp=%s rain=%s",
            location, state, nitrogen, phosphorus, potassium, ph, temperature_c, rainfall_mm
        )

        # 1. Resolve Season
        current_season = season_service.get_current_season()
        season_window = season_service.get_season_window(current_season)

        # 2. Derive Weather/Rainfall if coordinates provided and parameters missing
        if latitude is not None and longitude is not None:
            if temperature_c is None or humidity_pct is None:
                try:
                    w_res = await WeatherService.get_current_weather(latitude, longitude)
                    if w_res.get("success"):
                        temperature_c = temperature_c or w_res.get("temperature_c")
                        humidity_pct = humidity_pct or w_res.get("humidity_percent")
                except Exception as e:
                    logger.warning("failed_to_fetch_weather_for_crop_agent", exc_info=e)

            if rainfall_mm is None or rainfall_mm <= 0:
                try:
                    r_res = await WeatherService.get_annual_rainfall(latitude, longitude)
                    if r_res.get("success"):
                        rainfall_mm = float(r_res.get("annual_rainfall_mm", 0.0))
                except Exception as e:
                    logger.warning("failed_to_fetch_rainfall_for_crop_agent", exc_info=e)

        # Defaults for climate if still unresolved
        temp_resolved = temperature_c if temperature_c is not None else 26.0
        hum_resolved = humidity_pct if humidity_pct is not None else 65.0
        rain_resolved = rainfall_mm if rainfall_mm is not None else 650.0

        # 3. Determine Execution Mode
        is_mode_a = (
            nitrogen is not None and phosphorus is not None and
            potassium is not None and ph is not None
        )

        ranked_results: List[Dict[str, Any]] = []
        is_reliable: bool = False
        summary_msg: str = ""
        fallback_used: bool = False
        recommendation_source: str = "local_agent"
        fallback_reason: Optional[str] = None

        # 4. PRIMARY EXECUTION: Local Crop Recommendation Agent
        if not force_fallback:
            try:
                if is_mode_a:
                    ranked_results, is_reliable, summary_msg = local_crop_engine.recommend_mode_a(
                        nitrogen=nitrogen,
                        phosphorus=phosphorus,
                        potassium=potassium,
                        ph=ph,
                        temperature_c=temp_resolved,
                        humidity_pct=hum_resolved,
                        rainfall_mm=rain_resolved,
                        state=state,
                        soil_type=soil_type,
                        season=current_season,
                        farm_size_acres=farm_size_acres,
                    )
                else:
                    ranked_results, is_reliable, summary_msg = local_crop_engine.recommend_mode_b(
                        temperature_c=temp_resolved,
                        humidity_pct=hum_resolved,
                        rainfall_mm=rain_resolved,
                        ph=ph,
                        soil_type=soil_type,
                        state=state,
                        season=current_season,
                        farm_size_acres=farm_size_acres,
                    )
            except Exception as e:
                logger.error("local_crop_engine_error_triggering_fallback", exc_info=e)
                is_reliable = False
                fallback_reason = f"Local engine execution error: {str(e)}"

        # 5. FALLBACK LAYER: Only when local result is unreliable, empty, or force requested
        if not is_reliable or len(ranked_results) == 0 or force_fallback:
            fallback_used = True
            recommendation_source = "groq_fallback"
            if not fallback_reason:
                fallback_reason = (
                    "Local engine confidence score below reliability threshold (< 0.45) "
                    "or candidate set empty."
                )

            logger.info("triggering_groq_fallback reason=%s", fallback_reason)

            fallback_recs, fallback_insights, fb_success = await fallback_engine.generate_fallback_recommendations(
                location=location,
                state=state,
                season=current_season,
                soil_type=soil_type,
                temperature_c=temp_resolved,
                humidity_pct=hum_resolved,
                rainfall_mm=rain_resolved,
                farm_size_acres=farm_size_acres,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                ph=ph,
                fallback_reason=fallback_reason,
                language=language,
            )

            ranked_results = fallback_recs
            summary_msg = fallback_insights
            is_reliable = fb_success

        # 6. Format to Standard Pydantic CropRecommendation objects
        final_recommendations: List[CropRecommendation] = []
        for item in ranked_results[:5]:
            final_recommendations.append(
                CropRecommendation(
                    crop_name=item.get("crop_name", "Unknown"),
                    confidence_score=round(float(item.get("confidence_score", 0.70)), 2),
                    expected_yield_tons=round(float(item.get("expected_yield_tons", 2.5)), 2),
                    market_demand=str(item.get("market_demand", "medium")).lower(),
                    estimated_profit_usd=round(float(item.get("estimated_profit_usd", 350.0)), 2),
                    growing_duration_months=int(round(float(item.get("growing_duration_months", 4.0)))),
                    water_requirement=str(item.get("water_requirement", "Medium")).split(" ")[0].lower()
                )
            )

        # 7. Generate Local Farmer Message / Insights if not from fallback
        if not fallback_used and ranked_results:
            top_rec = ranked_results[0]
            top_name = top_rec.get("crop_name", "")
            top_hindi = top_rec.get("hindi_name", "")
            top_conf_pct = int(top_rec.get("confidence_score", 0.7) * 100)
            alt_names = ", ".join(r.get("crop_name", "") for r in ranked_results[1:3] if r.get("crop_name"))

            if language.lower().strip() == "hi":
                summary_msg = (
                    f"आपके क्षेत्र ({state or location}) और वर्तमान {current_season} मौसम के अनुसार, "
                    f"कृषि संदर्भ डेटा के आधार पर FarmFusion सिफारिश: **{top_name} ({top_hindi})** "
                    f"(मॉडल संरेखण विश्वास: {top_conf_pct}%)। "
                    f"सिंचाई की आवश्यकता: {top_rec.get('water_requirement', 'मध्यम')}। "
                    f"वैकल्पिक फसलें: {alt_names or 'उपलब्ध नहीं'}।"
                )
            else:
                summary_msg = (
                    f"FarmFusion recommendation based on agricultural reference data for {state or location} in the {current_season} season: "
                    f"**{top_name}** ({top_conf_pct}% model alignment confidence). "
                    f"Water requirement: {top_rec.get('water_requirement', 'Moderate')}. "
                    f"Alternative options: {alt_names or 'None'}."
                )

        # 8. Provenance & Operational Metadata
        metadata = {
            "version": self.agent_version,
            "recommendation_source": recommendation_source,
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
            "is_reliable": is_reliable,
            "confidence_tier": ranked_results[0].get("confidence_tier", "medium") if ranked_results else "unclear",
            "confidence_disclaimer": "Confidence scores represent heuristic model alignment with agro-climatic parameters, not guaranteed crop yield or production certainty.",
            "economic_data_status": "benchmark_estimate_not_live_price",
            "economic_disclaimer": "Economic return values represent approximate gross historical benchmarks for planning only. NOT live mandi prices or guaranteed profit.",
            "season": current_season,
            "season_window": season_window,
            "mode": "MODE_A_SOIL_REPORT" if is_mode_a else "MODE_B_NO_SOIL_REPORT",
            "candidate_count": len(ranked_results),
            "top_crop": ranked_results[0].get("crop_name") if ranked_results else None,
            "raw_candidates": ranked_results[:5]
        }

        return final_recommendations, summary_msg, metadata


# Singleton Agent V2 instance
crop_agent_v2 = CropRecommendationAgentV2()
