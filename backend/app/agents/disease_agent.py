import base64
import os
from typing import Dict, Any
from app.agents.gemini_client import GeminiClient
from app.core.config import settings


def _detect_image_mime_type(image_bytes: bytes) -> str:
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if image_bytes.startswith(b"BM"):
        return "image/bmp"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


class DiseaseDetectionAgent:
    def detect(self, image_bytes: bytes) -> Dict[str, Any]:
        """Detect plant disease from actual image content using Gemini Vision API."""
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Gemini API key not configured. Cannot perform disease detection.")

        mime_type = _detect_image_mime_type(image_bytes)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "You are an expert plant pathologist and agricultural scientist. "
            "Analyze this image and identify if there is any plant disease visible. "
            "Provide:\n"
            "1. The disease name (or 'healthy' if no disease detected, or 'unknown' if you cannot determine)\n"
            "2. Confidence score between 0.0 and 1.0\n"
            "3. Brief description of symptoms if disease is detected\n"
            "Return ONLY valid JSON with keys: disease, confidence, description"
        )

        client = GeminiClient()
        try:
            data = client.complete_json_with_image(prompt, image_base64, mime_type=mime_type)
        except Exception as e:
            error_text = str(e)
            is_quota_error = "quota" in error_text.lower() or "rate limit" in error_text.lower()
            fallback_enabled = settings.debug or os.getenv("FALLBACK_DISEASE_DETECTION") == "1"

            if is_quota_error or fallback_enabled:
                return {
                    "disease": "unknown",
                    "confidence": 0.0,
                    "description": "AI service unavailable; unable to analyze image at this time."
                }
            raise RuntimeError(f"Gemini Vision API error: {error_text}")

        if not isinstance(data, dict):
            raise RuntimeError(f"AI returned unexpected JSON shape: {data}")

        return {
            "disease": data.get("disease", "unknown"),
            "confidence": float(data.get("confidence", 0.0)),
            "description": data.get("description", "")
        }
