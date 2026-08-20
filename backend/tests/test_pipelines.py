"""
Integration and unit tests for FarmFusion tools, workflows, and orchestrator.
"""
import pytest
from app.workflows.disease_workflow import run_disease_detection_workflow, DiseaseDetectionInput
from app.workflows.crop_recommendation import run_crop_recommendation_workflow, CropRecommendationInput
from app.workflows.market_forecasting import run_mandi_forecasting_pipeline, MandiForecastRequest
from app.orchestrator.graph import run_orchestrator_pipeline


@pytest.mark.asyncio
async def test_disease_workflow_confidence_tier():
    input_data = DiseaseDetectionInput(image_bytes=b"dummy_leaf_bytes", crop_name="Wheat", language="en")
    res = await run_disease_detection_workflow(input_data)
    assert res.confidence_tier in ["high", "medium", "low", "unclear"]
    assert res.disease_name is not None
    assert len(res.treatment_steps) > 0


@pytest.mark.asyncio
async def test_crop_recommendation_workflow():
    input_data = CropRecommendationInput(
        nitrogen=40.0, phosphorus=25.0, potassium=30.0, ph=6.5,
        temperature_c=25.0, humidity_pct=50.0, rainfall_mm=45.0, language="hi"
    )
    res = await run_crop_recommendation_workflow(input_data)
    assert res.top_recommendation is not None
    assert res.confidence > 0.0
    assert len(res.alternative_crops) > 0


@pytest.mark.asyncio
async def test_mandi_forecasting_pipeline():
    req = MandiForecastRequest(commodity="Wheat", mandi="Jaipur Mandi", days=5)
    res = await run_mandi_forecasting_pipeline(req)
    assert res.commodity == "Wheat"
    assert len(res.daily_forecasts) == 5
    assert res.disclaimer is not None


@pytest.mark.asyncio
async def test_orchestrator_weather_query():
    res = await run_orchestrator_pipeline(user_input="आज मौसम कैसा है", detected_language="hi")
    assert res["intent"] == "weather"
    assert res["final_response"] is not None
    assert not res["requires_clarification"]


@pytest.mark.asyncio
async def test_orchestrator_low_confidence_clarification():
    # Ambiguous input should trigger safety rule #6 clarification
    res = await run_orchestrator_pipeline(user_input="xyz123abc", detected_language="hi")
    assert res["intent"] == "clarify"
    assert res["requires_clarification"] is True
