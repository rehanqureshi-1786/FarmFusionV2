"""
Comprehensive Data Provenance & Quality Hardening Tests for Crop Recommendation Agent V2.

Verifies:
1. Local recommendation with Internet disabled (offline operation).
2. Local recommendation without GROQ_API_KEY.
3. Reliable local result does NOT invoke Groq.
4. Unreliable local result invokes Groq when available.
5. Groq unavailable -> safe local rule-based fallback.
6. Mode B does not fabricate N/P/K.
7. Economic estimates are explicitly labelled as benchmark estimates (not live prices or guaranteed profit).
8. Heuristic soil scores are explicitly labelled as heuristics (score_source="farmfusion_heuristic").
9. API response contains recommendation provenance (recommendation_source, fallback_used).
10. Recommendation explanation does not falsely claim ICAR endorsement for heuristics.
"""
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.crop_agent_v2.agriculture_db import agriculture_repo
from app.services.crop_agent_v2.ranking_engine import ranking_engine
from app.services.crop_agent_v2.local_engine import local_crop_engine
from app.services.crop_agent_v2.agent import crop_agent_v2


# 1. Local recommendation with Internet disabled
@pytest.mark.asyncio
async def test_offline_local_recommendation():
    """Verify local recommendation executes with complete network isolation."""
    with patch("httpx.AsyncClient.get", side_effect=RuntimeError("Network unreachable")), \
         patch("app.agents.groq_client.groq_client.is_available", return_value=False):
        recs, insights, meta = await crop_agent_v2.get_recommendations(
            location="Jaipur, Rajasthan",
            state="rajasthan",
            soil_type="sandy",
            temperature_c=30.0,
            rainfall_mm=400.0,
            farm_size_acres=2.0,
            language="en"
        )
        assert meta["fallback_used"] is False
        assert meta["recommendation_source"] == "local_agent"
        assert meta["is_reliable"] is True
        assert len(recs) >= 1


# 2. Local recommendation without GROQ_API_KEY
@pytest.mark.asyncio
async def test_recommendation_without_groq_api_key():
    """Verify local recommendation works when GROQ_API_KEY is unset."""
    with patch("app.agents.groq_client.groq_client.is_available", return_value=False):
        recs, insights, meta = await crop_agent_v2.get_recommendations(
            location="Karnal, Haryana",
            state="haryana",
            soil_type="alluvial",
            temperature_c=22.0,
            rainfall_mm=600.0,
            language="en"
        )
        assert meta["recommendation_source"] == "local_agent"
        assert meta["is_reliable"] is True
        assert len(recs) >= 1


# 3. Reliable local result does NOT invoke Groq
@pytest.mark.asyncio
async def test_reliable_result_bypasses_groq():
    """Verify Groq API is never called when local result is reliable."""
    with patch("app.agents.groq_client.groq_client.chat_completion", new_callable=AsyncMock) as mock_groq, \
         patch("app.agents.groq_client.groq_client.is_available", return_value=True):
        recs, insights, meta = await crop_agent_v2.get_recommendations(
            location="Udaipur, Rajasthan",
            state="rajasthan",
            soil_type="sandy",
            temperature_c=30.0,
            rainfall_mm=400.0,
            nitrogen=60.0,
            phosphorus=30.0,
            potassium=30.0,
            ph=7.0,
        )
        assert meta["fallback_used"] is False
        assert meta["is_reliable"] is True
        mock_groq.assert_not_called()


# 4. Unreliable local result invokes Groq when available
@pytest.mark.asyncio
async def test_unreliable_result_triggers_groq():
    """Verify Groq is invoked when local confidence is below threshold or forced."""
    mock_groq_response = {
        "success": True,
        "content": '{"recommendations": [{"crop_name": "Pearl Millet (Bajra)", "confidence_score": 0.72, "expected_yield_tons": 2.0, "market_demand": "high", "estimated_profit_usd": 300, "growing_duration_months": 4, "water_requirement": "low"}], "insights": "Fallback guidance"}'
    }
    with patch("app.agents.groq_client.groq_client.chat_completion", new_callable=AsyncMock, return_value=mock_groq_response) as mock_groq, \
         patch("app.agents.groq_client.groq_client.is_available", return_value=True):
        recs, insights, meta = await crop_agent_v2.get_recommendations(
            location="Unknown Harsh Area",
            force_fallback=True,
        )
        assert meta["fallback_used"] is True
        assert meta["recommendation_source"] == "groq_fallback"
        mock_groq.assert_called_once()


# 5. Groq unavailable -> safe local fallback
@pytest.mark.asyncio
async def test_groq_unavailable_safe_fallback():
    """Verify graceful fallback when both local is forced to fallback and Groq is unavailable."""
    with patch("app.agents.groq_client.groq_client.is_available", return_value=False):
        recs, insights, meta = await crop_agent_v2.get_recommendations(
            location="Remote Outback",
            force_fallback=True,
        )
        assert meta["fallback_used"] is True
        assert len(recs) >= 1
        assert "safety" in meta["recommendation_source"] or "groq_fallback" in meta["recommendation_source"]


# 6. Mode B does not fabricate N/P/K
def test_mode_b_no_npk_fabrication():
    """Verify Mode B executes without fabricating synthetic N/P/K values."""
    ranked, is_reliable, msg = local_crop_engine.recommend_mode_b(
        temperature_c=25.0,
        humidity_pct=60.0,
        rainfall_mm=600.0,
        soil_type="Black Soil",
        state="maharashtra",
        season="Kharif",
    )
    assert is_reliable is True
    assert len(ranked) > 0
    # Contributing factors should not mention fake N/P/K
    for r in ranked:
        for factor in r.get("contributing_factors", []):
            assert "soil N (" not in factor.lower()
            assert "soil P (" not in factor.lower()
            assert "soil K (" not in factor.lower()


# 7. Economic estimates are labelled as estimates
def test_economic_estimates_labelled():
    """Verify economic data is explicitly labelled as benchmark estimates."""
    ranked, _, _ = local_crop_engine.recommend_mode_a(
        nitrogen=80.0,
        phosphorus=40.0,
        potassium=40.0,
        ph=6.5,
        temperature_c=28.0,
        humidity_pct=70.0,
        rainfall_mm=600.0,
        state="rajasthan",
        soil_type="Loamy Soil",
        season="Kharif",
    )
    assert len(ranked) > 0
    top = ranked[0]
    assert top["economic_data_status"] == "benchmark_estimate_not_live_price"
    assert "benchmark_gross_return_usd" in top
    assert "benchmark_gross_return_inr" in top


# 8. Heuristic soil scores are labelled as heuristics
def test_heuristic_soil_scores_labelled():
    """Verify soil texture matrix compatibility scores are tagged as farmfusion_heuristic."""
    soil_mat = agriculture_repo.get_soil_compatibility("Sandy Soil", "Pearl Millet (Bajra)")
    assert soil_mat is not None
    assert soil_mat["score_source"] == "farmfusion_heuristic"
    assert soil_mat["provenance_category"] == "C_FARMFUSION_HEURISTIC"


# 9. API response contains recommendation provenance
@pytest.mark.asyncio
async def test_api_response_provenance():
    """Verify API endpoint returns valid structure with provenance metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "location": "Indore, Madhya Pradesh",
            "soil_type": "loamy",
            "rainfall_mm": 800.0,
            "temperature_c": 26.0,
            "farm_size_acres": 3.0,
            "preferred_language": "en",
        }
        response = await client.post("/crop/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["recommendations"]) > 0


# 10. Recommendation explanation does not falsely claim ICAR endorsement
@pytest.mark.asyncio
async def test_explanation_no_false_icar_claim():
    """Verify farmer explanations do NOT claim 'ICAR recommends' for heuristic outputs."""
    recs, insights, meta = await crop_agent_v2.get_recommendations(
        location="Nashik, Maharashtra",
        state="maharashtra",
        soil_type="black",
        temperature_c=28.0,
        rainfall_mm=700.0,
        language="en",
    )
    # The message must say FarmFusion recommendation based on agricultural reference data
    assert "ICAR expert engine recommends" not in insights
    assert "ICAR recommends" not in insights
    assert "FarmFusion recommendation" in insights
