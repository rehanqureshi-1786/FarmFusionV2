"""
API Integration Tests for Local Voice Agent Endpoints in FarmFusion.
Validates:
- GET /api/v1/voice/local/status
- GET /api/v1/voice/local/language-packs
- POST /api/v1/voice/local/mode
- POST /api/v1/voice/local/query
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_get_local_voice_status_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/voice/local/status")
        assert response.status_code == 200
        data = response.json()
        assert "runtime_mode" in data
        assert "device_tier" in data
        assert "engines" in data
        assert "registered_models" in data
        assert data["engines"]["nlu"]["is_available"] is True


@pytest.mark.asyncio
async def test_get_local_language_packs_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/voice/local/language-packs")
        assert response.status_code == 200
        data = response.json()
        assert data["total_packs"] >= 15
        pack_languages = [p["language"] for p in data["packs"]]
        assert "hi" in pack_languages
        assert "gu" in pack_languages


@pytest.mark.asyncio
async def test_set_voice_runtime_mode_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Valid switch
        resp = await client.post("/api/v1/voice/local/mode", json={"mode": "offline"})
        assert resp.status_code == 200
        assert resp.json()["current_mode"] == "offline"

        # Invalid mode
        bad_resp = await client.post("/api/v1/voice/local/mode", json={"mode": "INVALID"})
        assert bad_resp.status_code == 400

        # Switch back to hybrid
        resp = await client.post("/api/v1/voice/local/mode", json={"mode": "hybrid"})
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_process_local_voice_query_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/voice/local/query",
            json={
                "query": "म्हाने बाजरी रो भाव बताओ",
                "language_hint": "hi"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "mandi"
        assert any(w in data["response_text"] for w in ["भाव", "दाम", "बाजार", "₹", "प्रति क्विंटल", "मंडी"])
        assert data["runtime_mode"] in ["hybrid", "offline", "online"]
