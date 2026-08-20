"""
AI Agent for Crop Recommendations using Groq API (FREE tier)
Uses Llama 3.3 70B for intelligent crop recommendations
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import CropRecommendation
from app.agents.groq_client import groq_client


class CropRecommendationAgent:
    """
    AI Agent that analyzes soil, climate, and market data to recommend crops
    Uses Groq API (free tier: 1M tokens/day)
    """

    def __init__(self):
        self.system_prompt = """You are an expert agricultural AI assistant for Indian farmers.
Your task is to analyze farm conditions and recommend suitable crops.

INPUT DATA:
- Location: {location}
- Soil Type: {soil_type}
- Annual Rainfall: {rainfall_mm}mm
- Average Temperature: {temperature_c}°C
- Farm Size: {farm_size_acres} acres
- Budget: {budget_usd} USD
- Output Language: {language}

{lang_instruction}

OUTPUT FORMAT (JSON):
{{
    "recommendations": [
        {{
            "crop_name": "Crop Name",
            "confidence_score": 0.92,
            "expected_yield_tons": 4.5,
            "market_demand": "high|medium|low",
            "estimated_profit_usd": 500,
            "growing_duration_months": 4,
            "water_requirement": "low|medium|high"
        }}
    ],
    "insights": "Natural language advice about these recommendations"
}}

RULES:
1. Recommend 3-5 crops suitable for the conditions
2. Confidence scores should be realistic (0.7-0.95)
3. Consider Indian climate and market conditions
4. Include a mix of food crops and cash crops
5. Provide practical, actionable advice

Respond ONLY with valid JSON, no markdown formatting."""

    @staticmethod
    def _lang_instruction(language: str) -> str:
        lang = (language or "en").lower().strip()
        if lang in ("hi", "mr", "gu", "pa", "te", "kn", "ta", "ml", "bn"):
            return (
                "IMPORTANT: All human-readable strings in the JSON (crop_name, insights, and any "
                "explanatory text) MUST be written in clear, simple "
                f"{lang.upper()} using the correct script for farmers. "
                "Keep market_demand as exactly one of: high, medium, low (English). "
                "Keep water_requirement as exactly one of: low, medium, high (English)."
            )
        return (
            "IMPORTANT: All human-readable strings in the JSON (crop_name, insights, and any "
            "explanatory text) MUST be written in clear English. "
            "Keep market_demand as exactly one of: high, medium, low. "
            "Keep water_requirement as exactly one of: low, medium, high."
        )

    async def get_recommendations(
        self,
        location: str,
        soil_type: str,
        rainfall_mm: float,
        temperature_c: float,
        farm_size_acres: float,
        budget_usd: Optional[float] = None,
        language: str = "en",
    ) -> tuple[List[CropRecommendation], str]:
        """
        Get AI-powered crop recommendations using Groq

        Returns:
            - List of CropRecommendation objects
            - AI-generated insights string
        """
        # Check if Groq is available
        if groq_client.is_available():
            return await self._get_groq_recommendations(
                location, soil_type, rainfall_mm, temperature_c,
                farm_size_acres, budget_usd, language
            )
        else:
            # Fallback to rule-based logic
            print("⚠️ Groq API not available, using fallback logic")
            return await self._get_fallback_recommendations(
                location, soil_type, rainfall_mm, temperature_c,
                farm_size_acres, budget_usd, language
            )

    async def _get_groq_recommendations(
        self,
        location: str,
        soil_type: str,
        rainfall_mm: float,
        temperature_c: float,
        farm_size_acres: float,
        budget_usd: Optional[float],
        language: str = "en",
    ) -> tuple[List[CropRecommendation], str]:
        """Get recommendations from Groq API"""

        # Format the prompt with actual data
        user_prompt = self.system_prompt.format(
            location=location,
            soil_type=soil_type,
            rainfall_mm=rainfall_mm,
            temperature_c=temperature_c,
            farm_size_acres=farm_size_acres,
            budget_usd=budget_usd or "Not specified",
            language=language,
            lang_instruction=self._lang_instruction(language),
        )

        # System prompt for the actual task
        system = "You are FarmFusion AI, an expert agricultural advisor. Provide detailed crop recommendations in JSON format."

        # Call Groq API
        result = await groq_client.chat_completion(
            system_prompt=system,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=2000
        )

        if not result.get("success"):
            print(f"Groq API error: {result.get('error')}")
            return await self._get_fallback_recommendations(
                location, soil_type, rainfall_mm, temperature_c,
                farm_size_acres, budget_usd, language
            )

        try:
            # Parse JSON response
            content = result["content"]
            # Remove markdown code blocks if present
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)

            # Convert to CropRecommendation objects
            recommendations = []
            for rec in data.get("recommendations", []):
                recommendations.append(CropRecommendation(
                    crop_name=rec["crop_name"],
                    confidence_score=rec["confidence_score"],
                    expected_yield_tons=rec["expected_yield_tons"] * farm_size_acres,
                    market_demand=rec["market_demand"],
                    estimated_profit_usd=rec["estimated_profit_usd"] * farm_size_acres,
                    growing_duration_months=rec["growing_duration_months"],
                    water_requirement=rec["water_requirement"]
                ))

            insights = data.get("insights", self._generate_insights(
                location, soil_type, rainfall_mm, temperature_c, recommendations, language
            ))

            return recommendations, insights

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing Groq response: {e}")
            return await self._get_fallback_recommendations(
                location, soil_type, rainfall_mm, temperature_c,
                farm_size_acres, budget_usd, language
            )

    async def _get_fallback_recommendations(
        self,
        location: str,
        soil_type: str,
        rainfall_mm: float,
        temperature_c: float,
        farm_size_acres: float,
        budget_usd: Optional[float],
        language: str = "en",
    ) -> tuple[List[CropRecommendation], str]:
        """Rule-based fallback when AI is unavailable"""

        recommendations = []

        # Soil-based recommendations
        soil_crops = {
            "clay": [
                ("Rice", 0.90, 6.0, "high", 400, 5, "high"),
                ("Wheat", 0.85, 4.5, "high", 350, 4, "medium"),
                ("Sugarcane", 0.88, 35.0, "high", 800, 12, "high"),
            ],
            "sandy": [
                ("Groundnut", 0.92, 1.8, "high", 450, 4, "low"),
                ("Watermelon", 0.87, 15.0, "medium", 500, 3, "medium"),
                ("Carrot", 0.85, 8.0, "medium", 300, 3, "medium"),
            ],
            "loamy": [
                ("Maize", 0.92, 4.5, "high", 350, 4, "medium"),
                ("Cotton", 0.88, 2.0, "high", 600, 6, "medium"),
                ("Tomatoes", 0.85, 15.0, "high", 500, 3, "medium"),
                ("Soybean", 0.86, 2.5, "high", 400, 4, "medium"),
            ],
            "silty": [
                ("Vegetables", 0.87, 10.0, "high", 400, 3, "medium"),
                ("Wheat", 0.85, 5.0, "high", 350, 4, "medium"),
                ("Barley", 0.83, 4.0, "medium", 280, 4, "medium"),
            ],
            "peaty": [
                ("Rice", 0.88, 5.5, "high", 380, 5, "high"),
                ("Cranberries", 0.82, 3.0, "medium", 450, 6, "high"),
            ],
        }

        # Get crops for the soil type
        crops = soil_crops.get(soil_type.lower(), [
            ("Sorghum", 0.78, 3.0, "medium", 250, 5, "low"),
            ("Millet", 0.75, 2.0, "medium", 200, 3, "low"),
        ])

        # Filter by rainfall
        for crop_name, conf, yield_per_acre, demand, profit_per_acre, duration, water in crops:
            if rainfall_mm < 500 and water == "high":
                continue

            recommendations.append(CropRecommendation(
                crop_name=crop_name,
                confidence_score=conf,
                expected_yield_tons=yield_per_acre * farm_size_acres,
                market_demand=demand,
                estimated_profit_usd=profit_per_acre * farm_size_acres,
                growing_duration_months=duration,
                water_requirement=water
            ))

        # Add temperature-based crop
        if temperature_c > 25 and rainfall_mm > 600:
            recommendations.append(CropRecommendation(
                crop_name="Chili Peppers",
                confidence_score=0.82,
                expected_yield_tons=8.0 * farm_size_acres,
                market_demand="high",
                estimated_profit_usd=700 * farm_size_acres,
                growing_duration_months=4,
                water_requirement="medium"
            ))

        if temperature_c > 20 and rainfall_mm > 700:
            recommendations.append(CropRecommendation(
                crop_name="Okra",
                confidence_score=0.80,
                expected_yield_tons=6.0 * farm_size_acres,
                market_demand="medium",
                estimated_profit_usd=400 * farm_size_acres,
                growing_duration_months=3,
                water_requirement="medium"
            ))

        # Generate insights
        insights = self._generate_insights(
            location, soil_type, rainfall_mm, temperature_c, recommendations, language
        )

        return recommendations, insights

    def _generate_insights(
        self,
        location: str,
        soil_type: str,
        rainfall_mm: float,
        temperature_c: float,
        recommendations: List[CropRecommendation],
        language: str = "en",
    ) -> str:
        """Generate natural language insights"""
        crop_names = ", ".join([r.crop_name for r in recommendations[:3]])
        lang = (language or "en").lower().strip()
        if lang == "hi":
            return (
                f"आपकी {location} स्थिति में {soil_type} मिट्टी, वार्षिक {rainfall_mm} मिमी वर्षा "
                f"और औसत {temperature_c}°C तापमान के आधार पर {crop_names} पर ध्यान दें। "
                "ये फसलें आपके मौसम के अनुकूल हैं और बाजार में मांग अच्छी रह सकती है। "
                "सबसे अधिक विश्वास वाली सिफारिश से शुरुआत करें, सूखे दिनों में सिंचाई देखें।"
            )
        return (
            f"Based on your {soil_type} soil in {location} with {rainfall_mm}mm annual rainfall "
            f"and average temperature of {temperature_c}°C, I recommend focusing on {crop_names}. "
            f"These crops are well-suited to your climate conditions and have strong market demand. "
            f"Consider starting with the highest confidence recommendation and diversifying "
            f"as you gain experience. Ensure proper irrigation during dry spells and monitor "
            f"weather forecasts for optimal planting times."
        )

    async def explain_structured_recommendations(
        self,
        candidates: List[Dict],
        context: Dict[str, Any],
        language: str = "en",
    ) -> str:
        """
        Generate a natural-language explanation for a set of STRUCTURED ML
        candidates (from the trained XGBoost model).

        The LLM is explicitly instructed to ONLY explain the provided candidates
        and MUST NOT invent, add, or re-rank crops on its own. If the LLM is
        unavailable, a deterministic template explanation is returned instead.
        """
        lang = (language or "en").lower().strip()
        lang_instruction = self._lang_instruction(lang)

        system_prompt = (
            "You are FarmFusion AI, an expert agricultural advisor. "
            "You are given crop candidates that came from a trained machine-learning "
            "model (XGBoost classifier) with their model probability and regional score. "
            "Your job is to EXPLAIN those exact candidates: relate the inputs "
            "(soil N/P/K/pH, temperature, humidity, rainfall, season, state) to why each "
            "crop is recommended, and give practical farming advice. "
            "STRICT RULE: do NOT add new crops, remove candidates, or change their ranking. "
            "Only describe and advise on the candidates provided."
        )
        user_prompt = (
            "STRUCTURED ML CANDIDATES (top {n}, ranked):\n"
            "{candidates}\n\n"
            "CONTEXT:\n"
            "- Location: {location}\n"
            "- State: {state}\n"
            "- Season: {season}\n"
            "- Estimated soil: N={n_val}, P={p_val}, K={k_val}, pH={ph_val}\n"
            "- Weather: {temp}\u00b0C, humidity {hum}%, rainfall {rain}mm\n\n"
            "{lang_instruction}\n\n"
            "Provide a concise, practical, farmer-facing explanation (2-4 sentences)."
        ).format(
            n=len(candidates),
            candidates=json.dumps(candidates, indent=2),
            location=context.get("location", "unknown"),
            state=context.get("state") or "not provided",
            season=context.get("season", "unknown"),
            n_val=context.get("soil", {}).get("N", "?"),
            p_val=context.get("soil", {}).get("P", "?"),
            k_val=context.get("soil", {}).get("K", "?"),
            ph_val=context.get("soil", {}).get("ph", "?"),
            temp=context.get("weather", {}).get("temperature_c", "?"),
            hum=context.get("weather", {}).get("humidity_percent", "?"),
            rain=context.get("weather", {}).get("rainfall_mm", "?"),
            lang_instruction=lang_instruction,
        )

        if groq_client.is_available():
            result = await groq_client.chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.4,
                max_tokens=800,
            )
            if result.get("success"):
                content = result["content"].strip()
                if content:
                    return content
            print(f"Groq API error in explain: {result.get('error')}")

        return self._template_explanation(candidates, context, lang)

    def _template_explanation(
        self,
        candidates: List[Dict],
        context: Dict[str, Any],
        lang: str = "en",
    ) -> str:
        """Deterministic fallback explanation when the LLM is unavailable."""
        names = ", ".join(c.get("crop_name", "?") for c in candidates[:3])
        soil = context.get("soil", {})
        season = context.get("season", "this season")

        if lang == "hi":
            return (
                f"आपकी मिट्टी (N:{soil.get('N')}, P:{soil.get('P')}, K:{soil.get('K')}, "
                f"pH:{soil.get('ph')}) और मौसम के आधार पर {season} के लिए सुझाई गई फसलें: "
                f"{names}। ये सिफारिशें प्रशिक्षित ML मॉडल और क्षेत्रीय सत्यापन पर आधारित हैं। "
                "कृपया वास्तविक स्थानीय कृषि सलाह के लिए अपने कृषि विशेषज्ञ से परामर्श करें।"
            )
        return (
            f"Based on the estimated soil (N:{soil.get('N')}, P:{soil.get('P')}, "
            f"K:{soil.get('K')}, pH:{soil.get('ph')}) and the current weather, the "
            f"recommended crops for {season} are: {names}. These recommendations come from "
            "a trained ML classifier combined with a regional validation layer. "
            "Please confirm with a local agricultural expert before large-scale sowing."
        )


# Singleton instance
crop_agent = CropRecommendationAgent()
