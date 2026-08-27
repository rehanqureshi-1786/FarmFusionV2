"""
Tests for FarmFusion Crop Recommendation Agent V2.

Verifies:
1. Local SQLite Agricultural Knowledge Base queries
2. Agronomic Ranking & Confidence Engine (High/Medium/Low/Unclear tiers)
3. Local Crop Engine Mode A (Soil Report + XGBoost + ICAR)
4. Local Crop Engine Mode B (No Soil Report + ICAR Regional profiling)
5. Master Agent V2 routing (Local First, Fallback on low confidence)
6. Backward compatibility with existing API contracts
"""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.crop_agent_v2.agriculture_db import agriculture_repo
from app.services.crop_agent_v2.ranking_engine import ranking_engine
from app.services.crop_agent_v2.local_engine import local_crop_engine
from app.services.crop_agent_v2.agent import crop_agent_v2
from app.models.schemas import CropRecommendRequest, SoilType


# --------------------------------------------------------------------------
# 1. SQLite Agricultural DB Repository Tests
# --------------------------------------------------------------------------
def test_agriculture_db_profiles():
    profiles = agriculture_repo.get_all_crop_profiles()
    assert len(profiles) >= 20, "Expected at least 20 ICAR crop profiles in database"
    
    # Check Rice profile
    rice = agriculture_repo.get_crop_profile("Rice")
    assert rice is not None
    assert rice["hindi_name"] == "धान / चावल"
    assert "Kharif" in rice["suitable_seasons"]
    assert rice["water_requirement_tier"] == "High"


def test_agriculture_db_regional_and_soil():
    # Rajasthan regional check
    bajra_raj = agriculture_repo.get_regional_suitability("rajasthan", "Pearl Millet (Bajra)")
    assert bajra_raj is not None
    assert bajra_raj["suitability_multiplier"] > 1.0

    # Soil compatibility check
    sand_bajra = agriculture_repo.get_soil_compatibility("Sandy Soil", "Pearl Millet (Bajra)")
    assert sand_bajra is not None
    assert sand_bajra["compatibility_score"] >= 0.9


# --------------------------------------------------------------------------
# 2. Ranking Engine & Confidence Tier Tests
# --------------------------------------------------------------------------
def test_ranking_engine_mode_a():
    candidates = [
        {"crop_name": "Pearl Millet (Bajra)", "probability": 0.85},
        {"crop_name": "Wheat", "probability": 0.10},
    ]
    ranked = ranking_engine.rank_candidates(
        candidates=candidates,
        state="rajasthan",
        season="Kharif",
        soil_type="Sandy Soil",
        ph=7.2,
        temperature_c=32.0,
        rainfall_mm=450.0,
        nitrogen=60.0,
        phosphorus=30.0,
        potassium=30.0,
        is_mode_a=True,
    )
    assert len(ranked) >= 2
    top = ranked[0]
    assert top["crop_name"] == "Pearl Millet (Bajra)"
    assert top["confidence_tier"] in ["high", "medium"]
    assert top["confidence_score"] >= 0.45
    assert len(top["contributing_factors"]) > 0


def test_ranking_engine_mode_b_seasonal():
    candidates = [
        {"crop_name": "Wheat", "probability": 0.70},
        {"crop_name": "Pearl Millet (Bajra)", "probability": 0.70},
    ]
    # In Rabi season with cool temps, Wheat should rank above Bajra
    ranked = ranking_engine.rank_candidates(
        candidates=candidates,
        state="punjab",
        season="Rabi",
        soil_type="Alluvial Soil",
        ph=6.8,
        temperature_c=18.0,
        rainfall_mm=550.0,
        is_mode_a=False,
    )
    assert ranked[0]["crop_name"] == "Wheat"
    assert ranked[0]["confidence_score"] >= 0.45


# --------------------------------------------------------------------------
# 3. Local Crop Engine Execution Tests
# --------------------------------------------------------------------------
def test_local_engine_mode_a_execution():
    ranked, is_reliable, msg = local_crop_engine.recommend_mode_a(
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
        farm_size_acres=2.0,
    )
    assert is_reliable is True
    assert len(ranked) > 0
    assert ranked[0]["source"] == "local_agent"
    assert ranked[0]["expected_yield_tons"] > 0


def test_local_engine_mode_b_execution():
    ranked, is_reliable, msg = local_crop_engine.recommend_mode_b(
        temperature_c=26.0,
        humidity_pct=65.0,
        rainfall_mm=750.0,
        ph=6.8,
        soil_type="Black Soil",
        state="maharashtra",
        season="Kharif",
        farm_size_acres=1.5,
    )
    assert is_reliable is True
    assert len(ranked) > 0
    assert ranked[0]["source"] == "local_agent"


# --------------------------------------------------------------------------
# 4. Master Agent V2 Integration Tests
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_agent_v2_primary_local_execution():
    """Verify that normal requests use local agent with fallback_used=False."""
    recs, insights, meta = await crop_agent_v2.get_recommendations(
        location="Jaipur, Rajasthan",
        state="rajasthan",
        soil_type="sandy",
        temperature_c=30.0,
        rainfall_mm=400.0,
        farm_size_acres=2.0,
        language="hi",
    )
    assert len(recs) >= 1
    assert meta["fallback_used"] is False
    assert meta["recommendation_source"] == "local_agent"
    assert meta["is_reliable"] is True
    assert recs[0].confidence_score >= 0.45
    assert recs[0].growing_duration_months > 0
    assert "ICAR" in insights or "कृषि" in insights


@pytest.mark.asyncio
async def test_agent_v2_force_fallback_routing():
    """Verify that force fallback routes to Groq/Safety fallback and sets provenance correctly."""
    recs, insights, meta = await crop_agent_v2.get_recommendations(
        location="Unknown Desert Area",
        force_fallback=True,
        language="en",
    )
    assert len(recs) >= 1
    assert meta["fallback_used"] is True
    assert meta["recommendation_source"] in ["groq_fallback", "safety_fallback"]


# --------------------------------------------------------------------------
# 5. REST API Compatibility Test (/crop/recommend)
# --------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_crop_recommend_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "location": "Udaipur, Rajasthan",
            "soil_type": "sandy",
            "rainfall_mm": 450.0,
            "temperature_c": 28.0,
            "farm_size_acres": 2.5,
            "preferred_language": "hi",
        }
        response = await client.post("/crop/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["recommendations"]) > 0
        top = data["recommendations"][0]
        assert "crop_name" in top
        assert "confidence_score" in top
        assert "expected_yield_tons" in top
        assert "market_demand" in top
        assert "estimated_profit_usd" in top
        assert "growing_duration_months" in top
        assert isinstance(top["growing_duration_months"], int)
