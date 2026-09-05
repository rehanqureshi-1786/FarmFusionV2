"""
Phase F7 Quality Assurance: Hindi / Hinglish Response Quality, Numerical Immutability & English Terms.

Comprehensive test suite covering 16 required invariants:
1. Hindi weather response preserves temperature (°C)
2. Hindi weather response preserves rainfall (mm)
3. Hindi weather response preserves rain probability (%)
4. Hindi weather response preserves units (°C, mm, %, km/h)
5. Hindi mandi response preserves ₹ and unit (प्रति क्विंटल)
6. Hindi irrigation response preserves soil moisture (%)
7. Hindi disaster response preserves risk level (Disaster risk LOW/HIGH)
8. Hinglish response preserves numbers
9. English response remains accurate and intact
10. TTS text equals displayed factual content
11. "kal ka mausam" returns tomorrow data and temporal framing
12. "आज का मौसम" returns today data and temporal framing
13. "इस फसल की देखभाल" inherits crop context from active conversation
14. Missing crop context requests clarification
15. Low RAG evidence cannot become high-confidence
16. Deterministic fallback still preserves verified numbers and symbols
"""
import pytest
from app.orchestrator.semantic_extractor import extract_semantic_frame_deterministic
from app.orchestrator.nodes.synthesizer import (
    response_synthesizer_node,
    deterministic_fallback_synthesizer,
    is_hinglish_query,
)
from app.orchestrator.nodes.validation import (
    validation_node,
    extract_verified_facts_from_state,
    validate_response_temporal_alignment,
)
from app.schemas.semantic_frame import (
    CanonicalIntent,
    CapabilityType,
    ConversationContext,
    SemanticFrame,
    EntitySet,
    TimeContext,
    ConfidenceSet,
)


# =============================================================================
# 1. Hindi weather response preserves temperature
# =============================================================================
@pytest.mark.asyncio
async def test_hindi_weather_response_preserves_temperature():
    state = {
        "user_input": "कल का तापमान क्या रहेगा?",
        "detected_language": "hi",
        "intent": "weather",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 31.0,
            "max_temp_c": 31.0,
            "min_temp_c": 24.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
            "wind_speed_kmh": 18.0,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 31.0,
                "max_temp_c": 31.0,
                "min_temp_c": 24.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
                "wind_speed_kmh": 18.0,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "31°C" in text or "31" in text
    assert "कल" in text


# =============================================================================
# 2. Hindi weather response preserves rainfall
# =============================================================================
@pytest.mark.asyncio
async def test_hindi_weather_response_preserves_rainfall():
    state = {
        "user_input": "कल बारिश कितनी होगी?",
        "detected_language": "hi",
        "intent": "weather",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 28.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
            "wind_speed_kmh": 18.0,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 28.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
                "wind_speed_kmh": 18.0,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "8 mm" in text or "8.0 mm" in text or "8 मिमी" in text


# =============================================================================
# 3. Hindi weather response preserves rain probability
# =============================================================================
@pytest.mark.asyncio
async def test_hindi_weather_response_preserves_rain_probability():
    state = {
        "user_input": "कल बारिश की कितनी संभावना है?",
        "detected_language": "hi",
        "intent": "weather",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 28.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
            "wind_speed_kmh": 18.0,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 28.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
                "wind_speed_kmh": 18.0,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "70%" in text


# =============================================================================
# 4. Hindi weather response preserves units (°C, mm, %, km/h)
# =============================================================================
@pytest.mark.asyncio
async def test_hindi_weather_response_preserves_units():
    state = {
        "user_input": "कल का पूरा मौसम पूर्वानुमान बताओ",
        "detected_language": "hi",
        "intent": "weather",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 31.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
            "wind_speed_kmh": 18.0,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 31.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
                "wind_speed_kmh": 18.0,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "°C" in text
    assert "mm" in text or "मिमी" in text
    assert "%" in text
    assert "km/h" in text or "किमी/घंटा" in text


# =============================================================================
# 5. Hindi mandi response preserves ₹ and unit (प्रति क्विंटल)
# =============================================================================
@pytest.mark.asyncio
async def test_hindi_mandi_response_preserves_rupee_and_unit():
    state = {
        "user_input": "सोयाबीन का आज का मंडी भाव क्या है?",
        "detected_language": "hi",
        "intent": "mandi_price",
        "tool_output": {
            "commodity": "Soybean",
            "hindi_name": "सोयाबीन",
            "modal_price": 4850,
            "price_unit": "₹/क्विंटल",
            "market": "Indore",
        },
        "tool_results": {
            "mandi": {
                "commodity": "Soybean",
                "hindi_name": "सोयाबीन",
                "modal_price": 4850,
                "price_unit": "₹/क्विंटल",
                "market": "Indore",
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "₹4,850" in text or "₹4850" in text
    assert "प्रति क्विंटल" in text
    assert "सोयाबीन" in text


# =============================================================================
# 6. Hindi irrigation response preserves soil moisture
# =============================================================================
@pytest.mark.asyncio
async def test_hindi_irrigation_response_preserves_soil_moisture():
    state = {
        "user_input": "कल irrigation करनी चाहिए क्या?",
        "detected_language": "hi",
        "intent": "smart_irrigation",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "soil_moisture_pct": 22.0,
            "expected_rain_mm": 8.0,
            "recommendation": "सिंचाई की आवश्यकता नहीं है",
            "irrigation_need_score": 0.35,
        },
        "tool_results": {
            "smart_irrigation": {
                "soil_moisture_pct": 22.0,
                "expected_rain_mm": 8.0,
                "recommendation": "सिंचाई की आवश्यकता नहीं है",
                "irrigation_need_score": 0.35,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "22%" in text or "22.0%" in text
    assert "8 mm" in text or "8.0 mm" in text or "8" in text


# =============================================================================
# 7. Hindi disaster response preserves risk level
# =============================================================================
@pytest.mark.asyncio
async def test_hindi_disaster_response_preserves_risk_level():
    state = {
        "user_input": "क्या बाढ़ का खतरा है?",
        "detected_language": "hi",
        "intent": "disaster_alert",
        "tool_output": {
            "risk_level": "LOW",
            "risk_score": 0.18,
            "disaster_type": "flood",
            "alert_status": "MONITORING",
            "recommendations": ["नालियों की निकासी साफ रखें"],
        },
        "tool_results": {
            "disaster_alert": {
                "risk_level": "LOW",
                "risk_score": 0.18,
                "disaster_type": "flood",
                "alert_status": "MONITORING",
                "recommendations": ["नालियों की निकासी साफ रखें"],
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "Disaster risk LOW" in text or "LOW" in text


# =============================================================================
# 8. Hinglish response preserves numbers
# =============================================================================
@pytest.mark.asyncio
async def test_hinglish_response_preserves_numbers():
    state = {
        "user_input": "aaj soybean ka mandi bhav kya chal raha hai?",
        "detected_language": "hi",
        "intent": "mandi_price",
        "tool_output": {
            "commodity": "Soybean",
            "modal_price": 4850,
            "market": "Kota",
        },
        "tool_results": {
            "mandi": {
                "commodity": "Soybean",
                "modal_price": 4850,
                "market": "Kota",
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "4,850" in text or "4850" in text
    assert "Soybean" in text or "सोयाबीन" in text


# =============================================================================
# 9. English response remains unchanged
# =============================================================================
@pytest.mark.asyncio
async def test_english_response_remains_unchanged():
    state = {
        "user_input": "What will the weather be tomorrow?",
        "detected_language": "en",
        "intent": "weather",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 31.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
            "wind_speed_kmh": 18.0,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 31.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
                "wind_speed_kmh": 18.0,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "Tomorrow" in text or "tomorrow" in text
    assert "31°C" in text or "31" in text
    assert "8 mm" in text or "8.0 mm" in text
    assert "70%" in text


# =============================================================================
# 10. TTS text equals displayed factual content
# =============================================================================
@pytest.mark.asyncio
async def test_tts_text_equals_displayed_factual_content():
    state = {
        "user_input": "कल का मौसम कैसा रहेगा?",
        "detected_language": "hi",
        "intent": "weather",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 31.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
            "wind_speed_kmh": 18.0,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 31.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
                "wind_speed_kmh": 18.0,
            }
        },
    }
    res = await response_synthesizer_node(state)
    displayed_text = res["final_response"]
    envelope = res["response_envelope"]
    tts_text = envelope["response_text"]
    assert displayed_text == tts_text
    assert "31°C" in tts_text or "31" in tts_text


# =============================================================================
# 11. "kal ka mausam" returns tomorrow data
# =============================================================================
@pytest.mark.asyncio
async def test_kal_ka_mausam_returns_tomorrow_data():
    sf = extract_semantic_frame_deterministic("कल का मौसम कैसा रहेगा?", detected_language="hi")
    assert sf.entities.time_context.relative_day == "TOMORROW"
    
    state = {
        "user_input": "कल का मौसम कैसा रहेगा?",
        "detected_language": "hi",
        "intent": "weather",
        "semantic_frame": sf.model_dump(),
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 31.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 31.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "कल" in text
    valid, err = validate_response_temporal_alignment(text, "TOMORROW", 1)
    assert valid is True


# =============================================================================
# 12. "आज का मौसम" returns today data
# =============================================================================
@pytest.mark.asyncio
async def test_aaj_ka_mausam_returns_today_data():
    sf = extract_semantic_frame_deterministic("आज का मौसम कैसा रहेगा?", detected_language="hi")
    assert sf.entities.time_context.relative_day == "TODAY"

    state = {
        "user_input": "आज का मौसम कैसा रहेगा?",
        "detected_language": "hi",
        "intent": "weather",
        "semantic_frame": sf.model_dump(),
        "tool_output": {
            "temperature_c": 32.0,
            "humidity_pct": 55,
            "wind_speed_kmh": 12.0,
        },
        "tool_results": {
            "weather": {
                "temperature_c": 32.0,
                "humidity_pct": 55,
                "wind_speed_kmh": 12.0,
            }
        },
    }
    res = await response_synthesizer_node(state)
    text = res["final_response"]
    assert "आज" in text
    valid, err = validate_response_temporal_alignment(text, "TODAY", 1)
    assert valid is True


# =============================================================================
# 13. "इस फसल की देखभाल" inherits crop context
# =============================================================================
def test_is_fasal_ki_dekhbhal_inherits_crop_context():
    ctx = ConversationContext(session_id="s123", farmer_id="f123")
    ctx.active_crop = "Wheat"
    
    sf = extract_semantic_frame_deterministic("इस फसल की देखभाल कैसे करें?", detected_language="hi", conversation_context=ctx)
    assert sf.entities.crop == "Wheat"
    assert sf.intent == CanonicalIntent.GENERAL_AGRICULTURE
    assert CapabilityType.RAG_KNOWLEDGE in sf.required_capabilities


# =============================================================================
# 14. Missing crop context requests clarification
# =============================================================================
def test_missing_crop_context_requests_clarification():
    ctx = ConversationContext(session_id="s123", farmer_id="f123")
    ctx.active_crop = None
    
    sf = extract_semantic_frame_deterministic("इस फसल की देखभाल कैसे करें?", detected_language="hi", conversation_context=ctx)
    assert sf.intent == CanonicalIntent.CLARIFICATION
    assert sf.confidence.intent_confidence == 0.50
    assert sf.required_capabilities == []


# =============================================================================
# 15. Low RAG evidence cannot become high-confidence
# =============================================================================
@pytest.mark.asyncio
async def test_low_rag_evidence_cannot_become_high_confidence():
    state = {
        "user_input": "कपास में गुलाबी सुंडी का उपचार क्या है?",
        "detected_language": "hi",
        "intent": "general_agronomy",
        "rag_grounding": {
            "evidence_strength": "LOW_EVIDENCE",
            "documents": [{"content": "कुछ कीटनाशकों का प्रयोग करें।"}],
            "average_similarity": 0.42,
        },
        "tool_results": {},
    }
    validated_state = await validation_node(state)
    assert validated_state["confidence_tier"] in ["medium", "low"]
    assert validated_state["aggregated_confidence"] <= 0.74


# =============================================================================
# 16. Deterministic fallback still preserves verified numbers
# =============================================================================
def test_deterministic_fallback_still_preserves_verified_numbers():
    state = {
        "intent": "weather",
        "user_input": "कल बारिश होगी क्या?",
        "semantic_frame": {
            "entities": {
                "time_context": {"relative_day": "TOMORROW", "forecast_horizon_days": 1}
            }
        },
        "tool_output": {
            "forecast_date": "2026-09-06",
            "temperature_c": 31.0,
            "expected_rain_mm": 8.0,
            "rain_probability": 70,
            "wind_speed_kmh": 18.0,
        },
        "tool_results": {
            "weather": {
                "forecast_date": "2026-09-06",
                "temperature_c": 31.0,
                "expected_rain_mm": 8.0,
                "rain_probability": 70,
                "wind_speed_kmh": 18.0,
            }
        },
    }
    text, action = deterministic_fallback_synthesizer(
        state, lang="hi", dialect=None, is_marwari=False, conf_tier="high", is_hinglish=False
    )
    assert "कल" in text
    assert "70%" in text
    assert "8 mm" in text or "8.0 mm" in text
    assert "31°C" in text
    assert action.action == "ANSWER"
