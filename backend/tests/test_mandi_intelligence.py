"""
Comprehensive Unit & Integration Test Suite for Mandi Price Intelligence Features:
1. Best Nearby & Best Practical Mandi Ranking
2. Mandi Comparison & Same Market Validation
3. Price Opportunity Alerts
4. Sell-Now vs Wait Advisory
5. Forecast Explanation
6. Voice Tool Registry & Numeric Integrity
7. Multi-Turn Voice Slot Filling & Clarification
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base, get_db
from app.schemas.market import (
    PriceAlertCreate,
    BestMandiResponse,
    MandiComparisonResponse,
    MandiAdvisoryResponse,
    ForecastExplanationResponse
)
from app.services.mandi_intelligence import (
    MandiIntelligenceService,
    haversine_distance,
    get_mandi_coordinates,
    calculate_freshness,
    compute_practical_score
)
from app.orchestrator.nodes.intent_classification import intent_classification_node
from app.orchestrator.nodes.synthesizer import response_synthesizer_node
from app.orchestrator.state import OrchestratorState
from app.tools.registry import tool_registry
from app.main import app


async def get_test_session():
    """Helper to create an in-memory SQLite async session with created tables."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return test_engine, async_session


# =============================================================================
# 1. GEODESIC DISTANCE & COORDINATES TESTS
# =============================================================================

def test_01_haversine_distance_accuracy():
    dist = haversine_distance(26.9124, 75.7873, 24.5854, 73.7125)
    assert 300.0 <= dist <= 350.0
    assert haversine_distance(26.9124, 75.7873, 26.9124, 75.7873) == 0.0


def test_02_mandi_coordinate_resolution():
    coords = get_mandi_coordinates("Jaipur Mandi", "Jaipur", "Rajasthan")
    assert coords is not None
    assert coords[0] == 26.9124

    coords_kota = get_mandi_coordinates("Kota", "Kota", "Rajasthan")
    assert coords_kota is not None
    assert coords_kota[0] == 25.2138


# =============================================================================
# 2. FRESHNESS & PRACTICAL SCORE FORMULA TESTS
# =============================================================================

def test_03_freshness_classification_rules():
    status_fresh, score_fresh = calculate_freshness("30/08/2026")
    assert status_fresh in ["FRESH", "RECENT"]
    assert score_fresh >= 0.70

    status_stale, score_stale = calculate_freshness("01/01/2020")
    assert status_stale == "STALE"
    assert score_stale == 0.40


def test_04_compute_practical_score_math():
    score1, reason1 = compute_practical_score(
        price=2580.0,
        min_pool_price=2400.0,
        max_pool_price=2670.0,
        distance_km=8.4,
        max_radius_km=300.0,
        freshness_score=1.0
    )
    assert 0.0 <= score1 <= 1.0
    assert len(reason1) > 0

    score2, reason2 = compute_practical_score(
        price=2670.0,
        min_pool_price=2400.0,
        max_pool_price=2670.0,
        distance_km=62.0,
        max_radius_km=300.0,
        freshness_score=1.0
    )
    assert 0.0 <= score2 <= 1.0


# =============================================================================
# 3. BEST PRACTICAL MANDI RANKING TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_05_best_practical_mandi_ranking_and_distinction():
    res = await MandiIntelligenceService.get_best_nearby_mandis(
        commodity="Wheat",
        latitude=26.9124,
        longitude=75.7873,
        district="Jaipur",
        limit=5
    )

    assert isinstance(res, BestMandiResponse)
    assert res.commodity == "Wheat"
    assert len(res.ranked_mandis) > 0
    assert res.best_practical_mandi is not None
    assert res.highest_price_mandi is not None

    all_prices = [m.modal_price for m in res.ranked_mandis]
    assert res.highest_price_mandi.modal_price == max(all_prices)
    assert res.highest_price_mandi.is_highest_price is True

    for m in res.ranked_mandis:
        assert 0.0 <= m.practical_score <= 1.0
        assert m.freshness_status in ["FRESH", "RECENT", "STALE"]
        assert m.unit == "₹/Quintal"


# =============================================================================
# 4. MANDI COMPARISON TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_06_mandi_comparison_mathematics():
    res = await MandiIntelligenceService.compare_mandis(
        commodity="Wheat",
        market_a="Udaipur",
        market_b="Jaipur"
    )

    assert isinstance(res, MandiComparisonResponse)
    assert res.commodity == "Wheat"
    assert res.market_a.modal_price > 0
    assert res.market_b.modal_price > 0

    expected_diff = round(abs(res.market_a.modal_price - res.market_b.modal_price), 2)
    assert res.comparison.price_difference == expected_diff
    assert res.comparison.percentage_difference >= 0.0
    assert "₹" in res.comparison.summary_hi
    assert "₹" in res.comparison.summary_en


# =============================================================================
# 5. PRICE OPPORTUNITY ALERTS TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_07_create_and_list_price_alerts():
    engine, session_maker = await get_test_session()
    async with session_maker() as session:
        payload = PriceAlertCreate(
            commodity="Mustard",
            market="Kota Mandi",
            target_price=5800.0,
            direction="ABOVE",
            user_id="farmer_123"
        )
        alert_res = await MandiIntelligenceService.create_price_alert(session, payload)

        assert alert_res.id is not None
        assert alert_res.commodity == "Mustard"
        assert alert_res.target_price == 5800.0
        assert alert_res.status == "ACTIVE"

        list_res = await MandiIntelligenceService.get_user_alerts(session, "farmer_123")
        assert list_res.total >= 1
        assert list_res.alerts[0].commodity == "Mustard"

    await engine.dispose()


# =============================================================================
# 6. SELL-NOW VS WAIT ADVISORY TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_08_sell_wait_advisory_decision_matrix():
    res = await MandiIntelligenceService.get_sell_wait_advisory(
        commodity="Wheat",
        market="Jaipur Mandi",
        days=7
    )

    assert isinstance(res, MandiAdvisoryResponse)
    assert res.observed.price > 0
    assert res.forecast.projected_price > 0
    assert res.advisory.signal in ["FAVORABLE_TO_SELL", "POSSIBLE_UPSIDE", "STABLE", "INSUFFICIENT_EVIDENCE"]
    assert len(res.advisory.recommendation_hi) > 0
    assert len(res.advisory.recommendation_en) > 0
    assert len(res.advisory.reasoning_factors) > 0


# =============================================================================
# 7. FORECAST EXPLANATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_09_forecast_explanation_signals():
    res = await MandiIntelligenceService.get_forecast_explanation(
        commodity="Wheat",
        market="Jaipur Mandi"
    )

    assert isinstance(res, ForecastExplanationResponse)
    assert res.commodity == "Wheat"
    assert len(res.factors) >= 3
    factor_names = [f.factor_name for f in res.factors]
    assert "Historical 7-Day Momentum" in factor_names
    assert "Agmarknet Seasonal Arrival Index" in factor_names


# =============================================================================
# 8. TOOL REGISTRY VOICE INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_10_tool_registry_mandi_tools():
    # 1. Best Nearby Tool
    res_nearby = await tool_registry.execute("best_nearby_mandi_tool", slots={"commodity": "Wheat", "latitude": 26.9124, "longitude": 75.7873})
    assert res_nearby.status.value == "success"
    assert "दर्ज भाव" in res_nearby.localized_message.get("hi", "")

    # 2. Best Practical Mandi Tool Alias
    res_practical = await tool_registry.execute("best_practical_mandi_tool", slots={"commodity": "Wheat", "latitude": 26.9124, "longitude": 75.7873})
    assert res_practical.status.value == "success"
    assert "व्यावहारिक" in res_practical.localized_message.get("hi", "")

    # 3. Mandi Comparison Tool
    res_comp = await tool_registry.execute("mandi_comparison_tool", slots={"commodity": "Wheat", "market_a": "Udaipur", "market_b": "Jaipur"})
    assert res_comp.status.value == "success"
    assert res_comp.data["comparison"]["price_difference"] >= 0

    # 4. Mandi Advisory Tool
    res_adv = await tool_registry.execute("mandi_advisory_tool", slots={"commodity": "Wheat", "market": "Jaipur Mandi"})
    assert res_adv.status.value == "success"
    assert res_adv.data["advisory"]["signal"] in ["FAVORABLE_TO_SELL", "POSSIBLE_UPSIDE", "STABLE", "INSUFFICIENT_EVIDENCE"]


# =============================================================================
# 9. REST API ENDPOINT TESTS (Including /best-practical)
# =============================================================================

@pytest.mark.asyncio
async def test_11_api_best_practical_and_nearby_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Best nearby
        res1 = await client.get("/api/v1/market/best-nearby?commodity=Wheat&latitude=26.9124&longitude=75.7873")
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["commodity"] == "Wheat"
        assert len(data1["ranked_mandis"]) > 0
        assert "best_practical_mandi" in data1

        # 2. Best practical dedicated alias endpoint
        res1b = await client.get("/api/v1/market/best-practical?commodity=Wheat&latitude=26.9124&longitude=75.7873")
        assert res1b.status_code == 200
        data1b = res1b.json()
        assert data1b["best_practical_mandi"]["practical_score"] >= 0.0

        # 3. Compare
        res2 = await client.get("/api/v1/market/compare?commodity=Wheat&market_a=Udaipur&market_b=Jaipur")
        assert res2.status_code == 200
        data2 = res2.json()
        assert "price_difference" in data2["comparison"]

        # 4. Advisory
        res3 = await client.get("/api/v1/market/advisory?commodity=Wheat&market=Jaipur Mandi")
        assert res3.status_code == 200
        data3 = res3.json()
        assert "signal" in data3["advisory"]


# =============================================================================
# 10. MULTI-TURN VOICE CLARIFICATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_12_multi_turn_voice_mandi_comparison_clarification():
    # Turn 1: "Compare मंडी" (missing crop)
    state1 = OrchestratorState(
        user_input="Compare मंडी भाव",
        session_id="test_session_1",
        detected_language="hi"
    )
    s1 = await intent_classification_node(state1)
    assert s1["intent"] == "compare_mandi"
    assert s1.get("requires_clarification") is True
    assert "फसल" in s1.get("clarification_question", "")

    # Turn 2: Farmer provides crop "गेहूं"
    state2 = OrchestratorState(
        user_input="गेहूं का भाव",
        session_id="test_session_1",
        filled_slots={"commodity": "Wheat"},
        detected_language="hi"
    )
    s2 = await intent_classification_node(state2)
    assert s2.get("filled_slots", {}).get("commodity") == "Wheat"


@pytest.mark.asyncio
async def test_13_multi_turn_voice_price_alert_clarification():
    # Turn 1: "गेहूं के लिए alert लगाओ" (missing target price)
    state1 = OrchestratorState(
        user_input="गेहूं के लिए alert लगाओ",
        session_id="test_session_2",
        detected_language="hi"
    )
    s1 = await intent_classification_node(state1)
    assert s1["intent"] == "price_alert"
    assert s1.get("requires_clarification") is True
    assert "भाव" in s1.get("clarification_question", "")
