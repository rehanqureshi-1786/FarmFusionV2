import json
import re
from typing import Dict, Any

from app.agents.gemini_client import GeminiClient
from app.agents.groq_client import GroqClient
from app.agents.openai_client import OpenAIClient


class DiseaseDetectionAgent:
    def detect(self, image_url: str) -> Dict[str, Any]:
        prompt = (
            "You are a plant pathology expert. Based on the supplied image filename or URL, "
            "infer the most likely plant disease and a confidence score between 0 and 1. "
            "If there is not enough information, return disease as 'unknown' and confidence 0.0. "
            "Return only valid JSON with keys disease and confidence. "
            f"Image URL: {image_url}"
        )
        data = None
        last_error: RuntimeError | None = None
        for client_cls in (GroqClient, GeminiClient, OpenAIClient):
            try:
                data = client_cls().complete_json(prompt)
                break
            except RuntimeError as exc:
                last_error = exc
        if data is None:
            raise last_error or RuntimeError("No AI provider available for disease detection")

        if not isinstance(data, dict):
            raise RuntimeError(f"AI returned unexpected JSON shape: {data}")

        return {
            "disease": data.get("disease", "unknown"),
            "confidence": float(data.get("confidence", 0.0)),
        }
