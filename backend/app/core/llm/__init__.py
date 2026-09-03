"""
Centralized LLM provider factory and interface exports.
"""
from typing import Optional
import structlog

from app.core.config import get_settings
from app.core.llm.base import LLMMessage, LLMProvider, LLMResponse
from app.core.llm.groq_provider import GroqLLMProvider

logger = structlog.get_logger(__name__)

_active_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """
    Factory function returning the active canonical LLM provider.
    Currently defaults to GroqLLMProvider backed by GROQ_API_KEY.
    """
    global _active_provider
    if _active_provider is None:
        settings = get_settings()
        if settings.groq_api_key:
            _active_provider = GroqLLMProvider()
            logger.info("llm_provider_initialized", provider="groq", model=settings.groq_model)
        else:
            logger.warning("no_primary_llm_configured", reason="GROQ_API_KEY not found")
            _active_provider = GroqLLMProvider()  # Will return is_available() == False

    return _active_provider


__all__ = [
    "LLMMessage",
    "LLMResponse",
    "LLMProvider",
    "GroqLLMProvider",
    "get_llm_provider",
]
