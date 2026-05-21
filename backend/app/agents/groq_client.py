import json
import os
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class GroqClient:
    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GROQ_API_KEY") or getattr(settings, "GROQ_API_KEY", None)
        if not self.api_key:
            raise RuntimeError("Groq API key is not configured")
        self.model = model or os.getenv("GROQ_MODEL") or getattr(settings, "GROQ_MODEL", "grok-1")
        self.endpoint = "https://api.groq.com/openai/v1/responses"

    def _request(self, prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "input": prompt,
            "temperature": 0.6,
            "max_output_tokens": 600,
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
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
        if isinstance(response, dict) and "output_text" in response:
            return str(response.get("output_text", "")).strip()

        output = response.get("output")
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, dict):
                if "output_text" in first:
                    return str(first.get("output_text", "")).strip()
                content = first.get("content")
                if isinstance(content, list):
                    text_parts = [
                        item.get("text")
                        for item in content
                        if isinstance(item, dict) and item.get("type") == "output_text" and item.get("text")
                    ]
                    if text_parts:
                        return "\n".join(text_parts).strip()
                if isinstance(content, str):
                    return content.strip()

        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") or {}
            return str(message.get("content", "")).strip()

        return ""

    def complete(self, prompt: str) -> str:
        response = self._request(prompt)
        text = self._extract_text(response)
        if not text:
            raise RuntimeError(f"Groq response missing text output: {response}")
        return text

    def complete_json(self, prompt: str) -> Dict[str, Any]:
        text = self.complete(prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            raise RuntimeError(f"Groq response was not valid JSON: {text}") from err
