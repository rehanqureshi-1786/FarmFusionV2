"""
Phase F6 Hardening Golden Tests Suite.
Tests the 10 critical end-to-end verification points:
1. Low-confidence disease: 0.14 confidence must remain low/unclear, final response confidence <= 0.14
2. Healthy-vs-disease contradiction: flagged as INVALID/CONFLICTING by validation node
3. Mandi compound intent: Hindi, Hinglish, English queries produce CURRENT_PRICE + MANDI_DECISION
4. 7-day disaster query: preserves 7_DAYS horizon, not hijacked by current weather
5. High-confidence disease: confirmed diagnosis with verified RAG management
6. Low-confidence disaster: preserves LOW risk without false alarms
7. Multi-tool weather + irrigation: verified temperature, humidity, and actionable irrigation advice
8. Disease + weather + RAG: composite execution preserving individual facts
9. Mandi current + forecast + decision: numerical consistency between Agmarknet price and advisory
10. Missing image -> navigation: routes to DISEASE_SCAN with required_input=LEAF_IMAGE
"""

import pytest
import pytest_asyncio
from typing import Dict, Any

from app.orchestrator.semantic_extractor import extract_semantic_frame
from app.schemas.semantic_frame import CanonicalIntent, CapabilityType
from app.orchestrator.nodes.validation import (
    validation_node,
    compute_deterministic_confidence,
    check_disease_contradictions,
)
from app.orchestrator.nodes.synthesizer import (
    deterministic_fallback_synthesizer,
    verify_numerical_immutability,
    response_synthesizer_node,
)
from app.schemas.validation import VerifiedFact, ValidationResult
from app.schemas.envelope import ResponseEnvelope, StructuredActionPayload


# ==============================================================================
# GOLDEN TEST 1: Low-Confidence Disease (Confidence Immutability)
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_01_low_confidence_disease_immutability():
    """
    Disease model confidence = 0.14, tier = UNCLEAR.
    Final answer MUST remain LOW/UNCLEAR and final confidence MUST NOT inflate (<= 0.14).
    """
    model_conf = 0.14
    state: Dict[str, Any] = {
        "user_input": "मेरी फसल में क्या बीमारी है?",
        "detected_language": "hi",
        "intent": "disease",
        "intent_confidence": 0.90,
        "confidence_tier": "unclear",
        "tool_output": {
            "disease_name": "Tomato Mosaic Virus",
            "hindi_name": "टमाटर मोज़ेक वायरस",
            "confidence": model_conf,
            "model_confidence": model_conf,
            "confidence_tier": "unclear",
        },
        "tool_results": {
            "disease_1": {
                "disease_name": "Tomato Mosaic Virus",
                "hindi_name": "टमाटर मोज़ेक वायरस",
                "confidence": model_conf,
                "confidence_tier": "unclear",
            }
        },
    }

    # Run validation node
    val_state = await validation_node(state)
    val_result: ValidationResult = ValidationResult(**val_state["validation_result"])
    assert val_result.confidence_tier == "unclear"
    assert val_result.aggregated_confidence <= 0.14, f"Confidence inflated! Got {val_result.aggregated_confidence}"
    assert val_state["aggregated_confidence"] <= 0.14

    # Run response synthesizer
    syn_state = await response_synthesizer_node(val_state)
    envelope: Dict[str, Any] = syn_state["response_envelope"]

    # Invariants
    assert envelope["confidence"] <= 0.14, f"Envelope confidence inflated to {envelope['confidence']}!"
    assert envelope["confidence_tier"] in ["unclear", "low"]
    
    # Check wording does not claim certainty
    resp_text = envelope["response_text"]
    assert "विश्वसनीयता बहुत कम" in resp_text or "UNCLEAR" in resp_text or "कम" in resp_text
    assert "स्पष्ट लक्षण हैं" not in resp_text
    assert "पक्का लक्षण" not in resp_text


# ==============================================================================
# GOLDEN TEST 2: Contradictory Disease Result
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_02_contradictory_disease_result_rejection():
    """
    Contradiction: model predicts Tomato Mosaic Virus, but downstream image or
    rag indicates 'No Plant Detected' or leaf is healthy.
    Validation node must flag as INVALID/BLOCKING.
    Synthesizer must refuse confident answer and request fresh photo.
    """
    tool_output = {
        "disease_name": "Tomato Mosaic Virus",
        "confidence": 0.78,
        "is_plant": False,  # Contradiction: Pathogen diagnosed on non-plant!
        "plant_confidence": 0.10,
    }
    tool_results = {"disease_1": tool_output}

    from app.schemas.validation import VerifiedFactSet
    check = check_disease_contradictions(
        {"tool_results": tool_results, "tool_output": tool_output},
        VerifiedFactSet(facts=[]),
    )
    assert check is not None
    assert check.passed is False
    assert "non-plant" in check.details.lower()

    state: Dict[str, Any] = {
        "user_input": "यह कौन सा रोग है?",
        "detected_language": "hi",
        "intent": "disease",
        "intent_confidence": 0.85,
        "tool_output": tool_output,
        "tool_results": tool_results,
    }

    val_state = await validation_node(state)
    val_res = val_state["validation_result"]
    assert val_res["is_valid"] is False
    assert any("contradiction" in str(w).lower() for w in val_res["warnings"])

    syn_state = await response_synthesizer_node(val_state)
    env = syn_state["response_envelope"]
    assert env["action_payload"]["action"] == "REQUEST_INPUT"
    assert env["action_payload"]["required_input"] == "LEAF_IMAGE"
    assert "विरोधाभासी" in env["response_text"] or "Contradictory" in env["response_text"]


# ==============================================================================
# GOLDEN TEST 3: Mandi Compound Intent (Hindi, Hinglish, English)
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_03_mandi_compound_intent_multilingual():
    """
    Queries asking price + sell/hold decision in Hindi, Hinglish, and English
    must resolve to MANDI_DECISION with CURRENT_PRICE, MANDI_FORECAST, and MANDI_DECISION capabilities.
    """
    queries = [
        # Hindi
        "कोटा मंडी में सोयाबीन का क्या भाव है और क्या मुझे अभी बेचना चाहिए?",
        # Hinglish
        "Kota mandi me soybean ka kya rate chal raha hai aur kya mujhe abhi bechna chahiye ya ruku?",
        # English
        "What is the price of soybean in Kota mandi and should I sell now?",
    ]

    for q in queries:
        frame = await extract_semantic_frame(q)
        assert frame.intent == CanonicalIntent.MANDI_DECISION, f"Failed for query: {q}"
        assert CapabilityType.CURRENT_PRICE in frame.required_capabilities, f"Missing CURRENT_PRICE for: {q}"
        assert CapabilityType.MANDI_DECISION in frame.required_capabilities, f"Missing MANDI_DECISION for: {q}"
        assert CapabilityType.MANDI_FORECAST in frame.required_capabilities, f"Missing MANDI_FORECAST for: {q}"


# ==============================================================================
# GOLDEN TEST 4: 7-Day Disaster Query (Time Horizon Grounding)
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_04_7_day_disaster_query_horizon_grounding():
    """
    'अगले 7 दिन बाढ़ का खतरा है?'
    The plan and response must preserve 7_DAYS horizon and not collapse into current weather.
    """
    q = "अगले 7 दिन बाढ़ का खतरा है?"
    frame = await extract_semantic_frame(q)
    assert frame.intent == CanonicalIntent.DISASTER_RISK
    assert frame.entities.forecast_days == 7 or frame.entities.timeframe is not None

    # Mock executed state with 7-day disaster prediction
    state: Dict[str, Any] = {
        "user_input": q,
        "detected_language": "hi",
        "intent": "disaster_risk",
        "intent_confidence": 0.92,
        "forecast_horizon": "7_DAYS",
        "tool_output": {
            "forecast_days": 7,
            "forecast_horizon": "7_DAYS",
            "location": "कोटा",
            "peak_disaster_type": "Low Risk",
            "peak_risk_level": "LOW",
            "peak_risk_score": 14.0,
            "has_critical_alert": False,
        },
        "tool_results": {
            "weather_1": {"temperature_c": 32.0, "humidity_percent": 60},
            "disaster_1": {
                "forecast_days": 7,
                "forecast_horizon": "7_DAYS",
                "location": "कोटा",
                "peak_disaster_type": "Low Risk",
                "peak_risk_level": "LOW",
                "peak_risk_score": 14.0,
            },
        },
    }

    val_state = await validation_node(state)
    assert val_state["forecast_horizon"] == "7_DAYS"
    facts = {f["key"]: f["value"] for f in val_state["verified_facts"]}
    assert facts.get("forecast_horizon") == "7_DAYS"

    syn_state = await response_synthesizer_node(val_state)
    env = syn_state["response_envelope"]
    resp_text = env["response_text"]

    # Must preserve 7-day horizon in Hindi response
    assert "अगले 7 दिनों में" in resp_text
    assert "बाढ़ या गंभीर" in resp_text or "Low Risk" in resp_text
    # Must NOT be replaced with current weather report
    assert not resp_text.startswith("आज")


# ==============================================================================
# GOLDEN TEST 5: High-Confidence Disease
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_05_high_confidence_disease():
    """
    Disease model confidence = 0.88 (HIGH tier).
    Response confirms diagnosis and includes verified RAG management advice.
    """
    state: Dict[str, Any] = {
        "user_input": "टमाटर में यह कौन सा रोग है?",
        "detected_language": "hi",
        "intent": "disease",
        "intent_confidence": 0.95,
        "confidence_tier": "high",
        "tool_output": {
            "disease_name": "Tomato Early Blight",
            "hindi_name": "टमाटर अगेती झुलसा",
            "confidence": 0.88,
            "model_confidence": 0.88,
            "confidence_tier": "high",
            "chemical_control": "मैंकोजेब 75 WP 2 ग्राम प्रति लीटर पानी में मिलाकर छिड़काव करें।",
        },
        "tool_results": {
            "disease_1": {
                "disease_name": "Tomato Early Blight",
                "confidence": 0.88,
                "confidence_tier": "high",
            }
        },
        "rag_grounding": {
            "status": "grounded",
            "documents": [{"content": "अगेती झुलसा के नियंत्रण हेतु मैंकोजेब या कॉपर ऑक्सीक्लोराइड का छिड़काव करें।"}],
        },
    }

    val_state = await validation_node(state)
    assert val_state["validation_result"]["confidence_tier"] == "high"
    assert val_state["aggregated_confidence"] >= 0.75

    syn_state = await response_synthesizer_node(val_state)
    env = syn_state["response_envelope"]
    assert env["action_payload"]["action"] == "ANSWER"
    assert env["confidence_tier"] == "high"
    assert "स्पष्ट लक्षण हैं" in env["response_text"] or "88%" in env["response_text"]


# ==============================================================================
# GOLDEN TEST 6: Low-Confidence Disaster
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_06_low_confidence_disaster():
    """
    Disaster risk score is LOW (15.0).
    Response communicates Low Risk, safe conditions, and does NOT trigger alert call.
    """
    state: Dict[str, Any] = {
        "user_input": "क्या चक्रवात या आंधी का खतरा है?",
        "detected_language": "hi",
        "intent": "disaster_risk",
        "intent_confidence": 0.85,
        "tool_output": {
            "location": "जयपुर",
            "peak_disaster_type": "Low Risk",
            "peak_risk_level": "LOW",
            "peak_risk_score": 15.0,
            "has_critical_alert": False,
        },
        "tool_results": {
            "disaster_1": {
                "location": "जयपुर",
                "peak_disaster_type": "Low Risk",
                "peak_risk_level": "LOW",
                "peak_risk_score": 15.0,
            }
        },
    }

    val_state = await validation_node(state)
    syn_state = await response_synthesizer_node(val_state)
    env = syn_state["response_envelope"]

    assert env["action_payload"]["action"] == "ANSWER"
    assert env["action_payload"]["action"] != "CALL"
    assert "सुरक्षित" in env["response_text"] or "Low Risk" in env["response_text"]


# ==============================================================================
# GOLDEN TEST 7: Multi-Tool Weather + Irrigation
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_07_multitool_weather_and_irrigation():
    """
    Weather + smart irrigation multi-tool execution.
    Verified fact set captures temperature, humidity, and actionable irrigation advice.
    """
    state: Dict[str, Any] = {
        "user_input": "आज मौसम कैसा है और क्या सिंचाई करें?",
        "detected_language": "hi",
        "intent": "weather",
        "intent_confidence": 0.90,
        "tool_output": {
            "temperature_c": 31.5,
            "humidity_percent": 55,
            "condition": "धूप",
            "location_name": "कोटा",
            "smart_irrigation": {
                "actionable_advice": "शाम के समय हल्की सिंचाई करें, तेज धूप में पानी न दें।"
            },
        },
        "tool_results": {
            "weather_1": {
                "temperature_c": 31.5,
                "humidity_percent": 55,
                "condition": "धूप",
                "location_name": "कोटा",
            },
            "irrigation_1": {
                "actionable_advice": "शाम के समय हल्की सिंचाई करें, तेज धूप में पानी न दें।"
            },
        },
    }

    val_state = await validation_node(state)
    facts = {f["key"]: f["value"] for f in val_state["verified_facts"]}
    assert facts.get("temperature_c") == 31.5
    assert facts.get("humidity_percent") == 55.0

    syn_state = await response_synthesizer_node(val_state)
    env = syn_state["response_envelope"]
    assert "31.5" in env["response_text"] or "31.5°C" in env["response_text"]
    assert "सिंचाई" in env["response_text"]


# ==============================================================================
# GOLDEN TEST 8: Disease + Weather + RAG Composite Plan
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_08_disease_weather_rag_composite():
    """
    Composite execution where leaf disease is evaluated alongside weather/irrigation context.
    Validation extracts facts from specialist tools, not getting overwritten by RAG.
    """
    state: Dict[str, Any] = {
        "user_input": "टमाटर में पत्ती पर धब्बे हैं और बारिश होने वाली है, क्या दवा छिड़कें?",
        "detected_language": "hi",
        "intent": "disease",
        "intent_confidence": 0.88,
        "tool_output": {"matches": [{"title": "ICAR Tomato Guide"}]},  # RAG was last
        "tool_results": {
            "disease_1": {
                "disease_name": "Tomato Early Blight",
                "confidence": 0.82,
                "confidence_tier": "high",
            },
            "weather_1": {
                "temperature_c": 27.0,
                "humidity_percent": 85,
            },
            "rag_1": {
                "matches": [{"title": "ICAR Tomato Guide"}],
            },
        },
    }

    val_state = await validation_node(state)
    facts = {f["key"]: f["value"] for f in val_state["verified_facts"]}
    assert "detected_disease" in facts
    assert facts["detected_disease"] == "Tomato Early Blight"
    assert facts["disease_confidence"] == 0.82


# ==============================================================================
# GOLDEN TEST 9: Mandi Current + Forecast + Decision
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_09_mandi_current_forecast_decision():
    """
    Full Mandi intelligence chain:
    Agmarknet modal price: ₹4,650
    Prophet+LightGBM 7-day target: ₹4,820 (+3.6%)
    Deterministic decision: HOLD_FOR_TARGET
    Verifies numerical consistency across verified facts and response envelope.
    """
    state: Dict[str, Any] = {
        "user_input": "कोटा में सोयाबीन का भाव क्या है और क्या मुझे बेचना चाहिए?",
        "detected_language": "hi",
        "intent": "mandi_decision",
        "intent_confidence": 0.94,
        "tool_output": {
            "current_price": {"modal_price": 4650, "market": "कोटा", "commodity": "सोयाबीन"},
            "deterministic_action": {
                "action": "HOLD_FOR_TARGET",
                "target_price": 4820,
                "expected_pct_change": 3.6,
            },
        },
        "tool_results": {
            "mandi_price_1": {"modal_price": 4650, "market": "कोटा", "commodity": "सोयाबीन"},
            "forecast_1": {"predicted_max": 4820, "expected_pct_change": 3.6, "trend": "upward"},
            "decision_1": {"action": "HOLD_FOR_TARGET", "target_price": 4820, "expected_pct_change": 3.6},
        },
    }

    val_state = await validation_node(state)
    facts = {f["key"]: f["value"] for f in val_state["verified_facts"]}
    assert facts.get("mandi_current_price") == 4650.0

    syn_state = await response_synthesizer_node(val_state)
    env = syn_state["response_envelope"]
    resp_text = env["response_text"]

    assert "4650" in resp_text
    assert "HOLD" in resp_text or "रोकें" in resp_text


# ==============================================================================
# GOLDEN TEST 10: Missing Image -> Navigation
# ==============================================================================
@pytest.mark.asyncio
async def test_golden_10_missing_image_navigation():
    """
    Disease detection query with missing leaf photo.
    Must route to NAVIGATE with destination=DISEASE_SCAN and required_input=LEAF_IMAGE.
    """
    q = "मेरी फसल में कोई कीड़ा या बीमारी लग गई है, जांच करो"
    frame = await extract_semantic_frame(q)
    assert frame.intent == CanonicalIntent.DISEASE_DETECTION
    assert frame.required_input.value == "LEAF_IMAGE"

    state: Dict[str, Any] = {
        "user_input": q,
        "detected_language": "hi",
        "intent": "disease",
        "intent_confidence": 0.88,
        "requires_input": True,
        "required_input": "LEAF_IMAGE",
        "next_action": "NAVIGATE",
        "tool_status": "requires_photo",
        "tool_output": {},
        "tool_results": {},
    }

    val_state = await validation_node(state)
    syn_state = await response_synthesizer_node(val_state)
    env = syn_state["response_envelope"]

    assert env["action_payload"]["action"] == "NAVIGATE"
    assert env["action_payload"]["destination"] == "DISEASE_SCAN"
    assert env["action_payload"]["required_input"] == "LEAF_IMAGE"
    assert "फोटो" in env["response_text"]


# ==============================================================================
# CRITICAL FIX 6 TEST: Model Identity Verification
# ==============================================================================
def test_fix6_model_identity_provenance():
    """
    Assert that Crop Recommendation reports XGBoost / ICAR Agronomic Suitability,
    and NEVER falsely claims LightGBM.
    Assert that Mandi Price Forecasting reports Prophet + LightGBM.
    Assert that Disease Detection reports EfficientNet-B3.
    """
    from app.tools.contracts import CAPABILITY_CONTRACTS, CapabilityType
    
    crop_contract = CAPABILITY_CONTRACTS[CapabilityType.CROP_RECOMMENDATION]
    assert "LightGBM" not in crop_contract.provenance_source
    assert "XGBoost" in crop_contract.provenance_source or "ICAR" in crop_contract.provenance_source
    
    mandi_contract = CAPABILITY_CONTRACTS[CapabilityType.MANDI_FORECAST]
    assert "Prophet" in mandi_contract.provenance_source
    assert "LightGBM" in mandi_contract.provenance_source
    
    disease_contract = CAPABILITY_CONTRACTS[CapabilityType.DISEASE_DETECTION]
    assert "EfficientNet-B3" in disease_contract.provenance_source


# ==============================================================================
# CRITICAL FIX 7 TEST: Numerical & Semantic Consistency Guard
# ==============================================================================
def test_fix7_numerical_and_semantic_consistency_rejections():
    """
    verify_numerical_immutability must reject:
    - altered confidence / probabilities
    - altered risk levels (claiming safe when verified is HIGH, or vice versa)
    - changed prices (e.g. verified ₹2,260 -> candidate ₹2,500)
    - changed weather values (e.g. verified 32.5°C -> candidate 35.0°C)
    """
    facts = [
        VerifiedFact(key="mandi_current_price", value=2260.0, unit="INR/quintal", source_tool="mandi_tool", is_numeric=True),
        VerifiedFact(key="temperature_c", value=32.5, unit="C", source_tool="weather_tool", is_numeric=True),
        VerifiedFact(key="rainfall_mm", value=45.0, unit="mm", source_tool="weather_tool", is_numeric=True),
        VerifiedFact(key="disaster_risk_level", value="HIGH", unit=None, source_tool="disaster_tool", is_numeric=False),
    ]

    # 1. Reject altered price
    valid, violations = verify_numerical_immutability("आज मंडी में भाव ₹2500 प्रति क्विंटल है।", facts)
    assert valid is False
    assert any("price" in v.lower() for v in violations)

    # 2. Reject altered temperature
    valid, violations = verify_numerical_immutability("आज तापमान 38°C रहेगा।", facts)
    assert valid is False
    assert any("temperature" in v.lower() for v in violations)

    # 3. Reject altered rainfall
    valid, violations = verify_numerical_immutability("लगभग 80 mm बारिश होने की संभावना है।", facts)
    assert valid is False
    assert any("rainfall" in v.lower() for v in violations)

    # 4. Reject altered risk level (contradicting verified HIGH with claim of safe / low risk)
    valid, violations = verify_numerical_immutability("किसान भाई, कोई खतरा नहीं है, मौसम एकदम सुरक्षित और low risk है।", facts)
    assert valid is False
    assert any("high risk level" in v.lower() for v in violations)

    # 5. Accept exact verified numbers
    valid, violations = verify_numerical_immutability(
        "आज मंडी में भाव ₹2260 प्रति क्विंटल है, तापमान 32.5°C और बारिश 45 mm दर्ज की गई है।",
        facts,
    )
    assert valid is True
    assert len(violations) == 0
