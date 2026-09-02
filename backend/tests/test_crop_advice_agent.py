import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.orchestrator.graph import run_orchestrator_pipeline


@pytest.mark.asyncio
async def test_api_v1_crop_recommend_endpoint():
    """Test that POST /api/v1/crop/recommend works seamlessly with Android request structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test basic request
        payload = {
            "location": "Jaipur, Rajasthan",
            "soil_type": "Sandy Soil",
            "rainfall_mm": 450.0,
            "temperature_c": 28.0,
            "farm_size_acres": 2.5,
            "preferred_language": "hi",
            "latitude": 26.9124,
            "longitude": 75.7873
        }
        response = await client.post("/api/v1/crop/recommend", json=payload)
        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert len(data["recommendations"]) > 0
        assert "crop_name" in data["recommendations"][0]
        assert "confidence_score" in data["recommendations"][0]

        # 2. Test request with verified soil test nutrients (Mode A)
        payload_with_soil = {
            "location": "Udaipur, Rajasthan",
            "soil_type": "loamy",
            "rainfall_mm": -1.0,
            "temperature_c": 26.0,
            "farm_size_acres": 1.5,
            "preferred_language": "en",
            "nitrogen": 90.0,
            "phosphorus": 45.0,
            "potassium": 50.0,
            "ph": 6.8
        }
        response_soil = await client.post("/api/v1/crop/recommend", json=payload_with_soil)
        assert response_soil.status_code == 200
        data_soil = response_soil.json()
        assert data_soil["success"] is True
        assert len(data_soil["recommendations"]) > 0


@pytest.mark.asyncio
async def test_api_v1_crop_test_endpoint():
    """Test GET /api/v1/crop/test endpoint used by Android connection check."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/crop/test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Crop API is working!" in data["message"]


@pytest.mark.asyncio
async def test_api_v1_diagnostics_crop_agent():
    """Test GET /api/v1/diagnostics/crop-agent."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/diagnostics/crop-agent")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["test_recommendation_count"] > 0


@pytest.mark.asyncio
async def test_crop_advice_orchestrator_intents():
    """Test that all phrasing of 'crop advice' and 'crop recommendation' are recognized by the orchestrator."""
    test_queries = [
        ("crop advice", "crop_recommendation"),
        ("crop recommendation", "crop_recommendation"),
        ("give me crop advice", "crop_recommendation"),
        ("best crop suggestions for my field", "crop_recommendation"),
        ("फसल सलाह दो", "crop_recommendation"),
        ("खेत में क्या बोएं सलाह दो", "crop_recommendation"),
        ("which crop should I grow in sandy soil", "crop_recommendation"),
        ("crop prediction for this season", "crop_recommendation"),
    ]

    for query, expected_intent in test_queries:
        state = await run_orchestrator_pipeline(
            user_input=query,
            farmer_context={"latitude": 26.9124, "longitude": 75.7873, "state": "Rajasthan"}
        )
        assert state["intent"] == expected_intent, f"Query '{query}' classified as '{state['intent']}', expected '{expected_intent}'"
        assert state["tool_status"] == "success", f"Tool status for query '{query}' was '{state['tool_status']}'"
        assert len(state["final_response"]) > 0
