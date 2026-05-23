import base64
import os
from typing import Dict, Any, Optional
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
    def detect(
        self,
        image_bytes: bytes,
        crop_type: Optional[str] = None,
        response_language: str = "en",
    ) -> Dict[str, Any]:
        """Detect plant disease from actual image content using Gemini Vision API."""
        if not settings.gemini_api_key:
            raise RuntimeError("Gemini API key not configured. Cannot perform disease detection.")

        mime_type = _detect_image_mime_type(image_bytes)
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "You are an expert plant pathologist with 20+ years of experience. "
            "Analyze this image and identify the plant disease present. "
            "Even if you're not 100% certain, provide your BEST diagnosis based on visible symptoms.\n\n"
        )

        if crop_type:
            prompt += f"Crop type hint: {crop_type}\n"

        prompt += (
            "Instructions:\n"
            "1. ALWAYS provide a disease name - never say 'unknown' or 'unable to determine'\n"
            "2. If plant is healthy, respond with 'Healthy Plant'\n"
            "3. If you see disease symptoms, provide the most likely disease name\n"
            "4. Confidence score: 0.0-1.0 (your certainty level)\n"
            "5. Describe visible symptoms clearly\n"
            "6. Provide actionable treatment recommendations after you describe the problem\n\n"
            "Return ONLY valid JSON with keys in this order: disease, confidence, severity, description, treatment, prevention"
        )

        if response_language and response_language.lower() != "en":
            prompt += f"\nRespond in {response_language}."

        client = GeminiClient()
        try:
            data = client.complete_json_with_image(prompt, image_base64, mime_type=mime_type)
        except Exception as e:
            error_text = str(e)
            is_quota_error = "quota" in error_text.lower() or "rate limit" in error_text.lower()
            fallback_enabled = settings.debug or os.getenv("FALLBACK_DISEASE_DETECTION") == "1"

            print(f"[DISEASE DETECTION ERROR] {error_text}")
            if is_quota_error or fallback_enabled:
                return {
                    "disease": "Unknown",
                    "confidence": 0.0,
                    "severity": "unknown",
                    "description": "AI service unavailable; unable to analyze image at this time.",
                    "treatment": [],
                    "prevention": []
                }
            raise RuntimeError(f"Gemini Vision API error: {error_text}")

        if not isinstance(data, dict):
            raise RuntimeError(f"AI returned unexpected JSON shape: {data}")

        disease = str(data.get("disease", "")).strip()
        description = str(data.get("description", "")).strip()
        severity = str(data.get("severity", "unknown")).strip().lower() or "unknown"

        if disease.lower() in ("unknown", "unable to determine", "not sure", "unsure", "", "n/a"):
            if description:
                disease = "Possible disease symptoms"
            else:
                disease = "Unknown"

        treatment = data.get("treatment", [])
        prevention = data.get("prevention", [])

        if isinstance(treatment, str):
            treatment = [treatment.strip()] if treatment.strip() else []
        if isinstance(prevention, str):
            prevention = [prevention.strip()] if prevention.strip() else []

        return {
            "disease": disease,
            "confidence": float(data.get("confidence", 0.0)),
            "severity": severity,
            "description": description,
            "treatment": treatment,
            "prevention": prevention,
        }
