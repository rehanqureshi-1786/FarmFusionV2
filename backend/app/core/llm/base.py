"""
Base interfaces and data contracts for LLM providers in FarmFusion.
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LLMMessage(BaseModel):
    role: str = Field(..., description="Role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message text content")


class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: int = 0
    provider: str
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """Abstract interface for all LLM providers in FarmFusion."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available for inference."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None,
    ) -> LLMResponse:
        """Generate a chat completion."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        schema: Type[T],
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_retries: int = 2,
    ) -> T:
        """Generate and parse structured Pydantic output with schema validation."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Stream response tokens sequentially."""
        pass
