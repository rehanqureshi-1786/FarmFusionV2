"""
Comprehensive Test Suite for Phase F5 Task Planner & Dependency-Aware Orchestration.
Covers:
1. DAG topological sorting & cycle detection
2. Required-input gating (Leaf photo, location context)
3. 5 Canonical Golden Multi-Agent Examples
4. 50 Multilingual Planner Test Cases (Hindi, English, Hinglish, Gujarati, Marathi, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam, Marwari)
5. Real Tool Registry execution traces (Weather+Irrigation, Mandi Suite, Disaster Risk)
6. Dynamic result propagation & dependency injection
7. Blocking vs non-blocking failure handling
8. Full LangGraph orchestrator pipeline integration
"""
import pytest
import time
from typing import Any, Dict, List

from app.schemas.semantic_frame import (
    SemanticFrame,
    EntitySet,
    ConfidenceSet,
    CapabilityType,
    RequiredInput,
    CanonicalIntent,
    FarmLocation,
)
from app.orchestrator.planner import (
    TaskPlan,
    PlannedTask,
    PlanStatus,
    TaskStatus,
    ActionType,
    DAGCycleError,
    InvalidDependencyError,
    build_execution_batches,
    generate_task_plan,
    execute_task_plan,
)
from app.orchestrator.graph import run_orchestrator_pipeline
from app.tools.registry import tool_registry


def make_conf(intent_conf: float = 0.95) -> ConfidenceSet:
    return ConfidenceSet(
        language_confidence=0.95,
        intent_confidence=intent_conf,
        entity_confidence=0.95,
        overall_confidence=intent_conf,
    )


def make_frame(
    raw_text: str,
    language: str = "hi",
    intent: CanonicalIntent = CanonicalIntent.GENERAL_AGRICULTURE,
    entities: Any = None,
    required_capabilities: Any = None,
    required_input: RequiredInput = RequiredInput.NONE,
    confidence: Any = None,
    request_id: str = "req_test",
    session_id: str = "sess_test",
    normalized_text: Any = None,
) -> SemanticFrame:
    return SemanticFrame(
        request_id=request_id,
        session_id=session_id,
        raw_text=raw_text,
        normalized_text=normalized_text or raw_text,
        language=language,
        intent=intent,
        entities=entities if entities is not None else EntitySet(),
        required_capabilities=required_capabilities or [],
        required_input=required_input,
        confidence=confidence or make_conf(0.95),
    )


# =============================================================================
# 1. DAG Building, Topological Sorting & Cycle Detection Tests
# =============================================================================

def test_dag_topological_sort_and_parallel_batches():
    """Verify independent tasks are grouped in parallel batches and dependencies are ordered."""
    # Mandi scenario: Price, Compare, Forecast can run concurrently; Decision depends on Price and Forecast
    tasks = [
        PlannedTask(task_id="mandi_price_1", capability=CapabilityType.CURRENT_PRICE, tool_name="mandi_current_price_tool", depends_on=[]),
        PlannedTask(task_id="mandi_compare_1", capability=CapabilityType.MANDI_COMPARISON, tool_name="mandi_comparison_tool", depends_on=[]),
        PlannedTask(task_id="mandi_forecast_1", capability=CapabilityType.MANDI_FORECAST, tool_name="mandi_forecast_tool", depends_on=[]),
        PlannedTask(task_id="mandi_decision_1", capability=CapabilityType.MANDI_DECISION, tool_name="mandi_decision_tool", depends_on=["mandi_price_1", "mandi_forecast_1"]),
    ]
    batches = build_execution_batches(tasks)
    assert len(batches) == 2
    # First batch contains all 3 independent tasks (parallel stage)
    assert set(batches[0]) == {"mandi_price_1", "mandi_compare_1", "mandi_forecast_1"}
    # Second batch contains decision task
    assert batches[1] == ["mandi_decision_1"]


def test_dag_cycle_detection():
    """Verify circular dependencies raise DAGCycleError."""
    cyclic_tasks = [
        PlannedTask(task_id="task_a", capability=CapabilityType.WEATHER, tool_name="weather_tool", depends_on=["task_b"]),
        PlannedTask(task_id="task_b", capability=CapabilityType.SMART_IRRIGATION, tool_name="smart_irrigation_tool", depends_on=["task_a"]),
    ]
    with pytest.raises(DAGCycleError):
        build_execution_batches(cyclic_tasks)


def test_dag_invalid_dependency_error():
    """Verify depending on a non-existent task_id raises InvalidDependencyError."""
    invalid_tasks = [
        PlannedTask(task_id="task_a", capability=CapabilityType.WEATHER, tool_name="weather_tool", depends_on=["non_existent_task"]),
    ]
    with pytest.raises(InvalidDependencyError):
        build_execution_batches(invalid_tasks)


# =============================================================================
# 2. Required-Input Gates Tests
# =============================================================================

def test_disease_diagnosis_without_photo_gate():
    """
    Step 5 Requirement: When disease detection is requested without an image,
    the planner must NEVER guess a disease or call a model.
    It MUST generate an ActionType.NAVIGATE plan to DISEASE_SCAN screen.
    """
    sf = make_frame(
        raw_text="Meri wheat crop mein kaunsi disease hai?",
        language="hi",
        intent=CanonicalIntent.DISEASE_DETECTION,
        entities=EntitySet(crop="Wheat"),
        required_capabilities=[CapabilityType.DISEASE_DETECTION, CapabilityType.RAG_KNOWLEDGE],
        required_input=RequiredInput.LEAF_IMAGE,
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(sf, image_bytes=None, image_path=None)
    assert plan.action_type == ActionType.NAVIGATE
    assert plan.navigation_destination == "DISEASE_SCAN"
    assert plan.navigation_route == "crop_disease"
    assert plan.required_input == RequiredInput.LEAF_IMAGE
    assert len(plan.tasks) == 0  # No tool execution allowed without photo


def test_missing_location_gate_for_weather():
    """Verify physical tools halt and request location if completely absent."""
    sf = make_frame(
        raw_text="Will it rain tomorrow?",
        language="en",
        intent=CanonicalIntent.WEATHER,
        entities=EntitySet(),
        required_capabilities=[CapabilityType.WEATHER],
        confidence=make_conf(0.95),
    )
    # Empty farmer context with no coordinates or district
    plan = generate_task_plan(sf, farmer_context={})
    assert plan.action_type == ActionType.REQUEST_INPUT
    assert plan.required_input == RequiredInput.FARM_LOCATION
    assert "latitude" in plan.unresolved_inputs


def test_direct_navigation_plan():
    """Verify navigation intent generates valid typed navigation action."""
    sf = make_frame(
        raw_text="Mandi bhav wali screen kholo",
        language="hi",
        intent=CanonicalIntent.NAVIGATION_REQUEST,
        entities=EntitySet(additional_entities={"destination": "mandi"}),
        required_capabilities=[CapabilityType.NAVIGATION],
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(sf)
    assert plan.action_type == ActionType.NAVIGATE
    assert plan.navigation_destination == "MANDI"
    assert plan.navigation_route == "mandi_rates"


# =============================================================================
# 3. Five Canonical Multi-Agent Golden Examples
# =============================================================================

def test_golden_example_1_weather_and_irrigation():
    """
    Example 1: 'Kal rain hone wali hai, kya wheat ko water karun?'
    Plan: WEATHER + SMART_IRRIGATION.
    Irrigation must depend on Weather.
    """
    sf = make_frame(
        raw_text="Kal rain hone wali hai, kya wheat ko water karun?",
        language="hi",
        intent=CanonicalIntent.IRRIGATION_ADVISORY,
        entities=EntitySet(crop="Wheat", timeframe="tomorrow"),
        required_capabilities=[CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION],
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(sf, farmer_context={"latitude": 26.9124, "longitude": 75.7873})
    assert plan.action_type == ActionType.EXECUTE_TOOL
    assert len(plan.tasks) == 2
    weather_task = plan.get_task("weather_1")
    irrigation_task = plan.get_task("irrigation_1")
    assert weather_task is not None
    assert irrigation_task is not None
    assert "weather_1" in irrigation_task.depends_on
    assert plan.execution_batches == [["weather_1"], ["irrigation_1"]]


def test_golden_example_2_disease_missing_photo():
    """Example 2: 'Meri wheat crop mein kaunsi disease hai?' without image."""
    sf = make_frame(
        raw_text="Meri wheat crop mein kaunsi disease hai?",
        language="hi",
        intent=CanonicalIntent.DISEASE_DETECTION,
        entities=EntitySet(crop="Wheat"),
        required_capabilities=[CapabilityType.DISEASE_DETECTION, CapabilityType.RAG_KNOWLEDGE],
        required_input=RequiredInput.LEAF_IMAGE,
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(sf)
    assert plan.action_type == ActionType.NAVIGATE
    assert plan.navigation_destination == "DISEASE_SCAN"


def test_golden_example_3_disease_with_photo_and_weather():
    """
    Example 3: 'Meri wheat crop mein disease hai aur kal heavy rain hai, kya karu?'
    When photo is provided: DISEASE_DETECTION + WEATHER run in parallel, followed by RAG.
    """
    sf = make_frame(
        raw_text="Meri wheat crop mein disease hai aur kal heavy rain hai, kya karu?",
        language="hi",
        intent=CanonicalIntent.DISEASE_DETECTION,
        entities=EntitySet(crop="Wheat", timeframe="tomorrow"),
        required_capabilities=[CapabilityType.DISEASE_DETECTION, CapabilityType.WEATHER, CapabilityType.RAG_KNOWLEDGE],
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(
        sf,
        farmer_context={"latitude": 26.9124, "longitude": 75.7873},
        image_bytes=b"fake_leaf_image_bytes"
    )
    assert plan.action_type == ActionType.EXECUTE_TOOL
    assert len(plan.tasks) == 3
    rag_task = plan.get_task("rag_1")
    assert rag_task is not None
    assert "disease_1" in rag_task.depends_on
    # Stage 0: disease_1 and weather_1 run concurrently
    assert set(plan.execution_batches[0]) == {"disease_1", "weather_1"}
    # Stage 1: rag_1 runs after disease diagnosis
    assert plan.execution_batches[1] == ["rag_1"]


def test_golden_example_4_compound_mandi_decision():
    """
    Example 4: 'Gehu Jaipur mein bechu ya Kalapipal aur agle 7 din ka bhav kya rahega?'
    Plan: CURRENT_PRICE + MANDI_COMPARISON + MANDI_FORECAST in parallel, followed by MANDI_DECISION.
    """
    sf = make_frame(
        raw_text="Gehu Jaipur mein bechu ya Kalapipal aur agle 7 din ka bhav kya rahega?",
        language="hi",
        intent=CanonicalIntent.MANDI_DECISION,
        entities=EntitySet(crop="Wheat", markets=["Jaipur", "Kalapipal"], forecast_days=7),
        required_capabilities=[
            CapabilityType.CURRENT_PRICE,
            CapabilityType.MANDI_COMPARISON,
            CapabilityType.MANDI_FORECAST,
            CapabilityType.MANDI_DECISION,
        ],
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(sf)
    assert plan.action_type == ActionType.EXECUTE_TOOL
    assert len(plan.tasks) == 4
    # Check parallel Stage 0: price, compare, forecast
    assert set(plan.execution_batches[0]) == {"mandi_price_1", "mandi_compare_1", "mandi_forecast_1"}
    # Check dependent Stage 1: decision
    assert plan.execution_batches[1] == ["mandi_decision_1"]


def test_golden_example_5_disaster_risk_and_rag():
    """
    Example 5: 'Flood ka risk hai aur kya karna chahiye?'
    Plan: WEATHER -> DISASTER_RISK -> RAG_KNOWLEDGE.
    """
    sf = make_frame(
        raw_text="Flood ka risk hai aur kya karna chahiye?",
        language="hi",
        intent=CanonicalIntent.DISASTER_RISK,
        entities=EntitySet(),
        required_capabilities=[CapabilityType.WEATHER, CapabilityType.DISASTER_RISK, CapabilityType.RAG_KNOWLEDGE],
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(sf, farmer_context={"latitude": 26.9124, "longitude": 75.7873})
    assert plan.action_type == ActionType.EXECUTE_TOOL
    assert len(plan.tasks) == 3
    disaster_task = plan.get_task("disaster_1")
    rag_task = plan.get_task("rag_1")
    assert "weather_1" in disaster_task.depends_on
    assert "disaster_1" in rag_task.depends_on
    assert plan.execution_batches == [["weather_1"], ["disaster_1"], ["rag_1"]]


# =============================================================================
# 4. 50 Multilingual Planner Test Cases (All 12 Indian Languages & Dialects)
# =============================================================================

MULTILINGUAL_PLANNER_CASES = [
    # Hindi
    ("hi_1", "hi", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "आज बारिश होगी?", {"crop": None, "market": None}),
    ("hi_2", "hi", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "जयपुर में गेहूं का भाव क्या है?", {"crop": "Wheat", "market": "Jaipur"}),
    ("hi_3", "hi", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "क्या मुझे गेहूं में पानी देना चाहिए?", {"crop": "Wheat", "market": None}),
    ("hi_4", "hi", CanonicalIntent.CROP_RECOMMENDATION, [CapabilityType.CROP_RECOMMENDATION], "रेतीली मिट्टी में कौन सी फसल लगाएं?", {"crop": None, "soil_type": "Sandy Soil"}),
    ("hi_5", "hi", CanonicalIntent.MANDI_FORECAST, [CapabilityType.MANDI_FORECAST], "कोटा में सरसों का 7 दिन का भाव बताओ", {"crop": "Mustard", "market": "Kota", "forecast_days": 7}),
    
    # English
    ("en_1", "en", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "What is the weather today in Udaipur?", {"crop": None, "market": "Udaipur"}),
    ("en_2", "en", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "Current price of Soybean in Indore", {"crop": "Soybean", "market": "Indore"}),
    ("en_3", "en", CanonicalIntent.MANDI_DECISION, [CapabilityType.CURRENT_PRICE, CapabilityType.MANDI_FORECAST, CapabilityType.MANDI_DECISION], "Should I sell my wheat now or hold?", {"crop": "Wheat", "market": "Jaipur"}),
    ("en_4", "en", CanonicalIntent.GOVERNMENT_SCHEME, [CapabilityType.GOVERNMENT_SCHEME], "Information about PM Kisan scheme", {"crop": None, "market": None}),
    ("en_5", "en", CanonicalIntent.DISASTER_RISK, [CapabilityType.WEATHER, CapabilityType.DISASTER_RISK], "Is there any flood alert for my farm?", {"crop": None, "market": None}),

    # Hinglish
    ("hng_1", "hi", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "Kal rain hone wali hai, kya wheat ko water karun?", {"crop": "Wheat", "timeframe": "tomorrow"}),
    ("hng_2", "hi", CanonicalIntent.MANDI_COMPARISON, [CapabilityType.MANDI_COMPARISON], "Wheat ka rate Jaipur better hai ya Kota?", {"crop": "Wheat", "markets": ["Jaipur", "Kota"]}),
    ("hng_3", "hi", CanonicalIntent.MANDI_FORECAST, [CapabilityType.MANDI_FORECAST], "Next week mustard prices rise honge kya?", {"crop": "Mustard", "market": "Kota", "forecast_days": 7}),
    ("hng_4", "hi", CanonicalIntent.ANIMAL_ALERT, [CapabilityType.ANIMAL_DETECTION], "Khet me animal intrusion alert aaya hai kya?", {"crop": None}),
    ("hng_5", "hi", CanonicalIntent.NAVIGATION_REQUEST, [CapabilityType.NAVIGATION], "Disease scan camera open karo", {"destination": "crop_disease"}),

    # Gujarati
    ("gu_1", "gu", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "આજે અમદાવાદમાં વરસાદ પડશે?", {"market": "Ahmedabad"}),
    ("gu_2", "gu", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "રાજકોટમાં કપાસનો શું ભાવ છે?", {"crop": "Cotton", "market": "Rajkot"}),
    ("gu_3", "gu", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "કપાસના પાકમાં પાણી ક્યારે આપવું?", {"crop": "Cotton"}),
    ("gu_4", "gu", CanonicalIntent.CROP_RECOMMENDATION, [CapabilityType.CROP_RECOMMENDATION], "કાળી જમીન માટે કયો પાક સારો?", {"soil_type": "Black Soil"}),
    ("gu_5", "gu", CanonicalIntent.DISASTER_RISK, [CapabilityType.WEATHER, CapabilityType.DISASTER_RISK], "વાવાઝોડાનું જોખમ છે?", {"crop": None}),

    # Marathi
    ("mr_1", "mr", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "पुण्यात आज हवामान कसे राहील?", {"market": "Pune"}),
    ("mr_2", "mr", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "पुण्यात कांद्याचा आजचा भाव काय आहे?", {"crop": "Onion", "market": "Pune"}),
    ("mr_3", "mr", CanonicalIntent.MANDI_COMPARISON, [CapabilityType.MANDI_COMPARISON], "कांदा नाशिकमध्ये विकू की पुण्यात?", {"crop": "Onion", "markets": ["Nashik", "Pune"]}),
    ("mr_4", "mr", CanonicalIntent.MANDI_FORECAST, [CapabilityType.MANDI_FORECAST], "पुढील आठवड्यात कांद्याचे भाव वाढतील का?", {"crop": "Onion", "market": "Nashik", "forecast_days": 7}),
    ("mr_5", "mr", CanonicalIntent.DISASTER_RISK, [CapabilityType.WEATHER, CapabilityType.DISASTER_RISK], "दुष्काळाचा धोका आहे का?", {"crop": None}),

    # Punjabi
    ("pa_1", "pa", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "ਕੱਲ੍ਹ ਲੁਧਿਆਣੇ ਵਿੱਚ ਮੌਸਮ ਕਿਵੇਂ ਰਹੇਗਾ?", {"market": "Ludhiana"}),
    ("pa_2", "pa", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "ਲੁਧਿਆਣਾ ਮੰਡੀ ਵਿੱਚ ਝੋਨੇ ਦਾ ਭਾਅ ਕੀ ਹੈ?", {"crop": "Paddy", "market": "Ludhiana"}),
    ("pa_3", "pa", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "ਕਣਕ ਨੂੰ ਪਾਣੀ ਕਦੋਂ ਲਾਈਏ?", {"crop": "Wheat"}),
    ("pa_4", "pa", CanonicalIntent.CROP_RECOMMENDATION, [CapabilityType.CROP_RECOMMENDATION], "ਇਸ ਮੌਸਮ ਵਿੱਚ ਕਿਹੜੀ ਫਸਲ ਲਾਈਏ?", {"crop": None}),
    ("pa_5", "pa", CanonicalIntent.DISASTER_RISK, [CapabilityType.WEATHER, CapabilityType.DISASTER_RISK], "ਕੀ ਹੜ੍ਹ ਦਾ ਖ਼ਤਰਾ ਹੈ?", {"crop": None}),

    # Bengali
    ("bn_1", "bn", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "আজ কলকাতায় বৃষ্টি হবে কি?", {"market": "Kolkata"}),
    ("bn_2", "bn", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "কলকাতায় ধানের দর কত?", {"crop": "Paddy", "market": "Kolkata"}),
    ("bn_3", "bn", CanonicalIntent.GOVERNMENT_SCHEME, [CapabilityType.GOVERNMENT_SCHEME], "কৃষক বন্ধু প্রকল্প সম্পর্কে বলুন", {"crop": None}),
    ("bn_4", "bn", CanonicalIntent.DISASTER_RISK, [CapabilityType.WEATHER, CapabilityType.DISASTER_RISK], "ঘূর্ণিঝড়ের সতর্কতা আছে কি?", {"crop": None}),
    ("bn_5", "bn", CanonicalIntent.CROP_RECOMMENDATION, [CapabilityType.CROP_RECOMMENDATION], "পলি মাটিতে কোন ফসল ভালো হয়?", {"soil_type": "Alluvial Soil"}),

    # Tamil
    ("ta_1", "ta", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "சென்னையில் இன்று மழை பெய்யுமா?", {"market": "Chennai"}),
    ("ta_2", "ta", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "பருத்தி விலை என்ன?", {"crop": "Cotton"}),
    ("ta_3", "ta", CanonicalIntent.GOVERNMENT_SCHEME, [CapabilityType.GOVERNMENT_SCHEME], "விவசாய திட்டம் பற்றி சொல்லுங்கள்", {"crop": None}),
    ("ta_4", "ta", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "பயிருக்கு தண்ணீர் பாய்ச்சலாமா?", {"crop": "Paddy"}),
    ("ta_5", "ta", CanonicalIntent.CROP_RECOMMENDATION, [CapabilityType.CROP_RECOMMENDATION], "செம்மண்ணில் என்ன பயிரிடலாம்?", {"soil_type": "Red Soil"}),

    # Telugu
    ("te_1", "te", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "హైదరాబాద్ లో ఈరోజు వర్షం పడుతుందా?", {"market": "Hyderabad"}),
    ("te_2", "te", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "వరి మద్దతు ధర ఎంత?", {"crop": "Paddy"}),
    ("te_3", "te", CanonicalIntent.GOVERNMENT_SCHEME, [CapabilityType.GOVERNMENT_SCHEME], "రైతు భరోసా పథకం వివరాలు", {"crop": None}),
    ("te_4", "te", CanonicalIntent.DISASTER_RISK, [CapabilityType.WEATHER, CapabilityType.DISASTER_RISK], "తుఫాను హెచ్చరిక ఉందా?", {"crop": None}),
    ("te_5", "te", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "పత్తి పంటకు నీరు పెట్టాలా?", {"crop": "Cotton"}),

    # Kannada
    ("kn_1", "kn", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "ಬೆಂಗಳೂರಿನಲ್ಲಿ ಇಂದು ಮಳೆ ಬರುತ್ತಾ?", {"market": "Bengaluru"}),
    ("kn_2", "kn", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "ಈರುಳ್ಳಿ ಮಾರುಕಟ್ಟೆ ದರ ಎಷ್ಟು?", {"crop": "Onion"}),
    ("kn_3", "kn", CanonicalIntent.GOVERNMENT_SCHEME, [CapabilityType.GOVERNMENT_SCHEME], "ಕೃಷಿ ಯೋಜನೆ ಮಾಹಿತಿ ನೀಡಿ", {"crop": None}),
    ("kn_4", "kn", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "ಬೆಳೆಗೆ ನೀರುಣಿಸಬೇಕೆ?", {"crop": "Paddy"}),
    ("kn_5", "kn", CanonicalIntent.CROP_RECOMMENDATION, [CapabilityType.CROP_RECOMMENDATION], "ಕಪ್ಪು ಮಣ್ಣಿಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆ ಯಾವುದು?", {"soil_type": "Black Soil"}),

    # Malayalam
    ("ml_1", "ml", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "ഇന്ന് കൊച്ചിയിൽ മഴ പെയ്യുമോ?", {"market": "Kochi"}),
    ("ml_2", "ml", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "നെല്ലിന്റെ ഇന്നത്തെ വില എത്ര?", {"crop": "Paddy"}),
    ("ml_3", "ml", CanonicalIntent.GOVERNMENT_SCHEME, [CapabilityType.GOVERNMENT_SCHEME], "സുഭിക്ഷ കേരളം പദ്ധതി വിവരങ്ങൾ", {"crop": None}),
    ("ml_4", "ml", CanonicalIntent.DISASTER_RISK, [CapabilityType.WEATHER, CapabilityType.DISASTER_RISK], "വെള്ളപ്പൊക്ക മുന്നറിയിപ്പ് ഉണ്ടോ?", {"crop": None}),
    ("ml_5", "ml", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "വാഴയ്ക്ക് നനയ്ക്കണോ?", {"crop": "Banana"}),

    # Marwari (Regional Dialect)
    ("rwr_1", "rwr", CanonicalIntent.WEATHER, [CapabilityType.WEATHER], "आज मींह बरसेला कांई?", {"market": "Jodhpur"}),
    ("rwr_2", "rwr", CanonicalIntent.MANDI_PRICE, [CapabilityType.CURRENT_PRICE], "मंडी में बाजरी रो भाव कांई चाल रह्यो है?", {"crop": "Bajra", "market": "Jodhpur"}),
    ("rwr_3", "rwr", CanonicalIntent.SMART_IRRIGATION, [CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION], "बाजरी में पाणी देणो ठीक है कांई?", {"crop": "Bajra"}),
    ("rwr_4", "rwr", CanonicalIntent.CROP_RECOMMENDATION, [CapabilityType.CROP_RECOMMENDATION], "रेतली धोरां वाली जमीन में कांई बोवां?", {"soil_type": "Sandy Soil"}),
    ("rwr_5", "rwr", CanonicalIntent.ANIMAL_ALERT, [CapabilityType.ANIMAL_DETECTION], "खेत में रोझड़ा (नीलगाय) रो सेंसर बज्यो कांई?", {"crop": None}),
]


@pytest.mark.parametrize("case_id, lang, intent, caps, text, ent_data", MULTILINGUAL_PLANNER_CASES)
def test_50_multilingual_planner_cases(case_id, lang, intent, caps, text, ent_data):
    """
    Step 16 Requirement: Test at least 50 planner cases across 12 Indian languages & dialects.
    Verifies valid plan construction, dependency ordering, and zero tool name hallucination.
    """
    entities = EntitySet(
        crop=ent_data.get("crop"),
        market=ent_data.get("market"),
        markets=ent_data.get("markets") or ([ent_data.get("market")] if ent_data.get("market") else []),
        forecast_days=ent_data.get("forecast_days"),
        timeframe=ent_data.get("timeframe"),
        soil_values={"soil_type": ent_data.get("soil_type")} if ent_data.get("soil_type") else None,
        additional_entities={"destination": ent_data.get("destination")} if ent_data.get("destination") else {},
    )
    sf = make_frame(
        raw_text=text,
        language=lang,
        intent=intent,
        entities=entities,
        required_capabilities=caps,
        confidence=make_conf(0.95),
    )
    farmer_ctx = {
        "latitude": 26.9124,
        "longitude": 75.7873,
        "district": "Jaipur",
        "state": "Rajasthan",
        "soil_type": ent_data.get("soil_type") or "Sandy Soil",
    }
    plan = generate_task_plan(sf, farmer_context=farmer_ctx)
    assert plan.status == PlanStatus.READY

    if plan.action_type == ActionType.NAVIGATE:
        assert plan.navigation_destination is not None
        assert plan.navigation_route is not None
    else:
        assert len(plan.tasks) > 0
        assert len(plan.execution_batches) > 0
        # Verify all tools in plan exist in executable ToolRegistry
        for t in plan.tasks:
            assert tool_registry.get_tool(t.tool_name) is not None, f"Tool '{t.tool_name}' not in registry"


# =============================================================================
# 5. Real Tool Execution Traces (Step 17)
# =============================================================================

@pytest.mark.asyncio
async def test_real_execution_weather_and_irrigation():
    """
    Verify real execution of Weather + Smart Irrigation:
    Weather executes first, then Smart Irrigation executes.
    """
    sf = make_frame(
        raw_text="Will it rain tomorrow and should I irrigate wheat?",
        language="en",
        intent=CanonicalIntent.IRRIGATION_ADVISORY,
        entities=EntitySet(crop="Wheat", timeframe="tomorrow"),
        required_capabilities=[CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION],
        confidence=make_conf(0.95),
    )
    farmer_ctx = {"latitude": 26.9124, "longitude": 75.7873, "district": "Jaipur"}
    plan = generate_task_plan(sf, farmer_context=farmer_ctx)
    assert len(plan.execution_batches) == 2

    # Execute plan through controlled executor
    executed_plan = await execute_task_plan(plan, context=farmer_ctx)
    assert executed_plan.status == PlanStatus.COMPLETED
    w_task = executed_plan.get_task("weather_1")
    i_task = executed_plan.get_task("irrigation_1")
    assert w_task.status == TaskStatus.COMPLETED
    assert i_task.status == TaskStatus.COMPLETED
    assert w_task.output is not None
    assert i_task.output is not None
    assert "temperature_c" in w_task.output or "current_weather" in w_task.output
    assert "status" in i_task.output


@pytest.mark.asyncio
async def test_real_execution_mandi_suite():
    """
    Verify real execution of Mandi Suite:
    Price + Forecast execute in parallel (Stage 0), Decision executes in Stage 1.
    """
    sf = make_frame(
        raw_text="Gehu ka rate batao aur agle 7 din ka forecast kya hai Kalapipal me?",
        language="hi",
        intent=CanonicalIntent.MANDI_DECISION,
        entities=EntitySet(crop="Wheat", market="Kalapipal", forecast_days=7),
        required_capabilities=[CapabilityType.CURRENT_PRICE, CapabilityType.MANDI_FORECAST, CapabilityType.MANDI_DECISION],
        confidence=make_conf(0.95),
    )
    plan = generate_task_plan(sf, farmer_context={"state": "Madhya Pradesh", "district": "Shajapur"})
    assert len(plan.execution_batches) == 2

    executed_plan = await execute_task_plan(plan, context={"state": "Madhya Pradesh", "district": "Shajapur"})
    assert executed_plan.status == PlanStatus.COMPLETED
    price_t = executed_plan.get_task("mandi_price_1")
    forecast_t = executed_plan.get_task("mandi_forecast_1")
    decision_t = executed_plan.get_task("mandi_decision_1")
    assert price_t.status == TaskStatus.COMPLETED
    assert forecast_t.status == TaskStatus.COMPLETED
    assert decision_t.status == TaskStatus.COMPLETED
    assert "current_price" in price_t.output
    assert "daily_forecasts" in forecast_t.output


@pytest.mark.asyncio
async def test_real_execution_disaster_risk():
    """Verify real execution of Weather -> Disaster Risk ensemble pipeline."""
    sf = make_frame(
        raw_text="Disaster risk alert for Jaipur",
        language="en",
        intent=CanonicalIntent.DISASTER_RISK,
        entities=EntitySet(market="Jaipur", forecast_days=7),
        required_capabilities=[CapabilityType.WEATHER, CapabilityType.DISASTER_RISK],
        confidence=make_conf(0.95),
    )
    farmer_ctx = {"latitude": 26.9124, "longitude": 75.7873, "district": "Jaipur"}
    plan = generate_task_plan(sf, farmer_context=farmer_ctx)
    executed_plan = await execute_task_plan(plan, context=farmer_ctx)
    assert executed_plan.status == PlanStatus.COMPLETED
    disaster_t = executed_plan.get_task("disaster_1")
    assert disaster_t.status == TaskStatus.COMPLETED
    assert "current_disaster_type" in disaster_t.output or "daily_timeline" in disaster_t.output or "summary" in disaster_t.output


# =============================================================================
# 6. Failure Handling (Blocking vs Non-Blocking)
# =============================================================================

@pytest.mark.asyncio
async def test_blocking_failure_halts_dependent_tasks():
    """
    Step 11 Requirement: When a blocking prerequisite fails,
    dependent downstream tasks must be SKIPPED/BLOCKED rather than executing on corrupt data.
    """
    # Create a plan with a failing weather task (e.g. invalid latitude)
    plan = TaskPlan(
        objective="Test blocking failure behavior",
        action_type=ActionType.EXECUTE_TOOL,
        tasks=[
            PlannedTask(
                task_id="bad_weather",
                capability=CapabilityType.WEATHER,
                tool_name="weather_tool",
                depends_on=[],
                static_inputs={"latitude": 999.0, "longitude": 999.0}, # Invalid coordinates
                is_blocking=True,
            ),
            PlannedTask(
                task_id="dependent_irrigation",
                capability=CapabilityType.SMART_IRRIGATION,
                tool_name="smart_irrigation_tool",
                depends_on=["bad_weather"],
                static_inputs={"crop": "Wheat"},
                is_blocking=True,
            ),
        ],
        execution_batches=[["bad_weather"], ["dependent_irrigation"]],
    )
    executed = await execute_task_plan(plan)
    assert executed.status in [PlanStatus.FAILED, PlanStatus.PARTIAL_SUCCESS]
    bad_t = executed.get_task("bad_weather")
    dep_t = executed.get_task("dependent_irrigation")
    assert bad_t.status == TaskStatus.FAILED
    assert dep_t.status == TaskStatus.SKIPPED
    assert "upstream blocking failure" in dep_t.error or "Prerequisite dependency failed" in dep_t.error


# =============================================================================
# 7. Full LangGraph Pipeline Orchestration Integration
# =============================================================================

@pytest.mark.asyncio
async def test_langgraph_pipeline_with_planner_and_executor():
    """
    Step 9 Requirement: Verify LangGraph StateGraph executes:
    START -> intent_classification -> planner -> plan_executor -> response_synthesizer -> END.
    """
    res = await run_orchestrator_pipeline(
        user_input="जयपुर में गेहूं का भाव क्या है?",
        detected_language="hi",
        session_id="session_f5_test_01",
        farmer_context={"state": "Rajasthan", "district": "Jaipur"}
    )
    # Check that task_plan was populated
    assert res.get("task_plan") is not None
    plan_dict = res["task_plan"]
    assert plan_dict["status"] in ["COMPLETED", "READY"]
    # Check completed tasks
    assert len(res.get("completed_tasks", [])) > 0
    # Check tool output and synthesis
    assert res.get("tool_status") == "success"
    assert len(res.get("final_response", "")) > 5
    assert "गेहूं" in res["final_response"] or "Wheat" in res["final_response"] or "भाव" in res["final_response"]
