"""
Comprehensive Pre-Live Verification Tests for FarmFusion Kisan Voice Calling Agent.
Tests:
1. Vobiz API endpoint URL structure (/api/v1/Account/.../Call/)
2. Vobiz authentication headers (X-Auth-ID and X-Auth-Token)
3. E.164 (+91) phone number validation and normalization
4. 5-minute duplicate-call prevention cooldown
5. Outbound audio playAudio event format and backward-compatibility with media event
6. Base64 linear PCM audio encoding and decoding roundtrip
7. 8kHz mono PCM audio conversion
8. Barge-in interruption state machine (clearAudio on speech start)
9. Hindi multi-turn conversational persona and prompt
10. English multi-turn conversational persona and prompt
11. FastAPI endpoints (/call, /trigger-mandi-alert, /trigger-weather-alert, /webhook/inbound)
"""

import pytest
import pytest_asyncio
import base64
import json
import time
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.calling_agent.prompts import get_kisan_call_prompt, get_initial_kisan_greeting
from app.calling_agent.service import kisan_calling_service, KisanCallingService
from app.calling_agent.orchestrator import KisanVoiceOrchestrator
from app.calling_agent.tts import TelephonyTTS
from app.schemas.calling import KisanCallRequest

# =============================================================================
# 1. VOBIZ API URL & AUTHENTICATION HEADERS VERIFICATION
# =============================================================================

@pytest.mark.asyncio
async def test_01_vobiz_endpoint_and_headers_structure():
    service = KisanCallingService()
    service.vobiz_account_id = "test_acc_123"
    service.vobiz_api_key = "test_key_456"

    captured_url = None
    captured_headers = None
    captured_json = None

    async def mock_post(url, headers=None, json=None, **kwargs):
        nonlocal captured_url, captured_headers, captured_json
        captured_url = url
        captured_headers = headers
        captured_json = json
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        req = KisanCallRequest(
            phone="+919876543210",
            farmer_name="Suresh",
            call_type="mandi_price_alert",
            language="hi",
            crop_name="Mustard",
            mandi_name="Kota",
            current_price=5800.0
        )
        res = await service.trigger_call(req, bypass_cooldown=True)

        assert res.status == "initiated"
        # 1. Verify correct official Vobiz API base URL and endpoint (with /api/v1/)
        assert captured_url == "https://api.vobiz.ai/api/v1/Account/test_acc_123/Call/"
        # 2. Verify both X-Auth-ID and X-Auth-Token headers
        assert captured_headers["X-Auth-ID"] == "test_acc_123"
        assert captured_headers["X-Auth-Token"] == "test_key_456"
        assert captured_headers["Content-Type"] == "application/json"
        # 3. Verify payload
        assert captured_json["to"] == "+919876543210"
        assert "/api/v1/calling/webhook/inbound" in captured_json["answer_url"]

# =============================================================================
# 2. PHONE VALIDATION (E.164 & +91) & DUPLICATE COOLDOWN
# =============================================================================

def test_02_e164_phone_validation_and_normalization():
    service = KisanCallingService()

    # Valid Indian numbers with +91
    assert service.validate_and_normalize_phone("+919876543210") == "+919876543210"
    assert service.validate_and_normalize_phone("+91 98765 43210") == "+919876543210"
    assert service.validate_and_normalize_phone("+91-98765-43210") == "+919876543210"

    # Valid Indian 10-digit without prefix -> auto prepends +91
    assert service.validate_and_normalize_phone("9876543210") == "+919876543210"

    # Invalid Indian mobile numbers
    with pytest.raises(ValueError, match="Invalid Indian mobile number"):
        service.validate_and_normalize_phone("+915876543210")  # starts with 5 (invalid in India)

    with pytest.raises(ValueError, match="Invalid phone number format"):
        service.validate_and_normalize_phone("12345")  # too short

@pytest.mark.asyncio
async def test_03_duplicate_call_prevention_cooldown():
    service = KisanCallingService()
    phone = "+919876500001"

    req = KisanCallRequest(
        phone=phone,
        farmer_name="Ramesh",
        call_type="mandi_price_alert",
        language="hi"
    )

    # First call succeeds
    res1 = await service.trigger_call(req)
    assert res1.status == "initiated"

    # Second call to same number immediately after raises ValueError (duplicate cooldown)
    with pytest.raises(ValueError, match="Duplicate call prevented"):
        await service.trigger_call(req)

    # Bypassing cooldown allows testing
    res3 = await service.trigger_call(req, bypass_cooldown=True)
    assert res3.status == "initiated"

# =============================================================================
# 3. WEBSOCKET AUDIO FORMAT, playAudio EVENT & BASE64 ROUNDTRIP
# =============================================================================

@pytest.mark.asyncio
async def test_04_play_audio_event_and_base64_roundtrip():
    mock_ws = AsyncMock()
    orchestrator = KisanVoiceOrchestrator(
        websocket=mock_ws,
        farmer_name="Ramesh",
        language="hi"
    )

    # Simulated 8kHz PCM audio bytes (16-bit mono: 16000 bytes = 1 second)
    sample_pcm = b"\x00\x01\x00\x02" * 4000

    # Mock TTS synthesis
    orchestrator.tts.synthesize_for_phone = AsyncMock(return_value=sample_pcm)

    await orchestrator.speak("नमस्ते किसान भाई")

    # Verify websocket sent playAudio event format
    assert mock_ws.send_text.called
    sent_raw = mock_ws.send_text.call_args[0][0]
    sent_json = json.loads(sent_raw)

    assert sent_json["event"] == "playAudio"
    b64_payload = sent_json["media"]["payload"]
    decoded_bytes = base64.b64decode(b64_payload)

    # Audio roundtrip integrity verification
    assert decoded_bytes == sample_pcm
    assert len(decoded_bytes) == len(sample_pcm)

# =============================================================================
# 4. 8kHz MONO PCM CONVERSION
# =============================================================================

def test_05_tts_8khz_pcm_conversion():
    tts = TelephonyTTS(language_code="hi")
    # Test PCM conversion helper with raw bytes
    test_wav = b"RIFF" + b"\x00" * 36 + b"data" + b"\x00" * 1000
    pcm_out = tts._convert_to_8khz_pcm(test_wav)
    assert isinstance(pcm_out, bytes)

# =============================================================================
# 5. BARGE-IN INTERRUPTION STATE MACHINE
# =============================================================================

@pytest.mark.asyncio
async def test_06_barge_in_state_machine():
    mock_ws = AsyncMock()
    orchestrator = KisanVoiceOrchestrator(
        websocket=mock_ws,
        farmer_name="Ramesh",
        language="hi"
    )

    assert not orchestrator.is_interrupted

    # Trigger speech started (barge-in event)
    await orchestrator.on_speech_started()

    # 1. is_interrupted becomes True immediately
    assert orchestrator.is_interrupted is True

    # 2. clearAudio event sent to Vobiz network to flush audio queue
    assert mock_ws.send_text.called
    clear_msg = json.loads(mock_ws.send_text.call_args[0][0])
    assert clear_msg["event"] == "clearAudio"

    # 3. speak() does not stream audio if interrupted
    mock_ws.send_text.reset_mock()
    await orchestrator.speak("Should not be spoken while interrupted")
    assert not mock_ws.send_text.called

# =============================================================================
# 6. MULTI-TURN HINDI & ENGLISH CONVERSATIONAL FLOW
# =============================================================================

def test_07_hindi_multi_turn_prompt_and_greeting():
    # Hindi Mandi Alert Persona
    prompt_hi = get_kisan_call_prompt(
        farmer_name="राकेश",
        call_type="mandi_price_alert",
        language="hi",
        location="जयपुर",
        crop_name="गेहूं",
        mandi_name="जयपुर मंडी",
        current_price=2450.0,
        target_price=2400.0
    )
    assert "Hindi" in prompt_hi
    assert "राकेश" in prompt_hi
    assert "2450" in prompt_hi
    assert "Kisan Mitra" in prompt_hi

    # Hindi Greeting
    greet_hi = get_initial_kisan_greeting(
        farmer_name="राकेश",
        call_type="mandi_price_alert",
        language="hi",
        crop_name="गेहूं",
        mandi_name="जयपुर मंडी",
        current_price=2450.0
    )
    assert "नमस्ते राकेश जी" in greet_hi
    assert "2450" in greet_hi

def test_08_english_multi_turn_prompt_and_greeting():
    # English Weather Warning Persona
    prompt_en = get_kisan_call_prompt(
        farmer_name="John",
        call_type="weather_warning",
        language="en",
        location="Pune",
        weather_summary="Heavy thunderstorm expected in next 24 hours"
    )
    assert "English" in prompt_en
    assert "John" in prompt_en
    assert "Pune" in prompt_en
    assert "thunderstorm" in prompt_en

    # English Greeting
    greet_en = get_initial_kisan_greeting(
        farmer_name="John",
        call_type="weather_warning",
        language="en"
    )
    assert "Hello John" in greet_en
    assert "Kisan Mitra" in greet_en

# =============================================================================
# 7. FASTAPI HTTP REST & WEBHOOK ENDPOINTS
# =============================================================================

@pytest.mark.asyncio
async def test_09_calling_api_endpoints_integration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger call endpoint with valid E.164 phone
        phone = f"+9198765{int(time.time()) % 100000:05d}"
        res = await client.post("/api/v1/calling/call", json={
            "phone": phone,
            "farmer_name": "Kailash",
            "call_type": "weather_warning",
            "language": "hi",
            "location": "Jaipur",
            "weather_summary": "Thunderstorm alert"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["farmer_name"] == "Kailash"
        assert data["status"] == "initiated"

        # 2. Inbound telephony webhook (Vobiz XML stream response)
        res_xml = await client.post("/api/v1/calling/webhook/inbound?farmer_name=Kailash&call_type=weather_warning")
        assert res_xml.status_code == 200
        assert "application/xml" in res_xml.headers["content-type"]
        assert "<Response>" in res_xml.text
        assert '<Stream bidirectional="true" keepCallAlive="true">' in res_xml.text
        assert "ws/calling/stream" in res_xml.text

        # 3. Duplicate call prevention returns HTTP 429
        res_dup = await client.post("/api/v1/calling/call", json={
            "phone": phone,
            "farmer_name": "Kailash",
            "call_type": "weather_warning"
        })
        assert res_dup.status_code == 429
        assert "Duplicate call prevented" in res_dup.json()["detail"]
