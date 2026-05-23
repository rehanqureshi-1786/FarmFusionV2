"""
Groq API Client for FarmFusion
Groq provides ultra-fast inference with open-source models
Free tier: 1M tokens/day, 20 requests/minute
"""
import base64
from typing import Optional, Dict, Any
from groq import AsyncGroq
from app.core.config import get_settings


class GroqClient:
    """
    Client for Groq API - provides access to Llama 3.3, Mixtral, Gemma models
    Uses Async Client to prevent event loop blocking.
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if self.settings.groq_api_key:
            self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    def is_available(self) -> bool:
        """Check if Groq API is configured and available"""
        return self.client is not None

    async def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Get chat completion from Groq (Async)
        """
        if not self.is_available():
            raise ValueError("Groq API key not configured. Get one at console.groq.com")

        model = model or self.settings.groq_model

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # Use await for non-blocking network call
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def vision_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        image_bytes: bytes,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1200
    ) -> Dict[str, Any]:
        """Analyze an image with a Groq vision-capable model (Async)."""
        if not self.is_available():
            raise ValueError("Groq API key not configured. Get one at console.groq.com")

        model = model or self.settings.groq_vision_model

        mime_type = "image/jpeg"
        if image_bytes.startswith(b"\x89PNG"):
            mime_type = "image/png"

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:{mime_type};base64,{image_base64}"

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ]

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


# Singleton instance
groq_client = GroqClient()
