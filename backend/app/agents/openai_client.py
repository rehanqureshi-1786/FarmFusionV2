import json
import os
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class OpenAIClient:
    USER_AGENT = "FarmFusion/1.0 (https://farmfusion1.onrender.com)"

    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
        if not self.api_key:
            raise RuntimeError("OpenAI API key is not configured")
        self.model = model or os.getenv("OPENAI_MODEL") or getattr(settings, "OPENAI_MODEL", "gpt-4.1-mini")
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def _request(self, prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert agriculture assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.6,
            "max_tokens": 600,
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": self.USER_AGENT,
        }
        req = Request(self.endpoint, data=data, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except HTTPError as err:
            body = err.read().decode(errors="ignore")
            raise RuntimeError(f"OpenAI API request failed ({err.code}): {err.reason}. Response: {body}")
        except URLError as err:
            raise RuntimeError(f"OpenAI API request failed: {err.reason}")

    def complete(self, prompt: str) -> str:
        response = self._request(prompt)
        choices = response.get("choices") or []
        if not choices or not isinstance(choices, list):
            raise RuntimeError("OpenAI response missing choices")

        message = choices[0].get("message") or {}
        return str(message.get("content", "")).strip()

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        text = self.complete(prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            raise RuntimeError(f"OpenAI response was not valid JSON: {text}")
