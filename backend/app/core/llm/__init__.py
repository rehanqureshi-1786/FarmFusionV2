"""
Centralized LLM provider factory and interface exports for FarmFusion.
Supports OpenRouter as primary reasoning layer with Groq and deterministic fallback.
"""
from typing import Optional
import structlog

from app.core.config import get_settings
from app.core.llm.base import LLMMessage, LLMProvider, LLMResponse
from app.core.llm.groq_provider import GroqLLMProvider
from app.core.llm.openrouter_provider import OpenRouterLLMProvider

logger = structlog.get_logger(__name__)

_active_provider: Optional[LLMProvider] = None


def get_llm_provider(force_refresh: bool = False) -> LLMProvider:
    """
    Factory function returning the active canonical LLM provider.
    Priority order:
    1. OpenRouterLLMProvider (if OPENROUTER_API_KEY is configured)
    2. GroqLLMProvider (if GROQ_API_KEY is configured)
    3. Unavailable fallback provider (returns is_available() == False)
    """
    global _active_provider
    if _active_provider is None or force_refresh:
        settings = get_settings()
        if settings.openrouter_api_key and not settings.openrouter_api_key.startswith("placeholder"):
            _active_provider = OpenRouterLLMProvider(
                api_key=settings.openrouter_api_key,
                model=settings.openrouter_model,
                base_url=settings.openrouter_base_url,
            )
            logger.info("llm_provider_initialized", provider="openrouter", model=settings.openrouter_model)
        elif settings.groq_api_key and not settings.groq_api_key.startswith("gsk_placeholder"):
            _active_provider = GroqLLMProvider()
            logger.info("llm_provider_initialized", provider="groq", model=settings.groq_model)
        else:
            logger.warning("no_primary_llm_configured", reason="Neither OPENROUTER_API_KEY nor GROQ_API_KEY is available")
            _active_provider = OpenRouterLLMProvider(api_key=None)  # is_available() == False

    return _active_provider


def get_openrouter_provider() -> OpenRouterLLMProvider:
    """Returns an OpenRouterLLMProvider instance using current settings."""
    settings = get_settings()
    return OpenRouterLLMProvider(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
    )


def get_groq_provider() -> GroqLLMProvider:
    """Returns a GroqLLMProvider instance using current settings."""
    return GroqLLMProvider()


__all__ = [
    "LLMMessage",
    "LLMResponse",
    "LLMProvider",
    "GroqLLMProvider",
    "OpenRouterLLMProvider",
    "get_llm_provider",
    "get_openrouter_provider",
    "get_groq_provider",
]
