import json
import re
from typing import Dict, Any

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
        # Try Groq first; if it fails, try OpenAI (so detection still works
        # when Groq credentials are invalid). Any RuntimeError from both
        # providers will propagate and result in a 502 from the API route.
        try:
            client = GroqClient()
            data = client.complete_json(prompt)
        except RuntimeError:
            # Attempt OpenAI as an alternative provider
            client = OpenAIClient()
            data = client.complete_json(prompt)

        if not isinstance(data, dict):
            raise RuntimeError(f"AI returned unexpected JSON shape: {data}")

        return {
            "disease": data.get("disease", "unknown"),
            "confidence": float(data.get("confidence", 0.0)),
        }
