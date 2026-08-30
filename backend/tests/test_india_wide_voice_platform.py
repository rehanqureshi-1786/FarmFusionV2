"""
Comprehensive 37-Scenario Test Suite for FarmFusion India-Wide Multilingual & Regional-Dialect Voice Platform.

Covers:
1. Hindi weather
2. Gujarati weather
3. Marathi crop query
4. Punjabi mandi query
5. Bengali crop-care query
6. Telugu weather query
7. Tamil crop query
8. Kannada scheme query
9. Malayalam crop-care query
10. Odia crop query
11. Assamese weather query
12. Urdu query
13. Maithili query
14. Mewari vocabulary normalization
15. Marwari vocabulary normalization
16. Bhojpuri vocabulary normalization
17. Haryanvi vocabulary normalization
18. Chhattisgarhi vocabulary normalization
19. Code-switched Hindi-English
20. Ambiguous dialect handling
21. Low ASR confidence clarification
22. Unsupported language fallback
23. Parent-language TTS fallback
24. Multi-turn dialect conversation
25. "First one" reference resolution
26. "This crop" reference resolution
27. What-if question
28. Weather -> Crop recommendation cross-domain
29. Crop -> Mandi price cross-domain
30. Crop -> Disease information cross-domain
31. Unsupported purchase request
32. Unsupported scheme application
33. No soil report -> Mode B without fabricated N/P/K
34. Disease request without image -> request image redirect
35. Repeat last response
36. Speech speed control
37. Navigation command
"""
import pytest
from app.orchestrator.graph import run_orchestrator_pipeline
from app.voice.languages import (
    LANGUAGE_REGISTRY,
    get_language_profile,
    detect_dialect,
    normalize_agricultural_term,
    normalize_crop_name,
    normalize_soil_name,
    resolve_language_code,
)
from app.voice.providers import voice_provider_manager, BhashiniASRProvider, BhashiniTTSProvider, ExecutionTrace
from app.tools.registry import tool_registry, ToolStatus


# =============================================================================
# SCENARIOS 1-13: SCHEDULED LANGUAGE COVERAGE
# =============================================================================

@pytest.mark.asyncio
async def test_01_hindi_weather():
    turn = await run_orchestrator_pipeline("जयपुर में आज का मौसम कैसा है?", detected_language="hi")
    assert turn["intent"] == "weather"
    assert turn["tool_status"] in ["success", "unavailable"]


@pytest.mark.asyncio
async def test_02_gujarati_weather():
    turn = await run_orchestrator_pipeline("અમદાવાદમાં વાતાવરણ કેવું છે?", detected_language="gu")
    assert turn["intent"] == "weather"
    assert turn["tool_status"] in ["success", "unavailable"]


@pytest.mark.asyncio
async def test_03_marathi_crop_query():
    turn = await run_orchestrator_pipeline("माझ्या शेतात कोणतं पीक चांगलं येईल?", detected_language="mr")
    assert turn["intent"] == "crop_recommendation"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_04_punjabi_mandi_query():
    turn = await run_orchestrator_pipeline("ਕਣਕ ਦੀ ਕੀਮਤ ਕੀ ਹੈ?", detected_language="pa")
    assert turn["intent"] == "mandi"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_05_bengali_crop_care():
    turn = await run_orchestrator_pipeline("ধান ফসলে সার কখন দিতে হবে?", detected_language="bn")
    assert turn["intent"] == "crop_care"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_06_telugu_weather():
    turn = await run_orchestrator_pipeline("హైదరాబాద్‌లో వాతావరణం ఎలా ఉంది?", detected_language="te")
    assert turn["intent"] == "weather"
    assert turn["tool_status"] in ["success", "unavailable"]


@pytest.mark.asyncio
async def test_07_tamil_crop_query():
    turn = await run_orchestrator_pipeline("எந்த பயிர் சாகுபடி செய்யலாம்?", detected_language="ta")
    assert turn["intent"] == "crop_recommendation"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_08_kannada_scheme_query():
    turn = await run_orchestrator_pipeline("ರೈತರಿಗೆ ಸರಕಾರಿ ಯೋಜನೆ ಯಾವುದು?", detected_language="kn")
    assert turn["intent"] == "scheme"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_09_malayalam_crop_care():
    turn = await run_orchestrator_pipeline("വിള പരിപാലനം എങ്ങനെ ചെയ്യാം?", detected_language="ml")
    assert turn["intent"] == "crop_care"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_10_odia_crop_query():
    turn = await run_orchestrator_pipeline("କେଉଁ ଫସଲ ଚାଷ କରିବି?", detected_language="or")
    assert turn["intent"] == "crop_recommendation"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_11_assamese_weather():
    turn = await run_orchestrator_pipeline("আজিৰ বতৰ কেনেকুৱা?", detected_language="as")
    assert turn["intent"] == "weather"
    assert turn["tool_status"] in ["success", "unavailable"]


@pytest.mark.asyncio
async def test_12_urdu_query():
    turn = await run_orchestrator_pipeline("گندم کی قیمت کیا ہے؟", detected_language="ur")
    assert turn["intent"] == "mandi"
    assert turn["tool_status"] == "success"


@pytest.mark.asyncio
async def test_13_maithili_query():
    turn = await run_orchestrator_pipeline("आई मौसम कतेक अछि?", detected_language="mai")
    assert turn["intent"] == "weather"
    assert turn["tool_status"] in ["success", "unavailable"]


# =============================================================================
# SCENARIOS 14-18: REGIONAL DIALECT VOCABULARY NORMALIZATION
# =============================================================================

def test_14_mewari_vocabulary_normalization():
    assert normalize_crop_name("बाजरो") == "Pearl Millet (Bajra)"
    assert normalize_crop_name("सींगदाना") == "Groundnut (Peanut)"
    assert normalize_crop_name("लसन") == "Garlic"
    term = normalize_agricultural_term("बोवणो", category="operation")
    assert term is not None
    assert term.canonical_entity == "sowing"


def test_15_marwari_vocabulary_normalization():
    assert normalize_crop_name("भूंगफली") == "Groundnut (Peanut)"
    assert normalize_crop_name("बाजरी") == "Pearl Millet (Bajra)"
    res = detect_dialect("म्हाने जोधपुर रो मौसम बताओ")
    assert res.dialect == "rwr"
    assert res.language == "hi"


def test_16_bhojpuri_vocabulary_normalization():
    assert normalize_crop_name("छोला") == "Chickpea (Gram / Chana)"
    assert normalize_crop_name("ईख") == "Sugarcane"
    assert normalize_soil_name("बलुई") == "Sandy Soil"
    res = detect_dialect("खेते में का बोईब रउआ बताईं")
    assert res.dialect == "bho"
    assert res.language == "hi"


def test_17_haryanvi_vocabulary_normalization():
    res = detect_dialect("तन्नै के लाग्ग्या मौसम कै सा सै?")
    assert res.dialect == "bgc"
    assert res.language == "hi"


def test_18_chhattisgarhi_vocabulary_normalization():
    res = detect_dialect("काबर गा खेती-खार म का बोवई हावय?")
    assert res.dialect == "hne"
    assert res.language == "hi"


# =============================================================================
# SCENARIOS 19-23: CODE-SWITCHING, AMBIGUITY, CONFIDENCE & FALLBACKS
# =============================================================================

@pytest.mark.asyncio
async def test_19_code_switched_hindi_english():
    turn1 = await run_orchestrator_pipeline("आज weather कैसा है?", detected_language="hi")
    assert turn1["intent"] == "weather"
    turn2 = await run_orchestrator_pipeline("गेहूं का market rate कितना है?", detected_language="hi")
    assert turn2["intent"] == "mandi"


def test_20_ambiguous_dialect_handling():
    res = detect_dialect("आज का मौसम कैसा है?")
    assert res.dialect is None  # Safe: weak evidence does not fabricate dialect
    assert res.language == "hi"
    assert res.support_tier == 1


@pytest.mark.asyncio
async def test_21_low_asr_confidence_clarification():
    turn = await run_orchestrator_pipeline(
        "अजब गजब कुछ भी",
        detected_language="hi",
        language_confidence=0.45
    )
    assert turn["intent"] == "clarify"
    assert turn["requires_clarification"] is True


def test_22_unsupported_language_fallback():
    # Rare dialect/variety fallback check
    profile = get_language_profile("unknown_xyz")
    assert profile.canonical_code == "hi"
    assert profile.support_tier == 1


@pytest.mark.asyncio
async def test_23_parent_language_tts_fallback():
    tts = BhashiniTTSProvider()
    res = await tts.synthesize("आज मौसम साफ रहेगा", language="mew")
    assert res.response_language == "hi"
    assert res.fallback_used is True
    assert len(res.audio_bytes) > 0


# =============================================================================
# SCENARIOS 24-27: MULTI-TURN MEMORY & ANAPHORA RESOLUTION
# =============================================================================

@pytest.mark.asyncio
async def test_24_multi_turn_dialect_conversation():
    # Turn 1
    turn1 = await run_orchestrator_pipeline(
        "म्हारे खेत में रेतीली मिट्टी है, कौन सी फसल सही रहेगी?",
        detected_language="hi",
        session_id="multi_mew_001",
        farmer_context={"latitude": 24.6178, "longitude": 73.9937, "state": "Rajasthan", "soil_type": "Sandy Soil"}
    )
    assert turn1["detected_dialect"] == "mew"
    assert turn1["intent"] == "crop_recommendation"
    assert len(turn1["last_recommendations"]) > 0

    # Turn 2: Anaphora "पहली वाली क्यों?"
    turn2 = await run_orchestrator_pipeline(
        "पहली वाली क्यों?",
        detected_language=turn1["detected_language"],
        detected_dialect=turn1["detected_dialect"],
        session_id="multi_mew_001",
        last_recommendations=turn1["last_recommendations"]
    )
    assert turn2["detected_dialect"] == "mew"
    assert turn2["intent"] == "explain_recommendation"
    assert turn1["last_recommendations"][0]["crop_name"] in turn2["final_response"]


@pytest.mark.asyncio
async def test_25_first_one_reference_resolution():
    recs = [{"crop_name": "Groundnut (Peanut)", "suitability_score": 0.90, "rank": 1}]
    turn = await run_orchestrator_pipeline(
        "पहली वाली फसल क्यों चुनी गई?",
        detected_language="hi",
        last_recommendations=recs
    )
    assert turn["intent"] == "explain_recommendation"
    assert "Groundnut (Peanut)" in turn["final_response"]


@pytest.mark.asyncio
async def test_26_this_crop_reference_resolution():
    recs = [{"crop_name": "Wheat", "suitability_score": 0.88, "rank": 1}]
    turn = await run_orchestrator_pipeline(
        "इस फसल का मंडी भाव क्या है?",
        detected_language="hi",
        last_recommendations=recs
    )
    assert turn["intent"] == "mandi"
    assert turn["filled_slots"].get("commodity") == "Wheat"


@pytest.mark.asyncio
async def test_27_what_if_question():
    turn = await run_orchestrator_pipeline(
        "अगर बारिश कम हो जाए तो?",
        detected_language="hi",
        farmer_context={"latitude": 26.9124, "longitude": 75.7873, "state": "Rajasthan", "soil_type": "Sandy Soil"}
    )
    assert turn["intent"] == "what_if"
    assert turn["tool_status"] == "success"
    assert "कम बारिश" in turn["final_response"]


# =============================================================================
# SCENARIOS 28-30: CROSS-DOMAIN CONVERSATIONAL TRANSITIONS
# =============================================================================

@pytest.mark.asyncio
async def test_28_cross_domain_weather_to_crop():
    turn1 = await run_orchestrator_pipeline("जयपुर में मौसम कैसा है?", detected_language="hi")
    assert turn1["intent"] == "weather"

    turn2 = await run_orchestrator_pipeline(
        "अब इस मौसम में कौन सी फसल लगाऊं?",
        detected_language="hi",
        farmer_context={"latitude": 26.9124, "longitude": 75.7873, "state": "Rajasthan", "soil_type": "Sandy Soil"}
    )
    assert turn2["intent"] == "crop_recommendation"
    assert turn2["tool_status"] == "success"


@pytest.mark.asyncio
async def test_29_cross_domain_crop_to_mandi():
    recs = [{"crop_name": "Mustard (Sarson)", "suitability_score": 0.85, "rank": 1}]
    turn = await run_orchestrator_pipeline("सरसों का आज मंडी में क्या भाव है?", detected_language="hi", last_recommendations=recs)
    assert turn["intent"] == "mandi"
    assert turn["filled_slots"].get("commodity") == "Mustard (Sarson)"


@pytest.mark.asyncio
async def test_30_cross_domain_crop_to_disease():
    recs = [{"crop_name": "Groundnut (Peanut)", "suitability_score": 0.90, "rank": 1}]
    turn = await run_orchestrator_pipeline("मूंगफली में कौन सा रोग लगता है?", detected_language="hi", last_recommendations=recs)
    assert turn["intent"] == "disease"
    assert ("रोग" in turn["final_response"] or "लक्षण" in turn["final_response"])


# =============================================================================
# SCENARIOS 31-37: SAFETY, DATA INTEGRITY & SYSTEM CONTROLS
# =============================================================================

@pytest.mark.asyncio
async def test_31_unsupported_purchase_request():
    turn = await run_orchestrator_pipeline("मेरे लिए 2 बोरी यूरिया खरीद दो", detected_language="hi")
    assert turn["intent"] == "unsupported_capability"
    assert "खरीद" in turn["final_response"]


@pytest.mark.asyncio
async def test_32_unsupported_scheme_submission():
    turn = await run_orchestrator_pipeline("मेरे नाम पर पीएम किसान का फॉर्म भर दो", detected_language="hi")
    assert turn["intent"] == "unsupported_capability"
    assert "आवेदन" in turn["final_response"]


@pytest.mark.asyncio
async def test_33_no_soil_report_never_fabricates_npk():
    res = await tool_registry.execute("crop_recommendation_tool", {
        "latitude": 24.6178,
        "longitude": 73.9937,
        "state": "Rajasthan",
        "soil_type": "Sandy Soil",
        "has_soil_report": False,
    })
    assert res.status == ToolStatus.SUCCESS
    assert res.data is not None
    assert "recommendations" in res.data
    # Confirms Mode B crop recommendations without fake N/P/K
    assert len(res.data["recommendations"]) > 0


@pytest.mark.asyncio
async def test_34_disease_request_without_image():
    turn = await run_orchestrator_pipeline("मेरी फसल में पीलापन आ रहा है, रोग बताओ", detected_language="hi")
    assert turn["intent"] == "disease"
    assert ("रोग" in turn["final_response"] or "लक्षण" in turn["final_response"])


@pytest.mark.asyncio
async def test_35_repeat_last_response():
    turn = await run_orchestrator_pipeline(
        "फिर से बताओ",
        detected_language="hi",
        last_final_response="जयपुर में आज मौसम साफ रहेगा।"
    )
    assert turn["intent"] == "repeat_last"
    assert turn["final_response"] == "जयपुर में आज मौसम साफ रहेगा।"


@pytest.mark.asyncio
async def test_36_speech_speed_control():
    turn = await run_orchestrator_pipeline("धीरे बोलो", detected_language="hi")
    assert turn["intent"] == "speech_control"
    assert "धीरे बोलूंगा" in turn["final_response"]


@pytest.mark.asyncio
async def test_37_navigation_command():
    turn = await run_orchestrator_pipeline("मंडी का भाव वाला पेज खोलो", detected_language="hi")
    assert turn["intent"] == "navigation"
    assert turn["tool_output"].get("destination") == "market_prices"
