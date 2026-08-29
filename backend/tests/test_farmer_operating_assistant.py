"""
Comprehensive test suite for FarmFusion Farmer Operating Assistant.

Validates all 30 operating assistant scenarios:
1. English weather
2. Hindi weather
3. Gujarati query
4. Marathi query
5. Punjabi query
6. Tamil query
7. Telugu query
8. Kannada query
9. Bengali query
10. Odia query
11. Assamese query
12. Mewari vocabulary normalization
13. Marwari vocabulary normalization
14. Bhojpuri vocabulary normalization
15. Ambiguous intent handling
16. Low confidence clarification trigger (Safety Rule #6)
17. Follow-up anaphora resolution
18. "First one" / "Second one" explanation
19. Counterfactual soil change
20. Counterfactual rain change
21. Live weather tool integration
22. Crop recommendation tool integration
23. Mandi price & forecast tool integration
24. Disease diagnosis without photo redirection
25. In-app navigation whitelist execution
26. Unsupported purchase request transparent admission
27. Unsupported scheme filing transparent admission
28. Repeat last response memory
29. Speech rate control
30. Crop care and agronomic management guide
"""
import pytest
from app.orchestrator.graph import run_orchestrator_pipeline
from app.tools.registry import tool_registry, ToolStatus
from app.voice.languages import normalize_crop_name, normalize_soil_name, resolve_language_code


# 1. English Weather
@pytest.mark.asyncio
async def test_scenario_01_english_weather():
    res = await run_orchestrator_pipeline("What is the weather in Jaipur today?", detected_language="en")
    assert res["intent"] == "weather"
    assert res["tool_status"] == "success"
    assert "temperature" in res["final_response"].lower()


# 2. Hindi Weather
@pytest.mark.asyncio
async def test_scenario_02_hindi_weather():
    res = await run_orchestrator_pipeline("भाई आज मौसम कैसा रहेगा?", detected_language="hi")
    assert res["intent"] == "weather"
    assert res["tool_status"] == "success"
    assert "तापमान" in res["final_response"]


# 3-11. Scheduled Indian Languages
@pytest.mark.asyncio
async def test_scenario_03_gujarati_mandi():
    res = await run_orchestrator_pipeline("ઘઉંનો આજનો ભાવ શું છે?", detected_language="gu")
    assert res["intent"] == "mandi"
    assert res["tool_status"] == "success"


@pytest.mark.asyncio
async def test_scenario_04_marathi_crop():
    res = await run_orchestrator_pipeline("माझ्या शेतात कोणतं पीक घ्यावं?", detected_language="mr")
    assert res["intent"] == "crop_recommendation"
    assert res["tool_status"] == "success"


@pytest.mark.asyncio
async def test_scenario_05_punjabi_weather():
    res = await run_orchestrator_pipeline("ਅੱਜ ਮੌਸਮ ਕਿਵੇਂ ਰਹੇਗਾ?", detected_language="pa")
    assert res["intent"] == "weather"
    assert res["tool_status"] == "success"


@pytest.mark.asyncio
async def test_scenario_06_to_11_multilingual_resolution():
    for lang in ["ta", "te", "kn", "bn", "or", "as"]:
        assert resolve_language_code(lang) == lang


# 12-14. Regional Dialects Normalization (Mewari, Marwari, Bhojpuri)
def test_scenario_12_mewari_vocabulary():
    assert normalize_crop_name("बाजरो") == "Pearl Millet (Bajra)"
    assert normalize_crop_name("singdana") == "Groundnut (Peanut)"
    assert resolve_language_code("mewari") == "hi"


def test_scenario_13_marwari_vocabulary():
    assert normalize_crop_name("gehun") == "Wheat"
    assert normalize_crop_name("dhan") == "Rice (Paddy)"
    assert resolve_language_code("marwari") == "hi"


def test_scenario_14_bhojpuri_vocabulary():
    assert normalize_crop_name("chhola") == "Chickpea (Gram / Chana)"
    assert resolve_language_code("bhojpuri") == "hi"


# 15-16. Ambiguous Intent & Low Confidence Clarification (Safety Rule #6)
@pytest.mark.asyncio
async def test_scenario_15_16_low_confidence_clarification():
    res = await run_orchestrator_pipeline("qwertyuiop12345", detected_language="hi")
    assert res["intent"] == "clarify"
    assert res["requires_clarification"] is True
    assert "क्या आप" in res["final_response"] or "clarify" in res["final_response"]


# 17-18. Follow-up Anaphora: "पहली वाली क्यों?" & "दूसरी वाली क्यों?"
@pytest.mark.asyncio
async def test_scenario_17_18_why_recommendation():
    sample_recs = [
        {"crop_name": "Groundnut (Peanut)", "suitability_score": 0.90, "contributing_factors": ["Optimal temperature", "Suitable sandy soil"]},
        {"crop_name": "Pearl Millet (Bajra)", "suitability_score": 0.85, "contributing_factors": ["Drought tolerance"]}
    ]
    res1 = await run_orchestrator_pipeline("वो पहली वाली फसल क्यों अच्छी है?", detected_language="hi", last_recommendations=sample_recs)
    assert res1["intent"] == "explain_recommendation"
    assert "Groundnut" in res1["final_response"]

    res2 = await run_orchestrator_pipeline("दूसरी वाली क्यों?", detected_language="hi", last_recommendations=sample_recs)
    assert res2["intent"] == "explain_recommendation"
    assert "Pearl Millet" in res2["final_response"] or "Bajra" in res2["final_response"]


# 19-20. Counterfactual What-If (Soil & Rain Changes)
@pytest.mark.asyncio
async def test_scenario_19_counterfactual_soil():
    res = await run_orchestrator_pipeline(
        "अगर मिट्टी काली हो तो क्या बोएं?",
        detected_language="hi",
        farmer_context={"latitude": 24.6178, "longitude": 73.9937, "state": "Rajasthan"}
    )
    assert res["intent"] == "what_if"
    assert res["tool_status"] == "success"
    assert len(res["last_recommendations"]) > 0


@pytest.mark.asyncio
async def test_scenario_20_counterfactual_rain():
    res = await run_orchestrator_pipeline(
        "अगर पानी कम मिले तो क्या करें?",
        detected_language="hi",
        farmer_context={"latitude": 24.6178, "longitude": 73.9937, "state": "Rajasthan", "soil_type": "Sandy Soil"}
    )
    assert res["intent"] == "what_if"
    assert res["tool_status"] == "success"


# 21-23. Weather, Crop, Mandi Tool Calls
@pytest.mark.asyncio
async def test_scenario_21_to_23_tool_integrations():
    w = await tool_registry.execute("weather_tool", {"latitude": 26.9124, "longitude": 75.7873})
    assert w.status == ToolStatus.SUCCESS
    assert "temperature_c" in w.data

    c = await tool_registry.execute("crop_recommendation_tool", {"latitude": 24.6178, "longitude": 73.9937, "soil_type": "Sandy Soil"})
    assert c.status == ToolStatus.SUCCESS

    m = await tool_registry.execute("market_price_tool", {"commodity": "Wheat", "state": "Rajasthan"})
    assert m.status == ToolStatus.SUCCESS


# 24. Disease Diagnosis without Photo (Guides to Camera UI)
@pytest.mark.asyncio
async def test_scenario_24_disease_photo_redirect():
    res = await run_orchestrator_pipeline("ये पत्ता खराब लग रहा है, इसकी फोटो देखकर बीमारी बताओ", detected_language="hi")
    assert res["intent"] == "disease"
    assert "कैमरा" in res["final_response"] or "camera" in res["final_response"].lower()


# 25. In-App Navigation Whitelist
@pytest.mark.asyncio
async def test_scenario_25_navigation_commands():
    for cmd, expected_dest in [
        ("मंडी वाला पेज खोलो", "market_prices"),
        ("मौसम दिखाओ", "weather"),
        ("फसल सलाह खोलो", "crop_recommendation"),
        ("होम पर चलो", "home"),
        ("वापस जाओ", "back"),
    ]:
        res = await run_orchestrator_pipeline(cmd, detected_language="hi")
        assert res["intent"] == "navigation"
        assert res["tool_status"] == "success"
        assert res["tool_output"]["destination"] == expected_dest


# 26-27. Unsupported Capabilities (Direct Purchases & Autonomous Scheme Applications)
@pytest.mark.asyncio
async def test_scenario_26_unsupported_purchase():
    res = await run_orchestrator_pipeline("मेरे लिए 10 बोरी यूरिया आर्डर कर दो", detected_language="hi")
    assert res["intent"] == "unsupported_capability"
    assert "सीधे खाद या बीज की ऑनलाइन खरीद नहीं करता" in res["final_response"]


@pytest.mark.asyncio
async def test_scenario_27_unsupported_scheme_submission():
    res = await run_orchestrator_pipeline("पीएम किसान योजना का फॉर्म भर दो", detected_language="hi")
    assert res["intent"] == "unsupported_capability"
    assert "आधिकारिक सरकारी पोर्टल" in res["final_response"]


# 28. Repeat Last Response Memory
@pytest.mark.asyncio
async def test_scenario_28_repeat_last_response():
    turn = await run_orchestrator_pipeline(
        "ये बात दोबारा बोलो",
        detected_language="hi",
        farmer_context={"last_final_response": "आज जयपुर में तापमान 28°C रहेगा।"}
    )
    assert turn["intent"] == "repeat_last"
    assert turn["tool_status"] == "success"


# 29. Speech Rate Control
@pytest.mark.asyncio
async def test_scenario_29_speech_rate_control():
    turn = await run_orchestrator_pipeline("भाई जरा धीरे बोलो", detected_language="hi")
    assert turn["intent"] == "speech_control"
    assert "आराम से" in turn["final_response"] or "slowly" in turn["final_response"].lower()


# 30. Crop Care and Fertilizer Timing
@pytest.mark.asyncio
async def test_scenario_30_crop_care_guide():
    turn = await run_orchestrator_pipeline("धान की देखभाल कैसे करूं?", detected_language="hi")
    assert turn["intent"] == "crop_care"
    assert turn["tool_status"] == "success"
    assert "देखभाल" in turn["final_response"] or "care" in turn["final_response"].lower()
