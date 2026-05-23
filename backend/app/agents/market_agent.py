"""
AI Agent for Market Price Predictions
Uses Groq API (FREE tier) for price trend analysis
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.agents.groq_client import groq_client


class MarketAnalysisAgent:
    """
    AI Agent for predicting market prices and trends
    Uses Groq API for intelligent analysis
    """

    def __init__(self):
        # Sample market data (in production, fetch from APIs)
        self.market_data = {
            "rice": {"base_price": 25, "volatility": "low"},
            "wheat": {"base_price": 22, "volatility": "low"},
            "maize": {"base_price": 18, "volatility": "medium"},
            "cotton": {"base_price": 65, "volatility": "high"},
            "tomatoes": {"base_price": 20, "volatility": "high"},
            "potatoes": {"base_price": 15, "volatility": "medium"},
            "soybean": {"base_price": 35, "volatility": "medium"},
            "groundnut": {"base_price": 55, "volatility": "medium"},
            "sugarcane": {"base_price": 3.5, "volatility": "low"},
        }

    async def predict_prices(
        self,
        crop_name: str,
        region: str,
        current_price: float,
        prediction_months: int = 3,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Predict market prices for the next N months
        """
        if groq_client.is_available():
            return await self._predict_with_groq(
                crop_name, region, current_price, prediction_months, historical_data
            )
        else:
            return self._predict_with_rules(
                crop_name, region, current_price, prediction_months
            )

    async def _predict_with_groq(
        self,
        crop_name: str,
        region: str,
        current_price: float,
        prediction_months: int,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Use Groq AI for price prediction with historical context"""

        historical_str = ""
        if historical_data:
            historical_str = "RECENT HISTORICAL DATA (from local records):\n"
            for d in historical_data[:10]:
                historical_str += f"- Date: {d['date']}, Modal Price: {d['price']}, District: {d['district']}\n"

        system_prompt = f"""You are an elite Pan-India Agricultural Market Analyst.
Your goal is to provide deep, predictive insights for crop prices across the entire Indian market, including national trends, seasonal shifts in different states, and the impact of national supply/demand.

When a region like "All India" or "National" is provided, analyze the nationwide average and major trading zones.
{historical_str}

OUTPUT FORMAT (JSON):
{{
    "commodity": "{crop_name}",
    "region": "{region}",
    "current_price": {current_price},
    "predictions": [
        {{"month": "Next Month", "predicted_price": 26.5, "trend": "rising", "confidence": 0.82}},
        {{"month": "Month 2", "predicted_price": 27.0, "trend": "rising", "confidence": 0.78}},
        {{"month": "Month 3", "predicted_price": 26.0, "trend": "stable", "confidence": 0.75}}
    ],
    "best_time_to_sell": "Month X",
    "ai_analysis": "Provide a comprehensive analysis of national market conditions, state-wise variations, and price drivers."
}}

Strictly adhere to the historical data trends provided if available.
Respond ONLY with valid JSON."""

        user_prompt = f"""Predict prices for:
- Crop: {crop_name}
- Region: {region}
- Current Price: ₹{current_price}/kg
- Prediction Period: {prediction_months} months
"""

        result = await groq_client.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=1500
        )

        if not result.get("success"):
            return self._predict_with_rules(crop_name, region, current_price, prediction_months)

        try:
            content = result["content"].replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            
            # Key Mapping for stability (Mapping potential camelCase or variations back to snake_case)
            mapping = {
                "aiAnalysis": "ai_analysis",
                "aiAnalysisText": "ai_analysis",
                "bestTimeToSell": "best_time_to_sell",
                "currentPrice": "current_price"
            }
            for old_key, new_key in mapping.items():
                if old_key in data and new_key not in data:
                    data[new_key] = data[old_key]

            data["source"] = "groq-ai (augmented with CSV data)" if historical_data else "groq-ai"
            return data
        except json.JSONDecodeError:
            return self._predict_with_rules(crop_name, region, current_price, prediction_months)

    async def get_current_prices_from_ai(self, region: str, crop: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fallback: Use AI to generate realistic price estimates for a region 
        when CSV data is missing.
        """
        if not groq_client.is_available():
            return self.get_current_prices(region) # Extreme fallback to hardcoded samples

        crop_filter = f"specifically for {crop}" if crop else "for major crops (Rice, Wheat, Tomato, Onion, Potato, Mustard, Maize, Cotton)"
        
        system_prompt = """You are a real-time Mandi price estimator. 
Generate current market price estimates for Indian crops based on recent seasonal patterns and known market statuses.
Return data in a structured JSON list.

OUTPUT FORMAT (JSON):
[
    {
        "state": "Gujarat",
        "district": "Amreli",
        "market": "Damnagar",
        "commodity": "Wheat",
        "variety": "Common",
        "grade": "FAQ",
        "arrival_date": "2024-05-20",
        "min_price": 2200,
        "max_price": 2400,
        "modal_price": 2300,
        "source": "Groq AI Estimate"
    }
]
Respond ONLY with valid JSON."""

        user_prompt = f"Estimate current Mandi prices in {region} {crop_filter}. Ensure prices are in INR per Quintal (100kg)."

        result = await groq_client.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.4,
            max_tokens=2000
        )

        if not result.get("success"):
            return []

        try:
            content = result["content"].replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except:
            return []

    def _predict_with_rules(
        self,
        crop_name: str,
        region: str,
        current_price: float,
        prediction_months: int
    ) -> Dict[str, Any]:
        """Rule-based price prediction (fallback)"""

        predictions = []
        base_price = current_price

        # Seasonal factors (simplified)
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        current_month = datetime.now().month

        for i in range(prediction_months):
            month_idx = (current_month + i) % 12
            month_name = month_names[month_idx]
            year = datetime.now().year + (current_month + i) // 12

            seasonal_factor = 1.0 + 0.1 * (i % 3)
            predicted = base_price * seasonal_factor
            confidence = max(0.6, 0.9 - (i * 0.08))

            if i == 0:
                trend = "stable"
            elif predicted > base_price * 1.02:
                trend = "rising"
            elif predicted < base_price * 0.98:
                trend = "falling"
            else:
                trend = "stable"

            predictions.append({
                "month": f"{month_name} {year}",
                "predicted_price": round(predicted, 2),
                "trend": trend,
                "confidence": round(confidence, 2)
            })

        best_month = max(predictions, key=lambda x: x["predicted_price"])

        analysis = (
            f"Based on seasonal patterns for {crop_name} in {region}, prices are expected to "
            f"trend {predictions[0]['trend']} over the next {prediction_months} months. "
        )

        return {
            "commodity": crop_name,
            "region": region,
            "current_price": current_price,
            "predictions": predictions,
            "best_time_to_sell": best_month["month"],
            "ai_analysis": analysis,
            "source": "rule-based (AI fallback)"
        }

    def get_current_prices(self, region: str = "India") -> List[Dict[str, Any]]:
        """Static sample data (Extreme fallback)"""
        prices = []
        for crop, data in self.market_data.items():
            variation = 0.9 + 0.2 * (hash(region + crop) % 100) / 100
            price = data["base_price"] * variation

            prices.append({
                "state": region,
                "district": "General",
                "market": "Main Market",
                "commodity": crop.capitalize(),
                "variety": "Common",
                "grade": "FAQ",
                "arrival_date": datetime.now().strftime("%Y-%m-%d"),
                "min_price": round(price * 0.9 * 100, 0),
                "max_price": round(price * 1.1 * 100, 0),
                "modal_price": round(price * 100, 0),
                "source": "Sample Data"
            })

        return sorted(prices, key=lambda x: x["commodity"])


# Singleton instance
market_agent = MarketAnalysisAgent()
