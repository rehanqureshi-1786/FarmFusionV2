from typing import Any, Dict, Optional

from app.agents.openai_client import OpenAIClient


class GeminiClient:
    def __init__(self, model: Optional[str] = None):
        self.client = OpenAIClient(model=model)

    def generate(self, prompt: str) -> str:
        return self.client.complete(prompt)
