import json
import os
import re
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class GrokClient:
    """Grok Vision API client for image analysis (via xAI API)."""
    DEFAULT_MODEL = "grok-vision-beta"
    USER_AGENT = "FarmFusion/1.0 (https://farmfusion1.onrender.com)"

    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GROQ_API_KEY") or getattr(settings, "groq_api_key", None)
        if not self.api_key:
            raise RuntimeError("Grok API key is not configured")
        self.model = (
            model
            or os.getenv("GROQ_VISION_MODEL")
            or getattr(settings, "groq_vision_model", None)
            or self.DEFAULT_MODEL
        )

    def _request(
        self,
        prompt: str,
        image_base64: Optional[str] = None,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Make a request to Grok Vision API."""
        url = "https://api.x.ai/v1/chat/completions"
        
        # Build content parts for vision
        messages = []
        if image_base64:
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            })
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 1024
        }
        
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": self.USER_AGENT,
        }
        
        req = Request(url, data=data, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except HTTPError as err:
            body = err.read().decode(errors="ignore")
            raise RuntimeError(
                f"Grok API request failed ({err.code}): {err.reason}. Response: {body}"
            )
        except URLError as err:
            raise RuntimeError(f"Grok API request failed: {err.reason}")

    @staticmethod
    def _extract_text(response: Dict[str, Any]) -> str:
        """Extract text from Grok API response."""
        choices = response.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        return content.strip() if isinstance(content, str) else ""

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        """Parse JSON from text response."""
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from code blocks
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            try:
                return json.loads(fenced.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to extract JSON object directly
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            try:
                return json.loads(brace.group())
            except json.JSONDecodeError:
                pass
        
        raise RuntimeError(f"Grok response was not valid JSON: {text}")

    def complete(self, prompt: str) -> str:
        """Generate text completion."""
        response = self._request(prompt)
        text = self._extract_text(response)
        if not text:
            raise RuntimeError(f"Grok response missing text output: {response}")
        return text

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        """Generate JSON response."""
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        text = self.complete(json_prompt)
        try:
            return self._parse_json(text)
        except Exception as err:
            raise RuntimeError(f"Grok response was not valid JSON: {text}") from err

    def complete_json_with_image(
        self,
        prompt: str,
        image_base64: str,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Analyze an image and return JSON response."""
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        response = self._request(json_prompt, image_base64, mime_type=mime_type)
        text = self._extract_text(response)
        if not text:
            raise RuntimeError(f"Grok response missing text output: {response}")
        try:
            return self._parse_json(text)
        except Exception as err:
            raise RuntimeError(f"Grok response was not valid JSON: {text}") from err

    def generate(self, prompt: str) -> str:
        """Generate content (alias for complete)."""
        return self.complete(prompt)


# Initialize global Grok client (may raise error if API key not configured)
try:
    grok_client = GrokClient()
except RuntimeError:
    grok_client = None
