from typing import Any, Dict, Optional


class OpenAIClient:
    def complete(self, prompt: str) -> str:
        return f"OpenAI response for: {prompt}"
