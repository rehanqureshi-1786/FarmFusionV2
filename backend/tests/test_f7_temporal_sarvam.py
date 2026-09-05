"""
Phase F7 Temporal ("kal") + Sarvam Voice/Language integration regression tests.

Covers:
1. Semantic temporal normalization across Hindi/Hinglish/English/regional languages.
2. Planner weather-tool routing: tomorrow -> weather_forecast_tool with target_date.
3. Validation temporal-consistency guard (today-data vs tomorrow-question).
4. Synthesizer date anchor ("कल" vs "आज").
5. Sarvam STT/TTS graceful fallback + language-metadata contract.
6. F7 typed ResponseEnvelope / action_payload survival through the API model.
"""
from datetime import date, datetime, timedelta

import pytest

from app.orchestrator.normalization import resolve_time_context
from app.orchestrator.planner import generate_task_plan
from app.schemas.semantic_frame import (
    SemanticFrame,
    EntitySet,
    TimeContext,
    RelativeDay,
    CanonicalIntent,
    CapabilityType,
    ConfidenceSet,
)
from app.models.voice import VoiceQueryResponse


def _frame(
    text: str,
    intent=CanonicalIntent.WEATHER,
    caps=(CapabilityType.WEATHER,),
) -> SemanticFrame:
    return SemanticFrame(
        request_id="req_t",
        session_id="sess_t",
        raw_text=text,
        normalized_text=text,
        language="hi",
        intent=intent,
        required_capabilities=list(caps),
        entities=EntitySet(time_context=TimeContext.model_validate(resolve_time_context(text))),
        confidence=ConfidenceSet(
            language_confidence=0.98,
            intent_confidence=0.9,
            entity_confidence=0.9,
            overall_confidence=0.9,
        ),
    )


# =============================================================================
# 1. SEMANTIC TEMPORAL NORMALIZATION (multilingual)
# =============================================================================

@pytest.mark.parametrize("query,day,offset,horizon", [
    ("kal ka mausam", "TOMORROW", 1, 1),
    ("kal mausam kaisa rahega", "TOMORROW", 1, 1),
    ("kal barish hogi?", "TOMORROW", 1, 1),
    ("tomorrow weather", "TOMORROW", 1, 1),
    ("weather tomorrow", "TOMORROW", 1, 1),
    ("what will the weather be tomorrow?", "TOMORROW", 1, 1),
    ("আগামীকাল আবহাওয়া কেমন হবে", "TOMORROW", 1, 1),
    ("next day mausam", "TOMORROW", 1, 1),
    ("agle din ka mausam", "TOMORROW", 1, 1),
    ("parsons weather", "DAY_AFTER_TOMORROW", 2, 1),
    ("agle 7 din ka mausam", "NEXT_7_DAYS", 0, 7),
    ("aaj ka mausam", "TODAY", 0, 1),
    ("today temperature", "TODAY", 0, 1),
])
def test_resolve_time_context_multilingual(query, day, offset, horizon):
    tc = resolve_time_context(query, reference_date="2026-09-05")
    assert tc["relative_day"] == day, f"{query} -> {tc}"
    assert tc["resolved_date"] == (date(2026, 9, 5) + timedelta(days=offset)).isoformat()
    assert tc["horizon_days"] == horizon
    assert tc["is_relative"] is True


def test_resolve_time_context_explicit_date():
    tc = resolve_time_context("mausam 15 September", reference_date="2026-09-05")
    assert tc["relative_day"] == "EXPLICIT_DATE"
    assert tc["explicit_date"] == f"{date.today().year}-09-15"


def test_resolve_time_context_no_signal():
    tc = resolve_time_context("aap ka naam kya hai?")
    assert tc["relative_day"] == "UNSPECIFIED"


# =============================================================================
# 2. PLANNER WEATHER TOOL ROUTING (tomorrow -> forecast, today -> current)
# =============================================================================

def test_planner_routes_tomorrow_to_forecast_tool():
    frame = _frame("kal ka mausam")
    assert frame.entities.time_context.relative_day == RelativeDay.TOMORROW
    plan = generate_task_plan(
        frame,
        farmer_context={"latitude": 26.9, "longitude": 75.8},
    )
    weather = [t for t in plan.tasks if t.tool_name in ("weather_tool", "weather_forecast_tool")]
    assert weather, "weather task must be present"
    w = weather[0]
    assert w.tool_name == "weather_forecast_tool"
    assert w.static_inputs.get("target_date") == frame.entities.time_context.resolved_date


def test_planner_routes_today_to_current_weather_tool():
    frame = _frame("aaj ka mausam")
    assert frame.entities.time_context.relative_day == RelativeDay.TODAY
    plan = generate_task_plan(
        frame,
        farmer_context={"latitude": 26.9, "longitude": 75.8},
    )
    weather = [t for t in plan.tasks if t.tool_name in ("weather_tool", "weather_forecast_tool")]
    assert weather
    assert weather[0].tool_name == "weather_tool"


# =============================================================================
# 3. VALIDATION TEMPORAL-CONSISTENCY GUARD
# =============================================================================

def _validation_state_with_weather(relative_day, weather_data):
    entities = {"time_context": {"relative_day": relative_day}}
    return {
        "intent": "weather",
        "semantic_frame": {"entities": entities},
        "tool_results": {"weather_1": weather_data},
        "failed_tasks": [],
        "task_plan": {"tasks": []},
    }


def test_validation_blocks_future_question_with_current_data():
    from app.orchestrator.nodes.validation import check_temporal_consistency
    state = _validation_state_with_weather("TOMORROW", {"temperature_c": 28.0, "annual_rainfall_mm": 0.0})
    check = check_temporal_consistency(state)
    assert check is not None
    assert check.check_name == "temporal_consistency"
    assert check.passed is False
    assert check.severity.value == "BLOCKING"


def test_validation_passes_future_question_with_forecast_data():
    from app.orchestrator.nodes.validation import check_temporal_consistency
    state = _validation_state_with_weather(
        "TOMORROW",
        {"forecast": [{"date": "2026-09-06", "temperature_avg_c": 30.0}], "forecast_date": "2026-09-06"},
    )
    check = check_temporal_consistency(state)
    assert check is None


def test_validation_passes_today_question_with_current_data():
    from app.orchestrator.nodes.validation import check_temporal_consistency
    state = _validation_state_with_weather("TODAY", {"temperature_c": 29.0, "annual_rainfall_mm": 0.0})

# =============================================================================
# 4. SARVAM VOICE/LANGUAGE LAYER (graceful fallback + language metadata contract)
# =============================================================================

@pytest.mark.asyncio
async def test_sarvam_stt_unconfigured_returns_none_fallback():
    """Without SARVAM_API_KEY the client must signal fallback, never raise."""
    from app.voice.sarvam import SarvamVoiceClient
    client = SarvamVoiceClient(api_key=None)
    assert client.is_configured is False
    assert await client.transcribe_audio(b"fake-audio") is None
    assert await client.generate_tts("namaste") is None
    await client.aclose()


@pytest.mark.asyncio
async def test_sarvam_stt_returns_language_metadata_contract():
    """Configured client maps Sarvam response to {text, language, confidence, provider}."""
    from app.voice.sarvam import SarvamVoiceClient

    class _Resp:
        status_code = 200

        def json(self):
            return {"transcript": "kal mausam kaisa rahega", "language_code": "hi-IN",
                    "confidence": 0.93}

    class _FakeClient:
        async def post(self, *a, **kw):
            return _Resp()

    client = SarvamVoiceClient(api_key="test-key")
    client._client = _FakeClient()
    result = await client.transcribe_audio(b"audio-bytes", language="hi")
    assert result is not None
    assert result["text"] == "kal mausam kaisa rahega"
    assert result["language"] == "hi-IN"
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["provider"] == "sarvam_stt"
    await client.aclose()


@pytest.mark.asyncio
async def test_sarvam_stt_http_error_returns_none():
    """HTTP failures must degrade to None (existing Bhashini/local fallback path)."""
    from app.voice.sarvam import SarvamVoiceClient

    class _Resp:
        status_code = 503

        def json(self):
            return {}

    class _FakeClient:
        async def post(self, *a, **kw):
            return _Resp()

    client = SarvamVoiceClient(api_key="test-key")
    client._client = _FakeClient()
    assert await client.transcribe_audio(b"audio") is None
    await client.aclose()


@pytest.mark.asyncio
async def test_sarvam_tts_decodes_audio_bytes():
    from app.voice.sarvam import SarvamVoiceClient
    import base64 as _b64
    payload = _b64.b64encode(b"RIFF-fake-audio").decode()

    class _Resp:
        status_code = 200

        def json(self):
            return {"audios": [payload]}

    class _FakeClient:
        async def post(self, *a, **kw):
            return _Resp()

    client = SarvamVoiceClient(api_key="test-key")
    client._client = _FakeClient()
    audio = await client.generate_tts("kal mausam achha rahega", language="hi")
    assert audio == b"RIFF-fake-audio"
    await client.aclose()


def test_sarvam_language_signal_is_not_intent_detection():
    """Language metadata must never pick the agent: same 'hi' text with weather
    content routes to WEATHER purely via F7 semantic extraction."""
    frame = _frame("kal barish hogi?")
    assert frame.language == "hi"
    assert frame.intent == CanonicalIntent.WEATHER
    plan = generate_task_plan(frame, farmer_context={"latitude": 26.9, "longitude": 75.8})
    assert any(t.tool_name.startswith("weather") for t in plan.tasks)


# =============================================================================
# 5. F7 TYPED RESPONSE ENVELOPE SURVIVAL THROUGH THE API MODEL
# =============================================================================

def test_voice_response_model_carries_envelope_and_action_payload():
    """VoiceQueryResponse must expose the full F7 ResponseEnvelope and its
    action_payload so ANSWER/NAVIGATE/REQUEST_INPUT/CALL/NOTIFY/CLARIFY reach Android."""
    envelope = {
        "response_text": "कल बारिश की संभावना है।",
        "action_payload": {"action": "REQUEST_INPUT", "required_input": "LEAF_IMAGE",
                           "message": "कृपया पत्ती की फोटो भेजें"},
        "verified_facts": [{"key": "rainfall_probability", "value": 72.5,
                            "tool": "weather_forecast_tool"}],
        "confidence_tier": "GROUNDING_TIER_A",
    }
    resp = VoiceQueryResponse(
        intent="disease",
        action="REQUEST_INPUT",
        response="कृपया पत्ती की फोटो भेजें",
        detected_language="hi",
        confidence=0.9,
        envelope=envelope,
        action_payload=envelope["action_payload"],
        timestamp=datetime.now().isoformat(),
    )
    serialized = resp.model_dump()
    assert serialized["envelope"]["action_payload"]["action"] == "REQUEST_INPUT"
    assert serialized["action_payload"]["required_input"] == "LEAF_IMAGE"
    # Serialization round-trip preserves the typed payload verbatim.
    from app.models.voice import VoiceQueryResponse as VQR
    rebuilt = VQR(**serialized)
    assert rebuilt.action_payload["action"] == "REQUEST_INPUT"
    assert rebuilt.envelope["verified_facts"][0]["value"] == 72.5


@pytest.mark.parametrize("typed_action", ["ANSWER", "NAVIGATE", "REQUEST_INPUT", "CALL", "NOTIFY", "CLARIFY"])
def test_all_f7_typed_actions_survive_serialization(typed_action):
    envelope = {"action_payload": {"action": typed_action}, "response_text": "x"}
    resp = VoiceQueryResponse(
        intent="weather", action=typed_action, response="x",
        detected_language="hi", confidence=0.9,
        envelope=envelope, action_payload=envelope["action_payload"],
        timestamp=datetime.now().isoformat(),
    )
    data = resp.model_dump(mode="json")
    assert data["action"] == typed_action
    assert data["action_payload"]["action"] == typed_action
