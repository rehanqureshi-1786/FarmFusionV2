import base64
import os
from typing import Dict, Any, Optional
from app.agents.gemini_client import GeminiClient
from app.agents.grok_client import grok_client
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
        """Detect plant disease using Vision AI (Gemini primary, Grok fallback)."""
        if not settings.gemini_api_key:
            raise RuntimeError("No AI API keys configured. Cannot perform disease detection.")

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

        # Try Gemini first
        data = None
        gemini_error = None
        try:
            client = GeminiClient()
            data = client.complete_json_with_image(prompt, image_base64, mime_type=mime_type)
            print(f"[DISEASE DETECTION] Using Gemini - disease={data.get('disease')}")
        except Exception as e:
            gemini_error = str(e)
            is_quota_error = "quota" in gemini_error.lower() or "rate limit" in gemini_error.lower()
            print(f"[DISEASE DETECTION] Gemini failed: {gemini_error}")
            
            # Try Grok as fallback if Gemini failed with quota error or if fallback is enabled
            if (is_quota_error or os.getenv("FALLBACK_DISEASE_DETECTION") == "1") and grok_client:
                try:
                    print(f"[DISEASE DETECTION] Trying Grok as fallback...")
                    data = grok_client.complete_json_with_image(prompt, image_base64, mime_type=mime_type)
                    print(f"[DISEASE DETECTION] Using Grok - disease={data.get('disease')}")
                except Exception as e:
                    grok_error = str(e)
                    print(f"[DISEASE DETECTION] Grok fallback failed: {grok_error}")
                    # Both failed, will return generic response below

        # If both AI services failed or returned no data, check if we should return generic response
        if data is None:
            fallback_enabled = settings.debug or os.getenv("FALLBACK_DISEASE_DETECTION") == "1"
            if fallback_enabled:
                return {
                    "disease": "Unknown",
                    "confidence": 0.0,
                    "severity": "unknown",
                    "description": "AI service unavailable; unable to analyze image at this time.",
                    "treatment": [],
                    "prevention": []
                }
            raise RuntimeError(f"Disease detection failed: Gemini={gemini_error}")

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
