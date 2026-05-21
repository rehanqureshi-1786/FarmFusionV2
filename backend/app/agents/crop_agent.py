from typing import Any

from app.agents.groq_client import GroqClient


class CropRecommendationAgent:
    def recommend(self, crop_name: str, soil_type: Any) -> str:
        prompt = (
            f"You are an agricultural advisor. Provide a concise, practical recommendation for growing {crop_name} in {soil_type} soil. "
            "Include pest management, irrigation, and nutrient guidance in plain language. "
            "Respond with a short paragraph only."
        )
        client = GroqClient()
        return client.complete(prompt)
