import json
import re
from typing import Dict, Any

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
        client = OpenAIClient()
        try:
            data = client.complete_json(prompt)
        except RuntimeError:
            response = client.complete(prompt)
            match = re.search(r"\{.*\}", response, re.S)
            if match:
                try:
                    data = json.loads(match.group(0))
                except Exception:
                    data = {"disease": "unknown", "confidence": 0.0}
            else:
                data = {"disease": "unknown", "confidence": 0.0}
        return {
            "disease": data.get("disease", "unknown"),
            "confidence": float(data.get("confidence", 0.0)),
        }
