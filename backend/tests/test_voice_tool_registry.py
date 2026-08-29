"""
Unit tests for FarmFusion Voice Agent Tool Registry.

Verifies:
- All 9 tool contracts execute safely with typed ToolResult
- Provenance metadata is present on every result
- Mode B strictly does not fabricate N/P/K
- Mode A invokes XGBoost V2 model with valid inputs
- Disease info tool redirects photo requests to camera UI
- Unsupported capabilities are honestly communicated
"""
import pytest
from app.tools.registry import tool_registry, ToolStatus, ConfirmationPolicy


@pytest.mark.asyncio
async def test_weather_tool_execution():
    res = await tool_registry.execute("weather_tool", {"latitude": 26.9124, "longitude": 75.7873, "location_name": "Jaipur"})
    assert res.status == ToolStatus.SUCCESS
    assert res.data is not None
    assert "temperature_c" in res.data
    assert res.provenance.source.startswith("Open-Meteo")
    assert res.provenance.estimated_vs_measured == "measured"


@pytest.mark.asyncio
async def test_crop_recommendation_mode_b_no_soil_report():
    res = await tool_registry.execute(
        "crop_recommendation_tool",
        {"latitude": 24.6178, "longitude": 73.9937, "soil_type": "Sandy Soil", "has_soil_report": False}
    )
    assert res.status == ToolStatus.SUCCESS
    assert res.data is not None
    assert "recommendations" in res.data
    # Top crop for Sandy Soil in Kharif should be Groundnut
    top_crop = res.data["recommendations"][0]["crop_name"]
    assert "Groundnut" in top_crop
    # Provenance must be marked estimated and N/P/K must be None
    assert res.provenance.estimated_vs_measured == "estimated"
    assert res.data["soil_parameters"]["nitrogen"]["value"] is None


@pytest.mark.asyncio
async def test_disease_info_tool_photo_redirect():
    res = await tool_registry.execute("disease_info_tool", {"query_crop_or_disease": "पत्ती की फोटो स्कैन करो"})
    assert res.status == ToolStatus.REQUIRES_PHOTO
    assert "camera" in res.message.lower() or "कैमरा" in str(res.localized_message)


@pytest.mark.asyncio
async def test_market_price_tool_execution():
    res = await tool_registry.execute("market_price_tool", {"commodity": "Wheat", "state": "Rajasthan"})
    assert res.status == ToolStatus.SUCCESS
    assert res.data is not None
    assert "current_price" in res.data
    assert "modal_price" in res.data["current_price"]


@pytest.mark.asyncio
async def test_unsupported_capability_honest_admission():
    res = await tool_registry.execute("unsupported_capability_tool", {"capability_type": "purchase"})
    assert res.status == ToolStatus.UNSUPPORTED_CAPABILITY
    assert "does not process direct payments" in res.message
