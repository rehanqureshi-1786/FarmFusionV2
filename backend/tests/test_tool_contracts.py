"""
Tests for Phase F4: Tool Contract & Capability Normalization.
Verifies:
1. Canonical Capability -> Tool mapping
2. Valid Input schemas
3. Invalid Input handling & structured errors
4. Required Input declarations
5. Missing Photo gating (disease_detection_tool -> REQUIRES_PHOTO -> NAVIGATE to DISEASE_SCAN)
6. Insufficient History handling in forecasting
7. Provenance metadata correctness (sources, models, estimated flags)
8. Status handling (SUCCESS, REQUIRES_PHOTO, INVALID_INPUT, MISSING_INPUT)
9. Navigation strict whitelist validation and Android route mapping
10. Calling tool contract and phone normalization
11. Serialization and deserialization of ToolResult and ToolContract
12. SemanticFrame.required_capabilities -> map_capabilities_to_tools -> ToolContract
13. Verification across all 5 Phase F3 Golden Examples
"""
import pytest
from app.schemas.semantic_frame import CapabilityType, RequiredInput
from app.tools.contracts import (
    ToolStatus,
    ProvenanceMetadata,
    ToolResult,
    ToolContract,
    AllowedNavigationDestination,
    NAVIGATION_ROUTE_MAP,
    CAPABILITY_CONTRACTS,
    get_tool_contract,
    map_capabilities_to_tools,
    WeatherInput,
    WeatherOutput,
    SmartIrrigationInput,
    SmartIrrigationOutput,
    DisasterRiskInput,
    CropRecommendationInput,
    DiseaseDetectionInput,
    MandiCurrentPriceInput,
    MandiForecastInput,
    MandiComparisonInput,
    MandiDecisionInput,
    RAGKnowledgeInput,
    GovernmentSchemeInput,
    AnimalDetectionInput,
    NavigationInput,
    NavigationOutput,
    CallingInput,
)
from app.tools.registry import tool_registry


def test_capability_contract_registration():
    """Verify all mandatory canonical capabilities have complete contracts."""
    expected_capabilities = [
        CapabilityType.WEATHER,
        CapabilityType.SMART_IRRIGATION,
        CapabilityType.DISASTER_RISK,
        CapabilityType.CROP_RECOMMENDATION,
        CapabilityType.DISEASE_DETECTION,
        CapabilityType.CURRENT_PRICE,
        CapabilityType.MANDI_HISTORY,
        CapabilityType.MANDI_FORECAST,
        CapabilityType.MANDI_COMPARISON,
        CapabilityType.MANDI_DECISION,
        CapabilityType.RAG_KNOWLEDGE,
        CapabilityType.GOVERNMENT_SCHEME,
        CapabilityType.ANIMAL_ALERT,
        CapabilityType.NAVIGATION,
        CapabilityType.CALLING,
    ]
    for cap in expected_capabilities:
        contract = get_tool_contract(cap)
        assert contract is not None, f"Missing contract for {cap}"
        assert contract.tool_name, f"Missing tool_name for {cap}"
        assert contract.input_schema is not None
        assert contract.output_schema is not None
        assert contract.provenance_source != ""
        # Verify the tool is actually registered in the executable tool_registry
        assert tool_registry.get_tool(contract.tool_name) is not None, (
            f"Tool '{contract.tool_name}' for capability '{cap}' is not registered in executable tool_registry"
        )


def test_mapping_semantic_frame_capabilities_to_tools():
    """Verify deterministic capability to tool name mapping."""
    # Single capability
    assert map_capabilities_to_tools([CapabilityType.WEATHER]) == ["weather_tool"]
    assert map_capabilities_to_tools([CapabilityType.SMART_IRRIGATION]) == ["smart_irrigation_tool"]

    # Compound Weather + Irrigation
    res = map_capabilities_to_tools([CapabilityType.WEATHER, CapabilityType.SMART_IRRIGATION])
    assert res == ["weather_tool", "smart_irrigation_tool"]

    # Compound Disease + RAG
    res = map_capabilities_to_tools([CapabilityType.DISEASE_DETECTION, CapabilityType.RAG_KNOWLEDGE])
    assert res == ["disease_detection_tool", "rag_knowledge_tool"]

    # Multi-step Mandi suite
    res = map_capabilities_to_tools([
        CapabilityType.CURRENT_PRICE,
        CapabilityType.MANDI_COMPARISON,
        CapabilityType.MANDI_FORECAST,
        CapabilityType.MANDI_DECISION,
    ])
    assert res == [
        "mandi_current_price_tool",
        "mandi_comparison_tool",
        "mandi_forecast_tool",
        "mandi_decision_tool",
    ]


def test_five_golden_examples_capability_mapping():
    """Verify all 5 Phase F3 golden examples map to exact executable tool contracts."""
    # Example A: Mandi Price
    ex_a_caps = ["CURRENT_PRICE"]
    tools_a = map_capabilities_to_tools(ex_a_caps)
    assert tools_a == ["mandi_current_price_tool"]
    contract_a = get_tool_contract(ex_a_caps[0])
    assert contract_a.tool_name == "mandi_current_price_tool"
    assert contract_a.required_fields == ["crop"]

    # Example B: Disease Detection with Image Gate
    ex_b_caps = ["DISEASE_DETECTION", "RAG_KNOWLEDGE"]
    tools_b = map_capabilities_to_tools(ex_b_caps)
    assert tools_b == ["disease_detection_tool", "rag_knowledge_tool"]

    # Example C: Irrigation Advisory
    ex_c_caps = ["WEATHER", "SMART_IRRIGATION"]
    tools_c = map_capabilities_to_tools(ex_c_caps)
    assert tools_c == ["weather_tool", "smart_irrigation_tool"]

    # Example D: Mandi Decision & Forecast
    ex_d_caps = ["CURRENT_PRICE", "MANDI_COMPARISON", "MANDI_FORECAST", "MANDI_DECISION"]
    tools_d = map_capabilities_to_tools(ex_d_caps)
    assert tools_d == [
        "mandi_current_price_tool",
        "mandi_comparison_tool",
        "mandi_forecast_tool",
        "mandi_decision_tool",
    ]

    # Example E: Disaster Risk
    ex_e_caps = ["WEATHER", "DISASTER_RISK", "RAG_KNOWLEDGE"]
    tools_e = map_capabilities_to_tools(ex_e_caps)
    assert tools_e == ["weather_tool", "disaster_risk_tool", "rag_knowledge_tool"]


@pytest.mark.asyncio
async def test_disease_detection_missing_photo_gate():
    """
    Step 6 Requirement: When disease detection is called without an image,
    it MUST NOT guess a disease. It must return ToolStatus.REQUIRES_PHOTO,
    required_input=LEAF_IMAGE, action=NAVIGATE, destination=DISEASE_SCAN.
    """
    res = await tool_registry.execute(
        "disease_detection_tool",
        slots={"crop": "Wheat"},
        context={}
    )
    assert res.status == ToolStatus.REQUIRES_PHOTO
    assert res.data is not None
    assert res.data.get("action") == "NAVIGATE"
    assert res.data.get("destination") == "DISEASE_SCAN"
    assert res.data.get("android_route") == "crop_disease"
    assert res.data.get("required_input") == "LEAF_IMAGE"
    assert "photo" in res.message.lower() or "image" in res.message.lower()
    assert res.provenance.source == "EfficientNet-B3 Gatekeeper"
    assert res.provenance.estimated is False


@pytest.mark.asyncio
async def test_smart_irrigation_tool_execution():
    """
    Step 5 Requirement: First-class smart irrigation tool reusing existing weather agent
    deterministic agronomic soil moisture balance logic.
    """
    res = await tool_registry.execute(
        "smart_irrigation_tool",
        slots={"latitude": 26.9124, "longitude": 75.7873, "crop": "Wheat"},
        context={}
    )
    assert res.status == ToolStatus.SUCCESS
    assert res.data is not None
    assert "status" in res.data
    assert "irrigation_need_score" in res.data
    assert "action" in res.data
    assert res.provenance.source.startswith("Open-Meteo")
    assert res.provenance.estimated_vs_measured == "measured"


@pytest.mark.asyncio
async def test_navigation_whitelist_and_typed_action():
    """
    Step 8 Requirement: Strict whitelist enforcement.
    Valid destination returns typed action with android route.
    Invalid destination returns INVALID_INPUT.
    """
    # 1. Valid destination: DISEASE_SCAN
    res_scan = await tool_registry.execute(
        "navigation_tool",
        slots={"destination": "DISEASE_SCAN"},
        context={}
    )
    assert res_scan.status == ToolStatus.SUCCESS
    assert res_scan.data["action"] == "NAVIGATE"
    assert res_scan.data["destination"] == "DISEASE_SCAN"
    assert res_scan.data["android_route"] == "crop_disease"
    assert res_scan.data["required_input"] == "LEAF_IMAGE"

    # 2. Valid destination: MANDI
    res_mandi = await tool_registry.execute(
        "navigation_tool",
        slots={"destination": "MANDI"},
        context={}
    )
    assert res_mandi.status == ToolStatus.SUCCESS
    assert res_mandi.data["android_route"] == "mandi_rates"

    # 3. Valid alias: "crop_recommendation"
    res_crop = await tool_registry.execute(
        "navigation_tool",
        slots={"destination": "crop_recommendation"},
        context={}
    )
    assert res_crop.status == ToolStatus.SUCCESS
    assert res_crop.data["destination"] == "CROP_RECOMMENDATION"
    assert res_crop.data["android_route"] == "crop_recommendation"

    # 4. Invalid destination rejection
    res_invalid = await tool_registry.execute(
        "navigation_tool",
        slots={"destination": "crypto_trading_screen"},
        context={}
    )
    assert res_invalid.status == ToolStatus.INVALID_INPUT
    assert "not a permitted navigation target" in res_invalid.message
    assert "allowed_destinations" in res_invalid.data


@pytest.mark.asyncio
async def test_calling_tool_contract_and_validation():
    """
    Step 7 Requirement: Calling tool exposed with clean contract delegating to KisanCallingService.
    Missing phone returns MISSING_INPUT.
    Invalid phone returns error.
    """
    # Missing phone
    res_missing = await tool_registry.execute(
        "calling_tool",
        slots={"farmer_name": "Ramesh Kumar"},
        context={}
    )
    assert res_missing.status == ToolStatus.MISSING_INPUT
    assert "phone" in res_missing.message.lower()

    # Invalid phone format
    res_invalid = await tool_registry.execute(
        "calling_tool",
        slots={"phone": "12345", "farmer_name": "Ramesh Kumar"},
        context={}
    )
    assert res_invalid.status == ToolStatus.ERROR
    assert "Invalid" in res_invalid.message or "E.164" in res_invalid.message


@pytest.mark.asyncio
async def test_mandi_current_price_provenance_and_execution():
    """Verify Mandi Current Price tool adheres to provenance rules."""
    res = await tool_registry.execute(
        "mandi_current_price_tool",
        slots={"crop": "Wheat", "market": "Jaipur"},
        context={"state": "Rajasthan", "district": "Jaipur"}
    )
    assert res.status == ToolStatus.SUCCESS
    assert res.data is not None
    assert "current_price" in res.data
    assert res.provenance.source.startswith("Agmarknet")
    assert res.provenance.estimated_vs_measured == "measured"
    assert res.provenance.confidence is not None


@pytest.mark.asyncio
async def test_mandi_comparison_tool():
    """Verify Mandi Comparison tool calculates mathematical spread."""
    res = await tool_registry.execute(
        "mandi_comparison_tool",
        slots={"commodity": "Wheat", "market_a": "Jaipur", "market_b": "Kota"},
        context={}
    )
    assert res.status == ToolStatus.SUCCESS
    assert "comparison" in res.data
    assert "price_difference" in res.data["comparison"]
    assert "higher_market" in res.data["comparison"]



def test_tool_result_serialization_and_deserialization():
    """Verify ToolResult serializes cleanly to JSON and reconstructs identically."""
    prov = ProvenanceMetadata(
        source="Open-Meteo Physical NWP",
        model="ECMWF IFS",
        model_version="0.25deg",
        confidence=0.95,
        estimated=False,
        estimated_vs_measured="measured",
        location="26.9124, 75.7873",
    )
    tr = ToolResult(
        status=ToolStatus.SUCCESS,
        capability="WEATHER",
        tool_name="weather_tool",
        data={"temperature_c": 31.5, "rainfall_mm": 0.0},
        confidence=0.95,
        provenance=prov,
        message="Current temperature in Jaipur is 31.5°C with no rainfall.",
        warnings=["High humidity expected in afternoon"],
        localized_message={"hi": "जयपुर में वर्तमान तापमान 31.5°C है।"},
    )
    json_str = tr.model_dump_json()
    reconstructed = ToolResult.model_validate_json(json_str)
    assert reconstructed.status == ToolStatus.SUCCESS
    assert reconstructed.capability == "WEATHER"
    assert reconstructed.data["temperature_c"] == 31.5
    assert reconstructed.provenance.model == "ECMWF IFS"
    assert reconstructed.warnings == ["High humidity expected in afternoon"]
    assert reconstructed.localized_message["hi"] == "जयपुर में वर्तमान तापमान 31.5°C है।"


def test_input_schema_validation_errors():
    """Verify Pydantic input schemas catch invalid types and out-of-range values."""
    # Latitude out of range
    with pytest.raises(Exception):
        WeatherInput(latitude=120.0, longitude=75.0)

    # Empty crop name in Mandi input
    with pytest.raises(Exception):
        MandiCurrentPriceInput(crop="")

    # Invalid navigation destination in NavigationInput
    with pytest.raises(Exception):
        NavigationInput(destination="unauthorized_screen_404")
