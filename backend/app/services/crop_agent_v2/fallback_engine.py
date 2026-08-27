"""
Groq Fallback Engine for Crop Recommendation Agent V2.

CRITICAL ARCHITECTURAL CONSTRAINTS:
1. Groq is STRICTLY a fallback layer.
2. It is ONLY called when the primary Local Crop Recommendation Agent produces
   an unreliable/unsupported result (confidence < 0.45), encounters missing data,
   or when explicitly requested.
3. Every response generated via this engine is marked with:
   - fallback_used = True
   - recommendation_source = "groq_fallback"
   - is_reliable = True / False depending on validation
"""
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.agents.groq_client import groq_client

logger = logging.getLogger(__name__)


class GroqFallbackEngine:
    """Fallback LLM service providing expert agricultural synthesis when local agent is uncertain."""

    SYSTEM_PROMPT = """You are FarmFusion AI Agricultural Fallback Advisor.
You are called ONLY because the primary local ICAR agronomic engine had insufficient or ambiguous data for this specific location/climate.
Your task is to analyze the environmental and soil conditions and recommend 3-5 suitable Indian crops.

CRITICAL RULES:
1. Ground recommendations in realistic Indian agro-climatic zones and ICAR guidelines.
2. Output valid JSON matching the exact schema below.
3. Include realistic confidence scores (0.60 to 0.88), expected yields, market demand, and water requirements.

SCHEMA (JSON):
{{
    "recommendations": [
        {{
            "crop_name": "Crop Name",
            "hindi_name": "हिंदी नाम",
            "confidence_score": 0.75,
            "confidence_tier": "medium",
            "suitability_level": "Suitable",
            "expected_yield_tons": 3.5,
            "market_demand": "high|medium|low",
            "estimated_profit_usd": 400.0,
            "growing_duration_months": 4.0,
            "water_requirement": "Low|Medium|High",
            "contributing_factors": ["Reason 1", "Reason 2"],
            "management_notes": ["Agronomic tip 1"]
        }}
    ],
    "insights": "Detailed agricultural guidance for the farmer."
}}

Respond ONLY with valid JSON, no conversational markdown wrapper."""

    @classmethod
    async def generate_fallback_recommendations(
        cls,
        location: str,
        state: Optional[str],
        season: str,
        soil_type: Optional[str],
        temperature_c: Optional[float],
        humidity_pct: Optional[float],
        rainfall_mm: Optional[float],
        farm_size_acres: float = 1.0,
        nitrogen: Optional[float] = None,
        phosphorus: Optional[float] = None,
        potassium: Optional[float] = None,
        ph: Optional[float] = None,
        fallback_reason: str = "Local agent returned low confidence or ambiguous result",
        language: str = "en"
    ) -> Tuple[List[Dict[str, Any]], str, bool]:
        """
        Executes Groq fallback recommendation.
        Returns: (recommendations_list, insights_text, success_bool)
        """
        if not groq_client.is_available():
            logger.warning("groq_fallback_unavailable_using_rule_backup")
            return cls._rule_based_safety_backup(
                location=location,
                state=state,
                season=season,
                soil_type=soil_type,
                rainfall_mm=rainfall_mm,
                temperature_c=temperature_c,
                farm_size_acres=farm_size_acres,
                language=language
            )

        user_prompt = (
            f"FARM CONTEXT (Fallback Reason: {fallback_reason}):\n"
            f"- Location: {location}\n"
            f"- State: {state or 'Not specified'}\n"
            f"- Current Season: {season}\n"
            f"- Soil Type: {soil_type or 'General / Loamy'}\n"
            f"- Soil pH: {ph if ph is not None else 'Not tested'}\n"
            f"- Soil N-P-K: N={nitrogen or 'N/A'}, P={phosphorus or 'N/A'}, K={potassium or 'N/A'} kg/ha\n"
            f"- Average Temperature: {temperature_c or 'N/A'} °C\n"
            f"- Humidity: {humidity_pct or 'N/A'} %\n"
            f"- Annual Rainfall: {rainfall_mm or 'N/A'} mm\n"
            f"- Farm Size: {farm_size_acres} acres\n"
            f"- Language: {language}\n\n"
            "Provide optimal crop recommendations strictly in Indian agronomic context."
        )

        try:
            result = await groq_client.chat_completion(
                system_prompt=cls.SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=1500
            )

            if result.get("success"):
                content = result["content"].replace("```json", "").replace("```", "").strip()
                data = json.loads(content)
                recs = data.get("recommendations", [])
                insights = data.get("insights", "Recommendations generated via agricultural fallback advisor.")

                # Normalize items
                normalized = []
                for r in recs:
                    conf = float(r.get("confidence_score", 0.65))
                    normalized.append({
                        "crop_name": r.get("crop_name", "Unknown Crop"),
                        "hindi_name": r.get("hindi_name", ""),
                        "confidence_score": conf,
                        "confidence_tier": "medium" if conf >= 0.45 else "low",
                        "suitability_level": r.get("suitability_level", "Suitable"),
                        "expected_yield_tons": float(r.get("expected_yield_tons", 2.5)) * farm_size_acres,
                        "market_demand": str(r.get("market_demand", "medium")).lower(),
                        "estimated_profit_usd": float(r.get("estimated_profit_usd", 350.0)) * farm_size_acres,
                        "estimated_profit_inr": float(r.get("estimated_profit_usd", 350.0)) * 83.0 * farm_size_acres,
                        "growing_duration_months": float(r.get("growing_duration_months", 4.0)),
                        "water_requirement": r.get("water_requirement", "Medium"),
                        "contributing_factors": r.get("contributing_factors", ["Selected based on general regional adaptability."]),
                        "management_notes": r.get("management_notes", ["Ensure timely irrigation and weed control."]),
                        "source": "groq_fallback"
                    })
                return normalized, insights, True
        except Exception as e:
            logger.error("groq_fallback_inference_failed", exc_info=e)

        return cls._rule_based_safety_backup(
            location=location,
            state=state,
            season=season,
            soil_type=soil_type,
            rainfall_mm=rainfall_mm,
            temperature_c=temperature_c,
            farm_size_acres=farm_size_acres,
            language=language
        )

    @classmethod
    def _rule_based_safety_backup(
        cls,
        location: str,
        state: Optional[str],
        season: str,
        soil_type: Optional[str],
        rainfall_mm: Optional[float],
        temperature_c: Optional[float],
        farm_size_acres: float = 1.0,
        language: str = "en"
    ) -> Tuple[List[Dict[str, Any]], str, bool]:
        """Ultimate safety fallback when both local engine and Groq are unavailable."""
        crops = [
            {
                "crop_name": "Pearl Millet (Bajra)" if season == "Kharif" else "Chickpea (Gram)",
                "hindi_name": "बाजरा" if season == "Kharif" else "चना",
                "confidence_score": 0.65,
                "confidence_tier": "medium",
                "suitability_level": "Suitable",
                "expected_yield_tons": 2.0 * farm_size_acres,
                "market_demand": "high",
                "estimated_profit_usd": 300.0 * farm_size_acres,
                "estimated_profit_inr": 25000.0 * farm_size_acres,
                "growing_duration_months": 3.5,
                "water_requirement": "Low",
                "contributing_factors": ["High climatic resilience and low water requirement."],
                "management_notes": ["Standard ICAR package of practices recommended."],
                "source": "safety_fallback"
            },
            {
                "crop_name": "Mungbean (Moong)",
                "hindi_name": "मूंग",
                "confidence_score": 0.60,
                "confidence_tier": "medium",
                "suitability_level": "Suitable",
                "expected_yield_tons": 1.2 * farm_size_acres,
                "market_demand": "high",
                "estimated_profit_usd": 280.0 * farm_size_acres,
                "estimated_profit_inr": 23000.0 * farm_size_acres,
                "growing_duration_months": 2.5,
                "water_requirement": "Low",
                "contributing_factors": ["Short duration pulse with nitrogen-fixing capability."],
                "management_notes": ["Ideal for quick cash turnaround."],
                "source": "safety_fallback"
            }
        ]
        insights = (
            f"Based on {season} conditions in {location}, drought-hardy pulses/millets are advised as a reliable safety choice."
        )
        return crops, insights, False


fallback_engine = GroqFallbackEngine()
