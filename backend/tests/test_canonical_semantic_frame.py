"""
Unit tests for Phase F2: Canonical Semantic Frame schemas, enums, validation, and serialization.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime, timezone

from app.schemas.semantic_frame import (
    CanonicalIntent,
    CapabilityType,
    RequiredInput,
    ActionIntent,
    NavigationDestination,
    ANDROID_ROUTE_MAP,
    ConfidenceSet,
    SoilValues,
    FarmLocation,
    EntitySet,
    UserContext,
    ConversationContext,
    FarmerRequest,
    SemanticFrame,
    NavigationAction,
    CallingAction,
    ToolInvocation,
    PlannedTask,
    ToolResultReference,
    ResponseEnvelope,
)


def test_confidence_set_validation():
    """ConfidenceSet must enforce 0.0 <= conf <= 1.0."""
    conf = ConfidenceSet(
        language_confidence=0.98,
        intent_confidence=0.92,
        entity_confidence=0.88,
        overall_confidence=0.88,
    )
    assert conf.language_confidence == 0.98
    assert conf.overall_confidence == 0.88

    # Test out of bounds
    with pytest.raises(ValidationError):
        ConfidenceSet(
            language_confidence=1.5,
            intent_confidence=0.9,
            entity_confidence=0.8,
            overall_confidence=0.8,
        )


def test_entity_set_no_fake_defaults():
    """Missing entities must remain None/empty and not hallucinate defaults."""
    entities = EntitySet()
    assert entities.crop is None
    assert entities.disease is None
    assert entities.market is None
    assert entities.markets == []
    assert entities.forecast_days is None
    assert entities.soil_values is None


def test_navigation_action_route_mapping():
    """NavigationAction must automatically map valid destinations to Android routes."""
    nav = NavigationAction(
        destination=NavigationDestination.DISEASE_SCAN,
        message="Please scan the leaf."
    )
    assert nav.action == ActionIntent.NAVIGATE
    assert nav.destination == NavigationDestination.DISEASE_SCAN
    assert nav.android_route == "crop_disease"

    nav_mandi = NavigationAction(
        destination=NavigationDestination.MANDI,
        message="Opening Mandi Prices"
    )
    assert nav_mandi.android_route == "mandi_prices"


def test_navigation_invalid_destination_rejection():
    """Invalid or invented navigation destination must raise ValidationError."""
    with pytest.raises(ValidationError):
        NavigationAction(
            destination="SECRET_ADMIN_SCREEN", # Not in enum
            message="Invalid"
        )


def test_calling_action_structure():
    """Calling action must validate phone number and urgency."""
    call = CallingAction(
        target_phone="+919876543210",
        caller_name="Ramesh Patel",
        reason="CRITICAL_FLOOD_ALERT",
        urgency="CRITICAL",
        script_context={"water_level_m": 4.2}
    )
    assert call.action == ActionIntent.CALL
    assert call.target_phone == "+919876543210"
    assert call.urgency == "CRITICAL"


# =============================================================================
# TESTS FOR THE 5 REQUIRED SPECIFICATION EXAMPLES
# =============================================================================

def test_example_a_mandi_price():
    """
    Example A:
    User: 'Gehu ka mandi bhav kya hai Jaipur mein?'
    Expected: intent = MANDI_PRICE, crop = wheat, market = Jaipur, required_input = NONE
    """
    frame = SemanticFrame(
        request_id="req_001",
        session_id="sess_101",
        raw_text="Gehu ka mandi bhav kya hai Jaipur mein?",
        normalized_text="गेहूं का मंडी भाव क्या है जयपुर में",
        language="hi",
        intent=CanonicalIntent.MANDI_PRICE,
        required_capabilities=[CapabilityType.CURRENT_PRICE],
        entities=EntitySet(crop="Wheat", market="Jaipur", city="Jaipur"),
        required_input=RequiredInput.NONE,
        confidence=ConfidenceSet(
            language_confidence=0.98,
            intent_confidence=0.95,
            entity_confidence=0.92,
            overall_confidence=0.92,
        ),
    )
    assert frame.intent == CanonicalIntent.MANDI_PRICE
    assert frame.entities.crop == "Wheat"
    assert frame.entities.market == "Jaipur"
    assert frame.required_input == RequiredInput.NONE
    assert CapabilityType.CURRENT_PRICE in frame.required_capabilities


def test_example_b_disease_detection_image_gate():
    """
    Example B:
    User: 'Meri gehun ki fasal mein kaunsi bimari hai?'
    Expected: intent = DISEASE_DETECTION, crop = wheat, required_input = LEAF_IMAGE, action = NAVIGATE -> DISEASE_SCAN
    """
    frame = SemanticFrame(
        request_id="req_002",
        session_id="sess_102",
        raw_text="Meri gehun ki fasal mein kaunsi bimari hai?",
        normalized_text="मेरी गेहूं की फसल में कौन सी बीमारी है",
        language="hi",
        intent=CanonicalIntent.DISEASE_DETECTION,
        required_capabilities=[CapabilityType.DISEASE_DETECTION, CapabilityType.RAG_KNOWLEDGE],
        entities=EntitySet(crop="Wheat"),
        required_input=RequiredInput.LEAF_IMAGE,
        confidence=ConfidenceSet(
            language_confidence=0.97,
            intent_confidence=0.94,
            entity_confidence=0.90,
            overall_confidence=0.90,
        ),
    )
    assert frame.intent == CanonicalIntent.DISEASE_DETECTION
    assert frame.entities.crop == "Wheat"
    assert frame.required_input == RequiredInput.LEAF_IMAGE

    # Action generated when LEAF_IMAGE is missing
    nav_action = NavigationAction(
        destination=NavigationDestination.DISEASE_SCAN,
        required_input=RequiredInput.LEAF_IMAGE,
        message="कृपया प्रभावित पत्ती की तस्वीर लें या अपलोड करें।"
    )
    assert nav_action.destination == NavigationDestination.DISEASE_SCAN
    assert nav_action.android_route == "crop_disease"
    assert nav_action.required_input == RequiredInput.LEAF_IMAGE


def test_example_c_irrigation_advisory():
    """
    Example C:
    User: 'Kal barish hogi to gehun mein pani dena chahiye?'
    Expected: intent = IRRIGATION_ADVISORY, crop = wheat, timeframe = tomorrow, capabilities = WEATHER + SMART_IRRIGATION
    """
    frame = SemanticFrame(
        request_id="req_003",
        session_id="sess_103",
        raw_text="Kal barish hogi to gehun mein pani dena chahiye?",
        normalized_text="कल बारिश होगी तो गेहूं में पानी देना चाहिए",
        language="hi",
        intent=CanonicalIntent.IRRIGATION_ADVISORY,
        required_capabilities=[CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION],
        entities=EntitySet(crop="Wheat", timeframe="tomorrow"),
        required_input=RequiredInput.NONE,
        confidence=ConfidenceSet(
            language_confidence=0.96,
            intent_confidence=0.93,
            entity_confidence=0.91,
            overall_confidence=0.91,
        ),
    )
    assert frame.intent == CanonicalIntent.IRRIGATION_ADVISORY
    assert frame.entities.crop == "Wheat"
    assert frame.entities.timeframe == "tomorrow"
    assert CapabilityType.WEATHER in frame.required_capabilities
    assert CapabilityType.SMART_IRRIGATION in frame.required_capabilities


def test_example_d_mandi_decision_and_forecast():
    """
    Example D:
    User: 'Gehu Jaipur mein bechu ya Kalapipal aur agle 7 din ka bhav kya rahega?'
    Expected: intent = MANDI_DECISION, crop = wheat, markets = [Jaipur, Kalapipal], forecast_days = 7,
              capabilities = CURRENT_PRICE + MANDI_COMPARISON + MANDI_FORECAST
    """
    frame = SemanticFrame(
        request_id="req_004",
        session_id="sess_104",
        raw_text="Gehu Jaipur mein bechu ya Kalapipal aur agle 7 din ka bhav kya rahega?",
        normalized_text="गेहूं जयपुर में बेचूं या कालापीपल और अगले 7 दिन का भाव क्या रहेगा",
        language="hi",
        intent=CanonicalIntent.MANDI_DECISION,
        required_capabilities=[
            CapabilityType.CURRENT_PRICE,
            CapabilityType.MANDI_COMPARISON,
            CapabilityType.MANDI_FORECAST,
            CapabilityType.MANDI_DECISION
        ],
        entities=EntitySet(
            crop="Wheat",
            markets=["Jaipur", "Kalapipal"],
            forecast_days=7,
            timeframe="next 7 days"
        ),
        required_input=RequiredInput.NONE,
        confidence=ConfidenceSet(
            language_confidence=0.98,
            intent_confidence=0.94,
            entity_confidence=0.93,
            overall_confidence=0.93,
        ),
    )
    assert frame.intent == CanonicalIntent.MANDI_DECISION
    assert frame.entities.crop == "Wheat"
    assert "Jaipur" in frame.entities.markets
    assert "Kalapipal" in frame.entities.markets
    assert frame.entities.forecast_days == 7
    assert CapabilityType.MANDI_COMPARISON in frame.required_capabilities
    assert CapabilityType.MANDI_FORECAST in frame.required_capabilities


def test_example_e_disaster_risk():
    """
    Example E:
    User: 'Flood ka risk hai kya aur kya karna chahiye?'
    Expected: intent = DISASTER_RISK, capabilities = WEATHER + DISASTER_RISK + RAG_KNOWLEDGE
    """
    frame = SemanticFrame(
        request_id="req_005",
        session_id="sess_105",
        raw_text="Flood ka risk hai kya aur kya karna chahiye?",
        normalized_text="बाढ़ का खतरा है क्या और क्या करना चाहिए",
        language="hi",
        intent=CanonicalIntent.DISASTER_RISK,
        required_capabilities=[
            CapabilityType.WEATHER,
            CapabilityType.DISASTER_RISK,
            CapabilityType.RAG_KNOWLEDGE
        ],
        entities=EntitySet(timeframe="next 7 days"),
        required_input=RequiredInput.NONE,
        confidence=ConfidenceSet(
            language_confidence=0.95,
            intent_confidence=0.96,
            entity_confidence=0.88,
            overall_confidence=0.88,
        ),
    )
    assert frame.intent == CanonicalIntent.DISASTER_RISK
    assert CapabilityType.WEATHER in frame.required_capabilities
    assert CapabilityType.DISASTER_RISK in frame.required_capabilities
    assert CapabilityType.RAG_KNOWLEDGE in frame.required_capabilities


# =============================================================================
# MULTILINGUAL, DIALECT, AND SERIALIZATION TESTS
# =============================================================================

def test_multilingual_and_dialect_metadata():
    """Test regional language (Gujarati) and dialect (Marwari) frames."""
    frame = SemanticFrame(
        request_id="req_006",
        session_id="sess_106",
        raw_text="खम्मा घणी, आज मौसम कांई रैवेला?",
        normalized_text="खम्मा घणी आज मौसम कांई रैवेला",
        language="hi",
        dialect="marwari",
        intent=CanonicalIntent.WEATHER,
        required_capabilities=[CapabilityType.WEATHER],
        entities=EntitySet(timeframe="today"),
        confidence=ConfidenceSet(
            language_confidence=0.99,
            intent_confidence=0.96,
            entity_confidence=0.90,
            overall_confidence=0.90,
        ),
        requested_output_language="hi",
    )
    assert frame.dialect == "marwari"
    assert frame.language == "hi"
    assert frame.intent == CanonicalIntent.WEATHER


def test_json_serialization_and_deserialization():
    """SemanticFrame must serialize to JSON and deserialize back losslessly."""
    original_frame = SemanticFrame(
        request_id="req_serial_01",
        session_id="sess_serial_01",
        raw_text="धान में खाद कब डालना है?",
        normalized_text="धान में खाद कब डालना है",
        language="hi",
        intent=CanonicalIntent.AGRICULTURAL_KNOWLEDGE,
        required_capabilities=[CapabilityType.RAG_KNOWLEDGE],
        entities=EntitySet(crop="Paddy", season="Kharif"),
        confidence=ConfidenceSet(
            language_confidence=0.98,
            intent_confidence=0.92,
            entity_confidence=0.95,
            overall_confidence=0.92,
        ),
    )
    json_str = original_frame.model_dump_json()
    assert isinstance(json_str, str)
    assert "Paddy" in json_str

    deserialized = SemanticFrame.model_validate_json(json_str)
    assert deserialized.request_id == original_frame.request_id
    assert deserialized.entities.crop == "Paddy"
    assert deserialized.intent == CanonicalIntent.AGRICULTURAL_KNOWLEDGE
    assert deserialized.confidence.overall_confidence == 0.92


def test_planned_task_and_response_envelope():
    """Test full cycle from PlannedTask execution DAG to ResponseEnvelope."""
    task = PlannedTask(
        plan_id="plan_001",
        request_id="req_001",
        intent=CanonicalIntent.IRRIGATION_ADVISORY,
        tool_invocations=[
            ToolInvocation(
                invocation_id="inv_1",
                tool_name="weather_tool",
                capability=CapabilityType.WEATHER,
                inputs={"latitude": 26.9124, "longitude": 75.7873},
                order_index=0,
            ),
            ToolInvocation(
                invocation_id="inv_2",
                tool_name="smart_irrigation_tool",
                capability=CapabilityType.SMART_IRRIGATION,
                inputs={"crop": "Wheat"},
                order_index=1,
                depends_on=["inv_1"],
            ),
        ],
        explanation="Fetch weather forecast followed by soil moisture calculation."
    )
    assert len(task.tool_invocations) == 2
    assert task.tool_invocations[1].depends_on == ["inv_1"]

    envelope = ResponseEnvelope(
        request_id="req_001",
        session_id="sess_101",
        language="hi",
        action=ActionIntent.ANSWER,
        response_text="कल 18 मिमी बारिश का अनुमान है। आज गेहूं में सिंचाई रोक दें।",
        confidence=ConfidenceSet(
            language_confidence=0.98,
            intent_confidence=0.95,
            entity_confidence=0.90,
            overall_confidence=0.90,
        ),
        follow_up_suggestions=["मौसम का 7 दिन का पूर्वानुमान", "मंडी भाव देखें"],
    )
    assert envelope.action == ActionIntent.ANSWER
    assert "सिंचाई रोक दें" in envelope.response_text
