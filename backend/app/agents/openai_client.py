"""
OpenAI client for FarmFusion voice workflows.
Uses the Responses API over plain HTTP so no extra SDK is required.
"""
from typing import Any, Dict, Optional

import httpx

from app.core.config import get_settings


class OpenAIClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.openai_api_key
        self.model = self.settings.openai_model
        self.base_url = "https://api.openai.com/v1"

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 20)

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_output_tokens: int = 600
    ) -> Dict[str, Any]:
        if not self.is_available():
            return {"success": False, "error": "OpenAI API key not configured"}

        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}]
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_prompt}]
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=25.0, trust_env=False) as client:
                response = await client.post(
                    f"{self.base_url}/responses",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "success": True,
                    "content": self._extract_output_text(data),
                    "raw": data
                }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    @staticmethod
    def _extract_output_text(data: Dict[str, Any]) -> str:
        output = data.get("output", [])
        for item in output:
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return content.get("text", "").strip()

        return data.get("output_text", "").strip()


openai_client = OpenAIClient()
