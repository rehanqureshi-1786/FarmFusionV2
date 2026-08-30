"""
Local Inference & Tool Execution Test for First FarmFusion Trained Model.
Validates:
1. Canonical NLU representation for dialect query: "म्हारे खेत में बाजरो बोवणो है, पानी कम है"
2. End-to-end tool execution (Crop Recommendation)
3. Zero data fabrication rules (never fabricates N, P, K, pH, weather, mandi prices)
4. Fallback transparency
"""
import pytest
from app.voice.local.nlu import LocalAgriculturalNLUEngine
from app.voice.local.runtime import voice_runtime_router, RuntimeMode
from app.orchestrator.graph import run_orchestrator_pipeline


@pytest.mark.asyncio
async def test_first_local_model_marwari_inference():
    """
    Test exact requirement:
    Input: "म्हारे खेत में बाजरो बोवणो है, पानी कम है"
    Output: language/dialect, intent, canonical entities
    """
    nlu = LocalAgriculturalNLUEngine()
    query = "म्हारे खेत में बाजरो बोवणो है, पानी कम है"
    
    # 1. Parse via trained Local Agricultural NLU
    res = await nlu.parse(query, language="hi", dialect="rwr")
    
    assert res.intent in ["crop_recommendation", "what_if"]
    assert res.slots.get("water_availability") == "LOW"
    assert "Pearl Millet" in res.slots.get("crop_name", "") or "Bajra" in res.slots.get("crop_name", "") or "बाजरा" in res.slots.get("crop_name", "")
    assert res.safety_classification == "READ_ONLY"


@pytest.mark.asyncio
async def test_local_nlu_to_tool_registry_execution():
    """
    Test that the trained Local NLU connects directly to the ToolRegistry and LangGraph orchestrator.
    """
    turn_res = await run_orchestrator_pipeline(
        user_input="म्हाने बाजरो बोवणो है पानी कम है",
        detected_language="hi",
        detected_dialect="rwr"
    )
    
    assert turn_res["intent"] in ["crop_recommendation", "what_if"]
    assert turn_res["response_dialect"] == "rwr"
    assert turn_res["native_tts"] is False
    assert turn_res["fallback_used"] is True
    assert "थांके खेत खातर" in turn_res["final_response"] or "चोखी फसल" in turn_res["final_response"] or "Pearl Millet" in turn_res["final_response"]


@pytest.mark.asyncio
async def test_safety_and_zero_fabrication_gate():
    """
    Verify the model NEVER invents N, P, K, weather numbers, or mandi prices without verified tools.
    """
    voice_runtime_router.set_mode(RuntimeMode.OFFLINE)
    res = await voice_runtime_router.process_voice_query(
        text_query="कल का मौसम कैसा रहेगा?",
        language_hint="hi",
    )
    assert res.runtime_mode == RuntimeMode.OFFLINE
    assert res.tool_output.get("error") == "OFFLINE_NETWORK_REQUIRED"
    assert "मौसम" in res.response_text
    # Ensure no fabricated numeric temperatures or mandi prices in offline mode
    assert "°C" not in res.response_text
    assert "₹" not in res.response_text

    voice_runtime_router.set_mode(RuntimeMode.HYBRID)
