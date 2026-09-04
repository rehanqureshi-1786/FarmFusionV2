"""
Tests for 7-Day Disaster Risk Prediction Tool, Intent Classification,
Tool Registry Integration, and Multilingual Synthesis.
"""
import pytest
from unittest.mock import patch, AsyncMock

from app.tools.disaster_risk_tool import disaster_risk_tool, DisasterRiskInput
from app.tools.registry import tool_registry, ToolStatus
from app.orchestrator.nodes.intent_classification import intent_classification_node
from app.orchestrator.nodes.tool_router import tool_router_node
from app.orchestrator.nodes.synthesizer import response_synthesizer_node


MOCK_FORECAST = {
    "success": True,
    "location": "Jaipur",
    "forecast": [
        {
            "date": f"2026-09-0{i+1}",
            "temperature_c": 32.0,
            "temperature_max_c": 36.0,
            "temperature_min_c": 26.0,
            "precipitation_mm": 2.0 if i < 3 else 0.0,
            "wind_speed_kmh": 15.0,
            "condition": "Partly Cloudy",
        }
        for i in range(7)
    ],
}
MOCK_CURRENT = {
    "success": True,
    "temperature_c": 31.0,
    "humidity_percent": 55.0,
    "pressure_hpa": 1010.0,
}


@pytest.mark.asyncio
async def test_disaster_risk_tool_7day_execution():
    """Verify disaster_risk_tool runs inference across a 7-day horizon with physical weather data."""
    with patch("app.services.weather_service.WeatherService.get_forecast", new=AsyncMock(return_value=MOCK_FORECAST)), \
         patch("app.services.weather_service.WeatherService.get_current_weather", new=AsyncMock(return_value=MOCK_CURRENT)):
        input_data = DisasterRiskInput(
            latitude=26.9124,
            longitude=75.7873,
            location_name="Jaipur",
            crop_name="Wheat",
            days=7
        )
        result = await disaster_risk_tool(input_data)

        assert result.error is None
        assert result.location == "Jaipur"
        assert result.forecast_days >= 1
        assert result.current_disaster_type in ["Low Risk", "Flood Risk", "Cyclone Risk", "Drought Risk"]
        assert result.peak_disaster_type in ["Low Risk", "Flood Risk", "Cyclone Risk", "Drought Risk"]
        assert result.peak_risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert 0.0 <= result.peak_risk_score <= 100.0
        assert len(result.daily_timeline) == result.forecast_days

        day1 = result.daily_timeline[0]
        assert day1.temperature_c is not None
        assert day1.rainfall_mm is not None
        assert day1.wind_speed_kmh is not None
        assert 0.0 <= day1.probability <= 1.0
        assert isinstance(day1.recommendations, list)


@pytest.mark.asyncio
async def test_disaster_intent_classification_multilingual():
    """Verify Hindi, English, and regional disaster hazard queries trigger disaster_risk intent."""
    test_cases = [
        ("जयपुर में अगले 7 दिन बाढ़ या तूफान का कोई खतरा है क्या?", "disaster_risk", 7, "Jaipur"),
        ("क्या अगले हफ्ते सूखा या तेज आंधी का खतरा रहेगा?", "disaster_risk", 7, None),
        ("Is there any flood or cyclone risk in Jaipur next week?", "disaster_risk", 7, "Jaipur"),
        ("શું આગામી 7 દિવસમાં પૂર કે વાવાઝોડું આવશે?", "disaster_risk", 7, None),
        ("पुढील 7 दिवसांत पुराचा धोका आहे का?", "disaster_risk", 7, None),
    ]

    for query, expected_intent, expected_days, expected_loc in test_cases:
        state = {
            "user_input": query,
            "detected_language": "hi",
            "filled_slots": {},
            "session_id": "test_session",
        }
        res_state = await intent_classification_node(state)
        assert res_state["intent"] == expected_intent, f"Failed on query: {query}"
        assert res_state["filled_slots"].get("days") == expected_days
        if expected_loc:
            assert res_state["filled_slots"].get("location_name") == expected_loc


@pytest.mark.asyncio
async def test_tool_registry_disaster_risk_execution():
    """Verify tool_registry executes disaster_risk_tool with proper provenance."""
    with patch("app.services.weather_service.WeatherService.get_forecast", new=AsyncMock(return_value=MOCK_FORECAST)), \
         patch("app.services.weather_service.WeatherService.get_current_weather", new=AsyncMock(return_value=MOCK_CURRENT)):
        slots = {"latitude": 26.9124, "longitude": 75.7873, "location_name": "Jaipur", "days": 7}
        context = {}

        tool_res = await tool_registry.execute("disaster_risk_tool", slots, context)
        assert tool_res.status == ToolStatus.SUCCESS
        assert tool_res.data is not None
        assert "DisasterPredictorAI" in tool_res.provenance.source
        assert tool_res.data["forecast_days"] >= 1
        assert "summary" in tool_res.data


@pytest.mark.asyncio
async def test_orchestrator_end_to_end_disaster_flow():
    """Verify complete LangGraph orchestrator flow from intent to tool to synthesis."""
    state = {
        "user_input": "जयपुर में अगले 7 दिन आंधी तूफान या भारी बारिश का खतरा बताओ",
        "detected_language": "hi",
        "detected_dialect": None,
        "filled_slots": {},
        "missing_slots": [],
        "session_id": "test_flow_session",
    }

    # 1. Intent node
    state = await intent_classification_node(state)
    assert state["intent"] == "disaster_risk"

    # 2. Tool router node
    state = await tool_router_node(state)
    assert state["last_tool"] == "disaster_risk_tool"
    assert state["last_disaster_result"] is not None
    assert state["tool_status"] == "success"

    # 3. Synthesizer node (Hindi)
    state = await response_synthesizer_node(state)
    response = state.get("last_final_response", "")
    assert len(response) > 0
    assert "जयपुर" in response or "दिनों" in response

    # 4. Synthesizer node (Marwari dialect)
    state["detected_dialect"] = "rwr"
    state["response_dialect"] = "rwr"
    state = await response_synthesizer_node(state)
    response_rwr = state.get("last_final_response", "")
    assert ("किसान भाई" in response_rwr or "रैवेला" in response_rwr)
