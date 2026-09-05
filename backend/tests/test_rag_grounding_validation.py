"""
Unit and integration tests for Phase F6:
Conditional RAG Grounding + Validation/Safety + Grounded Response Synthesis + ResponseEnvelope.
"""
import pytest
import pytest_asyncio
from typing import Any, Dict, List

from app.orchestrator.state import OrchestratorState
from app.orchestrator.nodes.rag_grounding import (
    rag_grounding_node,
    should_trigger_rag_grounding,
    construct_verified_rag_query,
    SIMILARITY_HIGH_THRESHOLD,
    SIMILARITY_LOW_THRESHOLD,
)
from app.orchestrator.nodes.validation import (
    validation_node,
    extract_verified_facts_from_state,
    check_cross_tool_consistency,
)
from app.orchestrator.nodes.synthesizer import (
    response_synthesizer_node,
    verify_numerical_immutability,
    deterministic_fallback_synthesizer,
)
from app.schemas.rag import EvidenceLevel, RAGCitation, RAGGroundingResult
from app.schemas.validation import (
    CheckSeverity,
    ValidationResult,
    VerifiedFact,
    VerifiedFactSet,
)
from app.schemas.envelope import ResponseEnvelope, StructuredActionPayload


@pytest.mark.asyncio
async def test_should_trigger_rag_grounding():
    """Verify conditional RAG grounding activation rules."""
    # Disease triggers RAG
    state_disease: OrchestratorState = {"intent": "disease", "tool_results": {"disease_tool": {"disease_name": "Early Blight"}}}
    should_run, domain = should_trigger_rag_grounding(state_disease)
    assert should_run is True
    assert domain == "disease"

    # Crop triggers RAG
    state_crop: OrchestratorState = {"intent": "crop_recommendation", "tool_results": {"crop_rec_tool": {"top_crop": "Wheat"}}}
    should_run, domain = should_trigger_rag_grounding(state_crop)
    assert should_run is True
    assert domain == "crop"

    # Disaster triggers RAG
    state_disaster: OrchestratorState = {"intent": "disaster_risk", "tool_results": {"disaster_tool": {"peak_disaster_type": "Flood Risk"}}}
    should_run, domain = should_trigger_rag_grounding(state_disaster)
    assert should_run is True
    assert domain == "disaster"

    # Schemes triggers RAG
    state_scheme: OrchestratorState = {"intent": "scheme", "user_input": "PM Kisan eligibility"}
    should_run, domain = should_trigger_rag_grounding(state_scheme)
    assert should_run is True
    assert domain == "scheme"

    # Pure navigation skips RAG
    state_nav: OrchestratorState = {"intent": "navigation", "next_action": "NAVIGATE"}
    should_run, domain = should_trigger_rag_grounding(state_nav)
    assert should_run is False
    assert domain == "none"

    # Clarification skips RAG
    state_clarify: OrchestratorState = {"requires_clarification": True, "intent": "clarify"}
    should_run, domain = should_trigger_rag_grounding(state_clarify)
    assert should_run is False
    assert domain == "none"


@pytest.mark.asyncio
async def test_construct_verified_rag_query():
    """Verify authoritatively formed queries contain confirmed entities only."""
    state: OrchestratorState = {
        "tool_results": {
            "disease_detection_tool": {
                "disease_name": "Tomato Early Blight",
                "crop": "Tomato",
            }
        }
    }
    query, doc_type, crop = construct_verified_rag_query(state, "disease")
    assert "Tomato Early Blight" in query
    assert "treatment management" in query
    assert doc_type == "disease_guide"
    assert crop == "tomato"


@pytest.mark.asyncio
async def test_rag_grounding_live_vector_retrieval():
    """Test live pgvector retrieval on real Tomato Early Blight query."""
    state: OrchestratorState = {
        "intent": "disease",
        "tool_results": {
            "disease_tool": {
                "disease_name": "Early Blight",
                "crop": "Tomato",
            }
        },
        "active_crop": "Tomato",
    }
    updated_state = await rag_grounding_node(state)
    rag_res = updated_state.get("rag_grounding")
    assert rag_res is not None
    assert rag_res["status"] == "SUCCESS"
    assert rag_res["evidence_level"] in [EvidenceLevel.HIGH_EVIDENCE.value, EvidenceLevel.LOW_EVIDENCE.value]
    assert len(rag_res["documents"]) > 0
    assert len(rag_res["citations"]) > 0

    # Ensure no fabricated citations
    citation = rag_res["citations"][0]
    assert citation["chunk_id"] > 0
    assert "title" in citation
    assert "organization" in citation


def test_validation_fact_extraction():
    """Verify extraction of immutable fact set from tool executions."""
    state: OrchestratorState = {
        "tool_results": {
            "mandi_tool": {
                "current_price": 2260.0,
                "daily_forecasts": [{"date": "2024-09-10", "predicted_price": 2350.0}],
                "deterministic_action": {"action": "HOLD_FOR_TARGET", "expected_pct_change": 4.0},
            },
            "weather_tool": {
                "temperature_c": 29.0,
                "humidity_percent": 96.0,
                "annual_rainfall_mm": 35.0,
            },
            "disaster_tool": {
                "peak_risk_level": "HIGH",
                "peak_risk_score": 78.0,
                "peak_disaster_type": "Flood Risk",
            },
            "disease_tool": {
                "disease_name": "Early Blight",
                "confidence": 0.88,
            }
        }
    }
    facts = extract_verified_facts_from_state(state)
    assert facts.get_fact("mandi_current_price").value == 2260.0
    assert facts.get_fact("temperature_c").value == 29.0
    assert facts.get_fact("humidity_percent").value == 96.0
    assert facts.get_fact("disaster_risk_level").value == "HIGH"
    assert facts.get_fact("disaster_risk_score").value == 78.0
    assert facts.get_fact("disease_confidence").value == 0.88


def test_cross_tool_consistency_check():
    """Verify cross-tool discrepancy detection between weather and irrigation."""
    # Heavy rain predicted (80%) vs immediate irrigation advice WATER_NOW
    state: OrchestratorState = {
        "tool_results": {
            "weather_tool": {
                "precipitation_probability_max": 85.0,
                "annual_rainfall_mm": 120.0,
            },
            "smart_irrigation_tool": {
                "status": "WATER_NOW",
            }
        }
    }
    facts = extract_verified_facts_from_state(state)
    res = check_cross_tool_consistency(state, facts)
    assert res.consistent is False
    assert "Weather forecast predicts heavy rainfall probability" in res.issue_description


@pytest.mark.asyncio
async def test_validation_node_confidence_tiers():
    """Verify Safety Rule #3: confidence tiering high/medium/low/unclear."""
    # High confidence >= 0.75
    state_high: OrchestratorState = {"tool_results": {"disease_tool": {"confidence": 0.82}}}
    s1 = await validation_node(state_high)
    assert s1["confidence_tier"] == "high"

    # Medium confidence 0.45 - 0.74
    state_med: OrchestratorState = {"tool_results": {"disease_tool": {"confidence": 0.60}}}
    s2 = await validation_node(state_med)
    assert s2["confidence_tier"] == "medium"

    # Low confidence 0.30 - 0.44
    state_low: OrchestratorState = {"tool_results": {"disease_tool": {"confidence": 0.38}}}
    s3 = await validation_node(state_low)
    assert s3["confidence_tier"] == "low"

    # Unclear < 0.30
    state_unclear: OrchestratorState = {"tool_results": {"disease_tool": {"confidence": 0.22}}}
    s4 = await validation_node(state_unclear)
    assert s4["confidence_tier"] == "unclear"


def test_numerical_immutability_guard_rejects_altered_numbers():
    """Step 7: Verify rejection of responses that modify or invent numerical facts."""
    facts = [
        VerifiedFact(key="mandi_current_price", value=2260.0, unit="INR/quintal", source_tool="mandi_tool", is_numeric=True),
        VerifiedFact(key="temperature_c", value=29.0, unit="C", source_tool="weather_tool", is_numeric=True),
        VerifiedFact(key="rainfall_mm", value=35.0, unit="mm", source_tool="weather_tool", is_numeric=True),
        VerifiedFact(key="disaster_risk_level", value="HIGH", unit=None, source_tool="disaster_tool", is_numeric=False),
    ]

    # 1. Exact verified numbers -> PASS
    valid_text = "आज मंडी में सोयाबीन का भाव ₹2260 प्रति क्विंटल है। तापमान 29°C और वर्षा 35 mm रहने का अनुमान है।"
    is_valid, violations = verify_numerical_immutability(valid_text, facts)
    assert is_valid is True
    assert len(violations) == 0

    # 2. Altered price (₹2300 instead of ₹2260) -> REJECT
    altered_price_text = "आज मंडी में सोयाबीन का भाव ₹2300 प्रति क्विंटल है।"
    is_valid, violations = verify_numerical_immutability(altered_price_text, facts)
    assert is_valid is False
    assert any("Mandi price altered or invented" in v for v in violations)

    # 3. Altered temperature (35°C instead of 29°C) -> REJECT
    altered_temp_text = "आज क्षेत्र में तापमान 35°C रहेगा।"
    is_valid, violations = verify_numerical_immutability(altered_temp_text, facts)
    assert is_valid is False
    assert any("Temperature altered or invented" in v for v in violations)

    # 4. Contradicting HIGH risk level with claims of low risk -> REJECT
    contradict_text = "मौसम पूरी तरह सुरक्षित और सामान्य (low risk) रहेगा।"
    is_valid, violations = verify_numerical_immutability(contradict_text, facts)
    assert is_valid is False
    assert any("Contradicted verified HIGH risk level" in v for v in violations)


@pytest.mark.asyncio
async def test_response_synthesizer_emits_valid_envelope():
    """Step 4 & Step 17: Verify emission of valid typed ResponseEnvelope."""
    state: OrchestratorState = {
        "intent": "weather",
        "detected_language": "hi",
        "tool_output": {
            "temperature_c": 29.0,
            "humidity_percent": 96.0,
            "condition": "बारिश",
            "location_name": "कोटा",
            "annual_rainfall_mm": 35.0,
        },
        "tool_results": {
            "weather_tool": {
                "temperature_c": 29.0,
                "humidity_percent": 96.0,
                "annual_rainfall_mm": 35.0,
            }
        },
    }
    result_state = await response_synthesizer_node(state)
    envelope_data = result_state.get("response_envelope")
    assert envelope_data is not None

    # Validate against Pydantic ResponseEnvelope schema
    envelope = ResponseEnvelope(**envelope_data)
    assert envelope.response_text is not None
    assert "29" in envelope.response_text
    assert "96" in envelope.response_text
    assert envelope.action_payload.action == "ANSWER"
    assert envelope.language == "hi"
    assert envelope.confidence_tier == "high"


@pytest.mark.asyncio
async def test_disease_without_image_navigates_to_disease_scan():
    """Step 12 & Step 17: Disease without image -> action=NAVIGATE, destination=DISEASE_SCAN."""
    state: OrchestratorState = {
        "intent": "disease",
        "tool_status": "requires_photo",
        "detected_language": "hi",
        "tool_output": {"status": "requires_photo"},
        "tool_results": {},
    }
    result_state = await response_synthesizer_node(state)
    envelope = ResponseEnvelope(**result_state["response_envelope"])
    assert envelope.action_payload.action == "NAVIGATE"
    assert envelope.action_payload.destination == "DISEASE_SCAN"
    assert envelope.action_payload.required_input == "LEAF_IMAGE"


@pytest.mark.asyncio
async def test_critical_disaster_triggers_call_action():
    """Step 14 & Step 17: Critical disaster alert -> action=CALL."""
    state: OrchestratorState = {
        "intent": "disaster_risk",
        "detected_language": "hi",
        "tool_output": {
            "location": "बाड़मेर",
            "forecast_days": 7,
            "peak_disaster_type": "Flood Risk",
            "peak_risk_level": "CRITICAL",
            "peak_risk_score": 92.0,
            "peak_risk_date": "2024-09-08",
            "has_critical_alert": True,
        },
        "tool_results": {
            "disaster_tool": {
                "peak_risk_level": "CRITICAL",
                "peak_risk_score": 92.0,
                "peak_disaster_type": "Flood Risk",
            }
        }
    }
    result_state = await response_synthesizer_node(state)
    envelope = ResponseEnvelope(**result_state["response_envelope"])
    assert envelope.action_payload.action == "CALL"
    assert envelope.action_payload.call_reason == "CRITICAL_DISASTER_ALERT"


@pytest.mark.asyncio
async def test_multilingual_exact_numerical_preservation():
    """Step 19: Multilingual responses must preserve identical numbers across languages."""
    base_state: OrchestratorState = {
        "intent": "mandi",
        "tool_output": {
            "current_price": {
                "commodity": "गेहूं",
                "market": "कोटा",
                "modal_price": 2260.0,
            },
            "deterministic_action": {
                "action": "SELL_NOW",
            }
        },
        "tool_results": {
            "mandi_tool": {
                "current_price": 2260.0,
            }
        }
    }

    languages = ["hi", "gu", "mr", "pa", "en"]
    for lang in languages:
        state = dict(base_state)
        state["detected_language"] = lang
        res = await response_synthesizer_node(state)
        envelope = ResponseEnvelope(**res["response_envelope"])
        # All languages must preserve the exact verified number 2260
        assert "2260" in envelope.response_text, f"Failed for language {lang}: {envelope.response_text}"
