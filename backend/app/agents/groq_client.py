from typing import Any


class GroqClient:
    def complete(self, prompt: str) -> str:
        return f"Groq completed: {prompt}"
