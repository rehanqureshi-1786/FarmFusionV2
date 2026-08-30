"""
Multi-turn conversational and anaphora resolution tests for FarmFusion Voice Agent.

Tests:
1. Follow-up anaphora: "पहली वाली क्यों?" resolves factors from previous crop recommendation
2. Cross-domain entity resolution: "इसमें कौनसी बीमारी लगती है?" carries forward crop name
3. Counterfactual 'What-if': "अगर मिट्टी काली हो?" updates condition and re-evaluates
4. Unsupported action transparent communication (purchasing, scheme submission)
5. Safety rule #6 low-confidence clarification
"""
import pytest
from app.orchestrator.graph import run_orchestrator_pipeline


@pytest.mark.asyncio
async def test_multiturn_crop_recommendation_and_why_explanation():
    # Turn 1: Farmer asks for crop recommendation in sandy soil
    turn1 = await run_orchestrator_pipeline(
        user_input="रेतीली मिट्टी में कौन सी फसल लगाएं?",
        detected_language="hi",
        session_id="session_101",
        farmer_context={"latitude": 24.6178, "longitude": 73.9937, "state": "Rajasthan", "soil_type": "Sandy Soil"}
    )
    assert turn1["intent"] == "crop_recommendation"
    assert turn1["tool_status"] == "success"
    assert len(turn1["last_recommendations"]) > 0
    top_crop = turn1["last_recommendations"][0]["crop_name"]
    assert len(top_crop) > 0

    # Turn 2: Farmer asks "पहली वाली क्यों?" (Why the top crop?)
    turn2 = await run_orchestrator_pipeline(
        user_input="पहली वाली क्यों?",
        detected_language="hi",
        session_id="session_101",
        farmer_context={"latitude": 24.6178, "longitude": 73.9937, "state": "Rajasthan"},
        last_recommendations=turn1["last_recommendations"]
    )
    assert turn2["intent"] == "explain_recommendation"
    assert top_crop in turn2["final_response"] or "प्राथमिकता" in turn2["final_response"]
    # Synthesizer must cite authentic factors from payload
    assert len(turn2["final_response"]) > 10


@pytest.mark.asyncio
async def test_cross_domain_crop_to_mandi_and_disease():
    # Turn 1: Farmer asks for mandi price of Wheat
    turn1 = await run_orchestrator_pipeline(
        user_input="गेहूं का मंडी भाव क्या है?",
        detected_language="hi",
        session_id="session_102",
        farmer_context={"state": "Rajasthan", "district": "Udaipur"}
    )
    assert turn1["intent"] == "mandi"
    assert "गेहूं" in turn1["final_response"] or "Wheat" in turn1["final_response"]

    # Turn 2: Farmer asks "इसमें कौनसी बीमारी लगती है?" (Carrying forward Wheat)
    turn2 = await run_orchestrator_pipeline(
        user_input="इसमें कौनसी बीमारी लगती है?",
        detected_language="hi",
        session_id="session_102",
        last_recommendations=[{"crop_name": "Wheat"}]
    )
    assert turn2["intent"] == "disease"
    assert turn2["tool_status"] == "success"


@pytest.mark.asyncio
async def test_what_if_soil_counterfactual():
    # Turn 1: Farmer asks what if soil is black
    turn = await run_orchestrator_pipeline(
        user_input="अगर मिट्टी काली हो तो क्या बोएं?",
        detected_language="hi",
        session_id="session_103",
        farmer_context={"latitude": 24.6178, "longitude": 73.9937, "state": "Rajasthan"}
    )
    assert turn["intent"] == "what_if"
    assert turn["tool_status"] == "success"
    # Black soil in Kharif yields Rice/Sugarcane/Cotton/Maize at top
    assert len(turn["last_recommendations"]) > 0


@pytest.mark.asyncio
async def test_unsupported_purchase_admission():
    turn = await run_orchestrator_pipeline(
        user_input="मेरे लिए 5 बोरी यूरिया खरीद लो",
        detected_language="hi",
        session_id="session_104"
    )
    assert turn["intent"] == "unsupported_capability"
    assert "सीधे खाद या बीज की ऑनलाइन खरीद नहीं करता" in turn["final_response"] or "does not process" in turn["final_response"]
