import json
import os
import re
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class GeminiClient:
    DEFAULT_MODEL = "gemini-3.5-flash"
    USER_AGENT = "FarmFusion/1.0 (https://farmfusion1.onrender.com)"

    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
        if not self.api_key:
            raise RuntimeError("Gemini API key is not configured")
        self.model = (
            model
            or os.getenv("GEMINI_MODEL")
            or getattr(settings, "GEMINI_MODEL", None)
            or self.DEFAULT_MODEL
        )

    def _request(self, prompt: str, image_base64: Optional[str] = None, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        
        # Build content parts
        parts = []
        if image_base64:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_base64
                }
            })
        parts.append({"text": prompt})

        payload = {"contents": [{"parts": parts}]}
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        req = Request(url, data=data, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except HTTPError as err:
            body = err.read().decode(errors="ignore")
            raise RuntimeError(f"Gemini API request failed ({err.code}): {err.reason}. Response: {body}")
        except URLError as err:
            raise RuntimeError(f"Gemini API request failed: {err.reason}")

    @staticmethod
    def _extract_text(response: Dict[str, Any]) -> str:
        candidates = response.get("candidates") or []
        if not candidates:
            return ""
        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        texts = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")]
        return "\n".join(texts).strip()

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            return json.loads(fenced.group(1))
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            return json.loads(brace.group())
        raise RuntimeError(f"Gemini response was not valid JSON: {text}")

    def complete(self, prompt: str) -> str:
        response = self._request(prompt)
        text = self._extract_text(response)
        if not text:
            raise RuntimeError(f"Gemini response missing text output: {response}")
        return text

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        text = self.complete(json_prompt)
        try:
            return self._parse_json(text)
        except json.JSONDecodeError as err:
            raise RuntimeError(f"Gemini response was not valid JSON: {text}") from err

    def complete_json_with_image(self, prompt: str, image_base64: str, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """Analyze an image and return JSON response."""
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        response = self._request(json_prompt, image_base64, mime_type=mime_type)
        text = self._extract_text(response)
        if not text:
            raise RuntimeError(f"Gemini response missing text output: {response}")
        try:
            return self._parse_json(text)
        except json.JSONDecodeError as err:
            raise RuntimeError(f"Gemini response was not valid JSON: {text}") from err

    def generate(self, prompt: str) -> str:
        return self.complete(prompt)


gemini_client = GeminiClient()