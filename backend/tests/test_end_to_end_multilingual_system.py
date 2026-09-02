"""
End-to-End Multilingual System Tests for FarmFusion.
Verifies language propagation across:
1. Canonical 38-Language & Dialect Registry Resolution
2. Mandi Market Intelligence Sell/Wait Advisory (Hindi, Gujarati, Marathi, Punjabi, Bengali, English)
3. Weather Agent Conditions & Actionable Farming Advice
4. Crop Recommendation Environmental Suitability Narratives
5. Kisan Calling Agent Prompts & Spoken Greetings
6. Animal Intrusion / IoT Alert Narratives
7. Invariance & Integrity of Structured Numeric Data (Prices, Temps, Rainfall, Coordinates)
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.language import resolve_language_code, set_current_language, get_current_language
from app.voice.languages import LANGUAGE_REGISTRY
from app.services.mandi_intelligence import MandiIntelligenceService
from app.agents.weather_agent import weather_agent
from app.services.no_soil_crop_service import no_soil_crop_service
from app.schemas.crop_recommendation import NoSoilReportRequest
from app.calling_agent.prompts import get_kisan_call_prompt, get_initial_kisan_greeting
from app.core.localization import ANIMAL_ALERT_MESSAGES, localize_text

# =============================================================================
# 1. CANONICAL 38-LANGUAGE REGISTRY & RESOLUTION TEST
# =============================================================================

def test_01_all_38_languages_and_dialects_resolve_correctly():
    assert len(LANGUAGE_REGISTRY) >= 38

    # Test Scheduled Languages
    scheduled = ["hi", "en", "gu", "mr", "pa", "bn", "ta", "te", "kn", "ml", "or", "as", "ur", "mai"]
    for code in scheduled:
        ctx = resolve_language_code(code)
        assert ctx.canonical_code == code
        assert not ctx.is_dialect

    # Test Regional Dialects (Resolves to appropriate parent language with dialect metadata preserved)
    dialects = {
        "mew": "hi",  # Mewari -> Hindi
        "rwr": "hi",  # Marwari -> Hindi
        "dhu": "hi",  # Dhundhari -> Hindi
        "har": "hi",  # Harauti -> Hindi
        "bho": "hi",  # Bhojpuri -> Hindi
        "awa": "hi",  # Awadhi -> Hindi
        "mup": "pa",  # Malwai -> Punjabi
        "vah": "mr",  # Varhadi -> Marathi
        "kat": "gu"   # Kathiawari -> Gujarati
    }
    for dialect_code, expected_parent in dialects.items():
        ctx = resolve_language_code(dialect_code)
        assert ctx.canonical_code == expected_parent
        assert ctx.is_dialect
        assert ctx.parent_language == expected_parent

    # Test Unknown Code Fallback -> Deterministic Hindi
    unknown_ctx = resolve_language_code("xyz_unknown")
    assert unknown_ctx.canonical_code == "hi"

# =============================================================================
# 2. MANDI AGENT MULTILINGUAL LOCALIZATION & NUMERIC INTEGRITY
# =============================================================================

@pytest.mark.asyncio
async def test_02_mandi_sell_wait_advisory_multilingual():
    # 1. Hindi
    adv_hi = await MandiIntelligenceService.get_sell_wait_advisory("Wheat", "Jaipur Mandi", days=7, language="hi")
    assert adv_hi.language == "hi"
    assert adv_hi.observed.price > 0
    assert "₹" in adv_hi.advisory.recommendation_hi
    assert adv_hi.advisory.localized_recommendation is not None

    # 2. Gujarati
    adv_gu = await MandiIntelligenceService.get_sell_wait_advisory("Wheat", "Jaipur Mandi", days=7, language="gu")
    assert adv_gu.language == "gu"
    assert adv_gu.observed.price == adv_hi.observed.price  # Numeric price remains strictly identical!
    assert "ભાવ" in adv_gu.advisory.localized_recommendation or "વેચ" in adv_gu.advisory.localized_recommendation or "મંડી" in adv_gu.advisory.localized_recommendation

    # 3. Marathi
    adv_mr = await MandiIntelligenceService.get_sell_wait_advisory("Wheat", "Jaipur Mandi", days=7, language="mr")
    assert adv_mr.language == "mr"
    assert adv_mr.observed.price == adv_hi.observed.price  # Numbers invariant
    assert "दर" in adv_mr.advisory.localized_recommendation or "विक" in adv_mr.advisory.localized_recommendation or "बाजार" in adv_mr.advisory.localized_recommendation

    # 4. Punjabi
    adv_pa = await MandiIntelligenceService.get_sell_wait_advisory("Wheat", "Jaipur Mandi", days=7, language="pa")
    assert adv_pa.language == "pa"
    assert adv_pa.observed.price == adv_hi.observed.price

    # 5. Bengali
    adv_bn = await MandiIntelligenceService.get_sell_wait_advisory("Wheat", "Jaipur Mandi", days=7, language="bn")
    assert adv_bn.language == "bn"
    assert adv_bn.observed.price == adv_hi.observed.price

# =============================================================================
# 3. WEATHER AGENT MULTILINGUAL LOCALIZATION
# =============================================================================

def test_03_weather_agent_multilingual():
    # Test weather text conditions
    cond_hi = weather_agent._weather_code_to_text(0, language="hi")
    cond_gu = weather_agent._weather_code_to_text(0, language="gu")
    cond_mr = weather_agent._weather_code_to_text(0, language="mr")
    cond_pa = weather_agent._weather_code_to_text(0, language="pa")
    cond_bn = weather_agent._weather_code_to_text(0, language="bn")
    cond_en = weather_agent._weather_code_to_text(0, language="en")

    assert cond_hi == "साफ आसमान"
    assert cond_gu == "સ્વચ્છ આકાશ"
    assert cond_mr == "निरभ्र आकाश"
    assert cond_pa == "ਸਾਫ ਅਸਮਾਨ"
    assert cond_bn == "পরিষ্কার আকাশ"
    assert cond_en == "clear sky"

    # Test farming advice localization
    adv_hi = weather_agent._generate_farming_advice(temperature_c=38.0, humidity_percent=90.0, wind_speed_kmh=10.0, weather_code=0, language="hi")
    adv_gu = weather_agent._generate_farming_advice(temperature_c=38.0, humidity_percent=90.0, wind_speed_kmh=10.0, weather_code=0, language="gu")
    adv_mr = weather_agent._generate_farming_advice(temperature_c=38.0, humidity_percent=90.0, wind_speed_kmh=10.0, weather_code=0, language="mr")
    adv_pa = weather_agent._generate_farming_advice(temperature_c=38.0, humidity_percent=90.0, wind_speed_kmh=10.0, weather_code=0, language="pa")
    adv_bn = weather_agent._generate_farming_advice(temperature_c=38.0, humidity_percent=90.0, wind_speed_kmh=10.0, weather_code=0, language="bn")

    assert "सिंचाई" in adv_hi or "नमी" in adv_hi
    assert "પિયત" in adv_gu or "ભેજ" in adv_gu
    assert "पाणी" in adv_mr or "ओलावा" in adv_mr
    assert "ਸਿੰਚਾਈ" in adv_pa or "ਨਮੀ" in adv_pa
    assert "সেচ" in adv_bn or "আর্দ্রতা" in adv_bn

# =============================================================================
# 4. CROP RECOMMENDATION MULTILINGUAL NARRATIVES
# =============================================================================

@pytest.mark.asyncio
async def test_04_crop_recommendation_multilingual():
    req = NoSoilReportRequest(
        latitude=26.9124,
        longitude=75.7873,
        state="Rajasthan",
        district="Jaipur"
    )

    # Set context language to Gujarati
    set_current_language("gu")
    res_gu = await no_soil_crop_service.recommend(req)
    assert res_gu.success
    assert "જીપીએસ" in res_gu.message or "હવામાન" in res_gu.message or "વાસ્તવિક" in res_gu.explanation

    # Set context language to Marathi
    set_current_language("mr")
    res_mr = await no_soil_crop_service.recommend(req)
    assert res_mr.success
    assert "जीपीएस" in res_mr.message or "हवामान" in res_mr.message or "स्थान" in res_mr.explanation

    # Set context language to Hindi
    set_current_language("hi")
    res_hi = await no_soil_crop_service.recommend(req)
    assert res_hi.success
    assert "जीपीएस" in res_hi.message or "मौसम" in res_hi.message

# =============================================================================
# 5. CALLING AGENT MULTILINGUAL PROMPTS & GREETINGS
# =============================================================================

def test_05_calling_agent_multilingual():
    # 1. Hindi Greeting
    greet_hi = get_initial_kisan_greeting("सुरेश", "mandi_price_alert", language="hi", crop_name="सरसों", mandi_name="कोटा", current_price=5800.0)
    assert "नमस्ते सुरेश जी" in greet_hi
    assert "5800" in greet_hi

    # 2. Gujarati Prompt & Greeting
    prompt_gu = get_kisan_call_prompt(farmer_name="રમેશ", call_type="mandi_price_alert", language="gu", crop_name="કપાસ", mandi_name="રાજકોટ", current_price=7200.0)
    assert "Gujarati" in prompt_gu
    assert "રમેશ" in prompt_gu
    assert "7200" in prompt_gu

    # 3. Marathi Prompt & Greeting
    prompt_mr = get_kisan_call_prompt(farmer_name="गणेश", call_type="weather_warning", language="mr", location="पुणे")
    assert "Marathi" in prompt_mr
    assert "गणेश" in prompt_mr

# =============================================================================
# 6. IOT / ANIMAL DETECTION MULTILINGUAL ALERTS
# =============================================================================

def test_06_iot_animal_detection_multilingual():
    alert_hi = localize_text(ANIMAL_ALERT_MESSAGES, "wild_boar", language="hi")
    alert_gu = localize_text(ANIMAL_ALERT_MESSAGES, "wild_boar", language="gu")
    alert_mr = localize_text(ANIMAL_ALERT_MESSAGES, "wild_boar", language="mr")
    alert_pa = localize_text(ANIMAL_ALERT_MESSAGES, "wild_boar", language="pa")
    alert_bn = localize_text(ANIMAL_ALERT_MESSAGES, "wild_boar", language="bn")

    assert "जंगली सूअर" in alert_hi
    assert "જંગલી ભૂંડ" in alert_gu
    assert "रानडुकराची" in alert_mr
    assert "ਜੰਗਲੀ ਸੂਰ" in alert_pa
    assert "বুনো শুয়োর" in alert_bn

# =============================================================================
# 7. FASTAPI HTTP HEADERS END-TO-END PROPAGATION
# =============================================================================

@pytest.mark.asyncio
async def test_07_http_requests_propagate_language_headers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Request with Gujarati header
        res_gu = await client.get("/api/v1/market/advisory?commodity=Wheat&market=Jaipur%20Mandi", headers={"Accept-Language": "gu"})
        assert res_gu.status_code == 200
        data_gu = res_gu.json()
        assert data_gu["language"] == "gu"
        assert res_gu.headers.get("x-resolved-language") == "gu"

        # Request with Marathi header
        res_mr = await client.get("/api/v1/market/advisory?commodity=Wheat&market=Jaipur%20Mandi", headers={"Accept-Language": "mr"})
        assert res_mr.status_code == 200
        data_mr = res_mr.json()
        assert data_mr["language"] == "mr"
        assert res_mr.headers.get("x-resolved-language") == "mr"

        # Request with Weather and Punjabi header
        res_pa = await client.get("/api/v1/weather/current?lat=26.9124&lon=75.7873", headers={"Accept-Language": "pa"})
        assert res_pa.status_code == 200
        data_pa = res_pa.json()["data"]
        assert data_pa["language"] == "pa"
        assert res_pa.headers.get("x-resolved-language") == "pa"
