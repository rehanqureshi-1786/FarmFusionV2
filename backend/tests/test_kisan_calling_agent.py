"""
Unit and integration tests for FarmFusion Kisan Voice Calling Agent.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.calling_agent.prompts import get_kisan_call_prompt, get_initial_kisan_greeting
from app.calling_agent.service import kisan_calling_service
from app.schemas.calling import KisanCallRequest

@pytest.mark.asyncio
async def test_01_kisan_call_prompts_and_greetings():
    prompt_mandi = get_kisan_call_prompt(
        farmer_name="Ramesh",
        call_type="mandi_price_alert",
        language="hi",
        location="Udaipur",
        crop_name="Wheat",
        mandi_name="Udaipur Mandi",
        current_price=2650.0,
        target_price=2600.0
    )
    assert "Ramesh" in prompt_mandi
    assert "Udaipur Mandi" in prompt_mandi
    assert "2650" in prompt_mandi
    assert "Kisan Mitra" in prompt_mandi

    greeting = get_initial_kisan_greeting(
        farmer_name="Ramesh",
        call_type="mandi_price_alert",
        language="hi",
        crop_name="Wheat",
        mandi_name="Udaipur Mandi",
        current_price=2650.0
    )
    assert "नमस्ते Ramesh जी" in greeting
    assert "2650" in greeting

@pytest.mark.asyncio
async def test_02_kisan_calling_service_trigger():
    req = KisanCallRequest(
        phone="+919876543210",
        farmer_name="Ramesh",
        call_type="mandi_price_alert",
        language="hi",
        crop_name="Wheat",
        mandi_name="Udaipur",
        current_price=2650.0
    )
    res = await kisan_calling_service.trigger_call(req)
    assert res.status == "initiated"
    assert res.phone == "+919876543210"
    assert res.farmer_name == "Ramesh"
    assert res.call_id in kisan_calling_service.active_calls

@pytest.mark.asyncio
async def test_03_calling_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger call endpoint
        res = await client.post("/api/v1/calling/call", json={
            "phone": "+919876543210",
            "farmer_name": "Suresh",
            "call_type": "weather_warning",
            "language": "hi",
            "location": "Jaipur",
            "weather_summary": "Heavy rainfall expected tomorrow"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["farmer_name"] == "Suresh"
        assert data["status"] == "initiated"

        # 2. Trigger mandi alert convenience endpoint
        res2 = await client.post("/api/v1/calling/trigger-mandi-alert", params={
            "phone": "+919876543210",
            "farmer_name": "Ramesh",
            "crop_name": "Mustard",
            "mandi_name": "Kota",
            "current_price": 5800.0,
            "target_price": 5700.0,
            "language": "hi"
        })
        assert res2.status_code == 200
        assert res2.json()["call_type"] == "mandi_price_alert"

        # 3. Inbound telephony webhook
        res3 = await client.post("/api/v1/calling/webhook/inbound?farmer_name=Ramesh&call_type=mandi_price_alert")
        assert res3.status_code == 200
        assert "application/xml" in res3.headers["content-type"]
        assert "Connecting to Kisan Mitra" in res3.text
        assert "Stream" in res3.text
