from typing import Any, Dict, Optional

from app.agents.groq_client import GroqClient


class GeminiClient:
    def __init__(self, model: Optional[str] = None):
        self.client = GroqClient(model=model)

    def generate(self, prompt: str) -> str:
        return self.client.complete(prompt)
