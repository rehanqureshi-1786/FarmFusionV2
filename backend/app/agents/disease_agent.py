import logging
import os
from typing import Any, Dict, List, Type

from app.agents.gemini_client import GeminiClient
from app.agents.groq_client import GroqClient
from app.agents.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class DiseaseDetectionAgent:
    _FILENAME_HINTS = (
        ("blight", "Late blight", 0.65),
        ("rust", "Leaf rust", 0.6),
        ("mildew", "Powdery mildew", 0.6),
        ("rot", "Root rot", 0.55),
        ("spot", "Leaf spot", 0.55),
        ("wilt", "Bacterial wilt", 0.55),
        ("mosaic", "Mosaic virus", 0.6),
    )

    def _build_prompt(self, image_ref: str) -> str:
        return (
            "You are a plant pathology expert. Based on the supplied image filename or URL, "
            "infer the most likely plant disease and a confidence score between 0 and 1. "
            "If there is not enough information, return disease as 'unknown' and confidence 0.0. "
            "Return only valid JSON with keys disease and confidence. "
            f"Image reference: {image_ref}"
        )

    @staticmethod
    def _providers() -> List[Type]:
        providers: List[Type] = [GroqClient, GeminiClient]
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        if openai_key and not openai_key.startswith("your_"):
            providers.append(OpenAIClient)
        return providers

    @staticmethod
    def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
        disease = str(data.get("disease") or data.get("disease_name") or "unknown").strip() or "unknown"
        try:
            confidence = float(data.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        return {"disease": disease, "confidence": confidence}

    def _fallback_from_filename(self, image_ref: str) -> Dict[str, Any]:
        name = (image_ref or "").lower()
        for hint, disease, confidence in self._FILENAME_HINTS:
            if hint in name:
                return {"disease": disease, "confidence": confidence}
        return {"disease": "unknown", "confidence": 0.0}

    def detect(self, image_ref: str) -> Dict[str, Any]:
        prompt = self._build_prompt(image_ref)
        last_error: Exception | None = None

        for client_cls in self._providers():
            provider = client_cls.__name__
            try:
                data = client_cls().complete_json(prompt)
                if isinstance(data, dict):
                    result = self._normalize(data)
                    logger.info("Disease detection succeeded via %s", provider)
                    return result
            except Exception as exc:
                last_error = exc
                logger.warning("Disease detection provider %s failed: %s", provider, exc)

        if last_error:
            logger.warning("All AI providers failed; using filename fallback. Last error: %s", last_error)
        return self._fallback_from_filename(image_ref)
