"""
Unit tests for Centralized LLM Provider Layer (Phase B).
"""
import pytest
from pydantic import BaseModel, Field
from app.core.llm import get_llm_provider, LLMMessage, LLMResponse, GroqLLMProvider


class SampleAgriculturalIntent(BaseModel):
    intent: str = Field(..., description="The detected agricultural intent (e.g. weather, mandi, crop)")
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_tools: bool = Field(...)


def test_llm_provider_initialization():
    provider = get_llm_provider()
    assert provider is not None
    assert isinstance(provider, GroqLLMProvider)


@pytest.mark.asyncio
async def test_llm_generate_basic():
    provider = get_llm_provider()
    if not provider.is_available():
        pytest.skip("GROQ_API_KEY not configured in test environment")

    messages = [
        LLMMessage(role="user", content="Reply with the single word 'NAMASTE' and nothing else.")
    ]
    response = await provider.generate(messages=messages, temperature=0.0, max_tokens=10)
    assert response is not None
    assert isinstance(response, LLMResponse)
    assert "NAMASTE" in response.content.upper()
    assert response.provider == "groq"
    assert response.tokens_used > 0


@pytest.mark.asyncio
async def test_llm_generate_structured():
    provider = get_llm_provider()
    if not provider.is_available():
        pytest.skip("GROQ_API_KEY not configured in test environment")

    messages = [
        LLMMessage(
            role="user",
            content="Classify this farmer statement: 'कल बारिश होगी क्या मेरे खेत में?' (Will it rain tomorrow on my farm?)"
        )
    ]
    structured: SampleAgriculturalIntent = await provider.generate_structured(
        schema=SampleAgriculturalIntent,
        messages=messages,
        system_prompt="You are an agricultural NLU router.",
        temperature=0.0
    )
    assert structured is not None
    assert isinstance(structured, SampleAgriculturalIntent)
    assert "weather" in structured.intent.lower() or "barish" in structured.intent.lower() or "rain" in structured.intent.lower()
    assert structured.confidence >= 0.5
    assert structured.requires_tools is True
