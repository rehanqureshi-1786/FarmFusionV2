"""
Comprehensive Test Suite for OpenRouter Free LLM Reasoning Layer Integration (Phase F7).
Covers:
Tests 1-8: Provider Configuration, Structured Output, Fallbacks, Error Handling.
Tests 9-20: Unseen Orchestration Queries across all Domains, Multi-Intent, Context, Temporal Invariants, and Languages.
"""
import os
import json
import pytest
import httpx
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.llm import (
    get_llm_provider,
    get_openrouter_provider,
    get_groq_provider,
    LLMMessage,
    LLMResponse,
    OpenRouterLLMProvider,
    GroqLLMProvider,
)
from app.orchestrator.semantic_extractor import (
    extract_semantic_frame,
    extract_semantic_frame_llm,
    extract_semantic_frame_deterministic,
)
from app.schemas.semantic_frame import (
    CanonicalIntent,
    CapabilityType,
    RequiredInput,
    RelativeDay,
    UserContext,
    ConversationContext,
    FarmLocation,
    SemanticFrame,
)
from app.orchestrator.nodes.synthesizer import call_llm_synthesizer


# =============================================================================
# PART 1: PROVIDER TESTS (1 - 8)
# =============================================================================

class MockStructuredResult(BaseModel):
    intent: str = Field(..., description="Detected intent")
    crop: str = Field(..., description="Target crop")
    confidence: float = Field(..., ge=0.0, le=1.0)


def test_01_openrouter_configuration_loading():
    """1. OpenRouter configuration loading from settings/environment."""
    settings = get_settings()
    assert hasattr(settings, "openrouter_api_key")
    assert hasattr(settings, "openrouter_model")
    assert hasattr(settings, "openrouter_base_url")
    assert settings.openrouter_base_url.startswith("http")
    assert settings.openrouter_model is not None

    provider = get_openrouter_provider()
    assert provider.default_model == settings.openrouter_model
    assert provider.base_url.rstrip("/") == settings.openrouter_base_url.rstrip("/")


@pytest.mark.asyncio
async def test_02_successful_structured_response():
    """2. Successful structured response generation with Pydantic validation."""
    provider = get_openrouter_provider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": json.dumps({"intent": "irrigation_check", "crop": "Wheat", "confidence": 0.95})}}],
        "usage": {"total_tokens": 25},
    }
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        messages = [
            LLMMessage(role="user", content="Classify the agricultural crop and intent: 'कल गेहूं (wheat) में पानी देना है क्या?'")
        ]
        res = await provider.generate_structured(
            schema=MockStructuredResult,
            messages=messages,
            system_prompt="Return valid JSON with keys: intent (string), crop (e.g. Wheat), confidence (float 0.0 to 1.0).",
        )
        assert res is not None
        assert isinstance(res, MockStructuredResult)
        assert res.confidence >= 0.0
        assert "wheat" in res.crop.lower()


@pytest.mark.asyncio
async def test_03_malformed_response_fallback():
    """3. Malformed JSON response triggers clean retries and fallback."""
    provider = OpenRouterLLMProvider(api_key="mock_test_key")
    
    # Mock httpx returning invalid non-JSON string
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "This is definitely not JSON at all."}}],
        "usage": {"total_tokens": 10},
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(ValueError) as excinfo:
            await provider.generate_structured(
                schema=MockStructuredResult,
                messages=[LLMMessage(role="user", content="Test")],
                max_retries=1,
            )
        assert "Failed to produce valid structured output" in str(excinfo.value)


@pytest.mark.asyncio
async def test_04_timeout_fallback():
    """4. Timeout in OpenRouter raises TimeoutError and triggers fallback in extractor."""
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Connection timed out")):
        # Direct provider raises TimeoutError
        provider = OpenRouterLLMProvider(api_key="mock_test_key")
        with pytest.raises(TimeoutError):
            await provider.generate(messages=[LLMMessage(role="user", content="Test")])

        # Semantic extractor falls back smoothly to deterministic without crashing
        frame = await extract_semantic_frame("kal barish hogi kya?", detected_language="hi")
        assert frame is not None
        assert frame.intent == CanonicalIntent.WEATHER
        assert frame.entities.time_context.relative_day == RelativeDay.TOMORROW


@pytest.mark.asyncio
async def test_05_http_429_fallback():
    """5. HTTP 429 Rate Limit error triggers fallback without crashing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        # In synthesizer, 429 falls back cleanly
        parsed, reason = await call_llm_synthesizer("Test prompt")
        # Should report error or fallback to groq/deterministic
        assert parsed is None or "openrouter_http_error_429" in reason or "groq" in reason


@pytest.mark.asyncio
async def test_06_authentication_failure():
    """6. Authentication failure (HTTP 401/403) is caught and handled safely."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized: Invalid API Key"

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        provider = OpenRouterLLMProvider(api_key="invalid_mock_key")
        with pytest.raises(RuntimeError) as excinfo:
            await provider.generate(messages=[LLMMessage(role="user", content="Hello")])
        assert "authentication failed" in str(excinfo.value).lower()


def test_07_missing_api_key():
    """7. Missing API key correctly marks provider unavailable."""
    provider = OpenRouterLLMProvider(api_key="")
    assert provider.is_available() is False

    placeholder_provider = OpenRouterLLMProvider(api_key="placeholder_openrouter_key")
    assert placeholder_provider.is_available() is False


def test_08_provider_selection_order():
    """8. Factory selection order prioritizes OpenRouter over Groq when both configured."""
    with patch("app.core.config.get_settings") as mock_settings:
        mock_s = MagicMock()
        mock_s.openrouter_api_key = "sk-or-valid-test-key"
        mock_s.openrouter_model = "openrouter/free"
        mock_s.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_s.groq_api_key = "gsk-valid-test-key"
        mock_settings.return_value = mock_s

        provider = get_llm_provider(force_refresh=True)
        assert isinstance(provider, OpenRouterLLMProvider)


# =============================================================================
# PART 2: UNSEEN ORCHESTRATION & SEMANTIC TESTS (9 - 20)
# =============================================================================

@pytest.mark.asyncio
async def test_09_orchestration_unseen_weather_query():
    """9. Unseen Weather: 'subah se badal hain kal kheti ka kaam karna theek hoga?'"""
    query = "subah se badal hain kal kheti ka kaam karna theek hoga?"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent in (CanonicalIntent.WEATHER, CanonicalIntent.IRRIGATION_ADVISORY, CanonicalIntent.GENERAL_AGRICULTURE)
    assert any(c in frame.required_capabilities for c in [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION])
    assert frame.entities.time_context is not None
    assert frame.entities.time_context.relative_day == RelativeDay.TOMORROW


@pytest.mark.asyncio
async def test_10_orchestration_unseen_irrigation_query():
    """10. Unseen Irrigation: 'zameen kaafi geeli hai abhi paani rok dena chahiye?'"""
    query = "zameen kaafi geeli hai abhi paani rok dena chahiye?"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent in (CanonicalIntent.IRRIGATION_ADVISORY, CanonicalIntent.SMART_IRRIGATION)
    assert CapabilityType.SMART_IRRIGATION in frame.required_capabilities


@pytest.mark.asyncio
async def test_11_orchestration_unseen_mandi_query():
    """11. Unseen Mandi: 'gehu ka rate neeche ja raha hai kya abhi rokna sahi hai?'"""
    query = "gehu ka rate neeche ja raha hai kya abhi rokna sahi hai?"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.entities.crop == "Wheat"
    assert frame.intent in (CanonicalIntent.MANDI_PRICE, CanonicalIntent.SELL_HOLD, CanonicalIntent.MANDI_DECISION)
    assert any(c in frame.required_capabilities for c in [CapabilityType.CURRENT_PRICE, CapabilityType.MANDI_DECISION, CapabilityType.MANDI_FORECAST])


@pytest.mark.asyncio
async def test_12_orchestration_unseen_disease_query():
    """12. Unseen Disease: 'tamatar ke patte ajeeb tarah se murjha rahe hain'"""
    query = "tamatar ke patte ajeeb tarah se murjha rahe hain"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent == CanonicalIntent.DISEASE_DETECTION
    assert frame.entities.crop == "Tomato"
    # Disease symptom mentioned without leaf photo must trigger LEAF_IMAGE gate
    assert frame.required_input == RequiredInput.LEAF_IMAGE


@pytest.mark.asyncio
async def test_13_orchestration_unseen_disaster_query():
    """13. Unseen Disaster: 'baarish aur hawa dekh ke koi bada risk lag raha hai kya?'"""
    query = "baarish aur hawa dekh ke koi bada risk lag raha hai kya?"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent in (CanonicalIntent.DISASTER_RISK, CanonicalIntent.WEATHER)
    assert any(c in frame.required_capabilities for c in [CapabilityType.DISASTER_RISK, CapabilityType.WEATHER])


@pytest.mark.asyncio
async def test_14_orchestration_unseen_crop_query():
    """14. Unseen Crop: 'mere area ke hisaab se is season me kya uga sakta hu?'"""
    query = "mere area ke hisaab se is season me kya uga sakta hu?"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent == CanonicalIntent.CROP_RECOMMENDATION
    assert CapabilityType.CROP_RECOMMENDATION in frame.required_capabilities


@pytest.mark.asyncio
async def test_15_orchestration_unseen_calling_request():
    """15. Unseen Calling: 'farmer ko phone laga do'"""
    query = "farmer ko phone laga do"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent == CanonicalIntent.CALLING
    assert CapabilityType.CALLING in frame.required_capabilities


@pytest.mark.asyncio
async def test_16_orchestration_multi_intent_query():
    """16. Multi-intent: 'kal baarish hogi kya aur irrigation karni chahiye?'"""
    query = "kal baarish hogi kya aur irrigation karni chahiye?"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert CapabilityType.WEATHER in frame.required_capabilities
    assert CapabilityType.SMART_IRRIGATION in frame.required_capabilities
    assert frame.entities.time_context.relative_day == RelativeDay.TOMORROW


@pytest.mark.asyncio
async def test_17_orchestration_contextual_query():
    """17. Contextual turn: Turn 1: 'main wheat uga raha hoon', Turn 2: 'iske liye kal kya karna chahiye?'"""
    # Turn 1
    t1_frame = await extract_semantic_frame(raw_text="main wheat uga raha hoon", detected_language="hi")
    assert t1_frame.entities.crop == "Wheat"

    # Context carrier
    conv_context = ConversationContext(
        turn_index=1,
        active_crop="Wheat",
        last_intent="general_agriculture",
    )

    # Turn 2
    t2_frame = await extract_semantic_frame(
        raw_text="iske liye kal kya karna chahiye?",
        detected_language="hi",
        conversation_context=conv_context,
    )
    assert t2_frame.entities.crop == "Wheat"
    assert t2_frame.entities.time_context is not None
    assert t2_frame.entities.time_context.relative_day == RelativeDay.TOMORROW


@pytest.mark.asyncio
@pytest.mark.parametrize("temporal_query", [
    "kal mausam kaisa rahega",
    "kal barish hogi?",
    "agle din mausam?",
    "next day weather",
    "kal shaam baarish hogi?",
])
async def test_18_orchestration_tomorrow_temporal_invariants(temporal_query: str):
    """18. Tomorrow/temporal queries must never silently convert to TODAY/CURRENT."""
    frame = await extract_semantic_frame(raw_text=temporal_query, detected_language="hi")
    assert frame is not None
    assert frame.entities.time_context is not None
    assert frame.entities.time_context.relative_day == RelativeDay.TOMORROW
    assert frame.entities.time_context.day_offset == 1
    assert CapabilityType.WEATHER in frame.required_capabilities


@pytest.mark.asyncio
async def test_19_orchestration_hindi_query():
    """19. Pure Hindi Query: 'कोटा मंडी में लहसुन का ताजा भाव बताओ'"""
    query = "कोटा मंडी में लहसुन का ताजा भाव बताओ"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent == CanonicalIntent.MANDI_PRICE
    assert frame.entities.crop == "Garlic"
    assert frame.entities.market == "Kota" or frame.entities.city == "Kota"
    assert CapabilityType.CURRENT_PRICE in frame.required_capabilities


@pytest.mark.asyncio
async def test_20_orchestration_hinglish_query():
    """20. Hinglish Query: 'kal shaam ko baarish ka kya scene hai?'"""
    query = "kal shaam ko baarish ka kya scene hai?"
    frame = await extract_semantic_frame(raw_text=query, detected_language="hi")
    assert frame is not None
    assert frame.intent == CanonicalIntent.WEATHER
    assert CapabilityType.WEATHER in frame.required_capabilities
    assert frame.entities.time_context.relative_day == RelativeDay.TOMORROW
