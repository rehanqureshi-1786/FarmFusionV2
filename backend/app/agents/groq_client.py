from typing import Any, Optional

from app.agents.openai_client import OpenAIClient


class GroqClient:
    def __init__(self, model: Optional[str] = None):
        self.client = OpenAIClient(model=model)

    def complete(self, prompt: str) -> str:
        return self.client.complete(prompt)
