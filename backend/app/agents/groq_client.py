import json
import os
import re
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class GroqClient:
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
    USER_AGENT = "FarmFusion/1.0 (https://farmfusion1.onrender.com)"

    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)
        if not self.api_key:
            raise RuntimeError("Groq API key is not configured")
        self.model = (
            model
            or os.getenv("GROQ_MODEL")
            or getattr(settings, "GROQ_MODEL", None)
            or self.DEFAULT_MODEL
        )
        self.endpoint = self.ENDPOINT

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
            raise RuntimeError(f"Groq API request failed ({err.code}): {err.reason}. Response: {body}")
        except URLError as err:
            raise RuntimeError(f"Groq API request failed: {err.reason}")

    @staticmethod
    def _extract_text(response: Dict[str, Any]) -> str:
        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") or {}
            return str(message.get("content", "")).strip()
        return ""

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
        raise RuntimeError(f"Groq response was not valid JSON: {text}")

    def complete(self, prompt: str) -> str:
        response = self._request(prompt)
        text = self._extract_text(response)
        if not text:
            raise RuntimeError(f"Groq response missing text output: {response}")
        return text

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        text = self.complete(prompt)
        try:
            return self._parse_json(text)
        except json.JSONDecodeError as err:
            raise RuntimeError(f"Groq response was not valid JSON: {text}") from err
