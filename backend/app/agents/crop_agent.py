from typing import Any
from app.schemas.crop import CropRecommendRequest, CropRecommendation


class CropRecommendationAgent:
    def recommend(self, crop_name: str, soil_type: Any) -> str:
        return f"Use balanced NPK fertilizer for {crop_name} on {soil_type} soil."
