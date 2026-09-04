"""
Test suite for PlantGatekeeperService and Non-Plant Rejection.
Verifies that everyday objects (computer mouse, keyboards, desk surfaces) are rejected
with 'No Plant Detected', while real plant/crop leaves are confirmed for diagnosis.
"""
import io
import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.plant_gatekeeper_service import PlantGatekeeperService
from app.services.disease_service import DiseaseService


def test_plant_gatekeeper_rejects_neutral_desk():
    """Verify white/gray desk image is rejected as non-plant."""
    desk = Image.new("RGB", (300, 300), color=(235, 235, 235))
    buf = io.BytesIO()
    desk.save(buf, format="JPEG")
    res = PlantGatekeeperService.verify_plant(buf.getvalue())
    assert res["is_plant"] is False
    assert "No plant" in res["reason"] or "Non-plant" in res["reason"]


def test_plant_gatekeeper_rejects_keyboard():
    """Verify dark keyboard image is rejected as non-plant."""
    keyboard = Image.new("RGB", (300, 300), color=(28, 28, 30))
    buf = io.BytesIO()
    keyboard.save(buf, format="JPEG")
    res = PlantGatekeeperService.verify_plant(buf.getvalue())
    assert res["is_plant"] is False


def test_plant_gatekeeper_accepts_green_leaf():
    """Verify green foliage is confirmed as a plant."""
    leaf = Image.new("RGB", (300, 300), color=(40, 140, 45))
    buf = io.BytesIO()
    leaf.save(buf, format="JPEG")
    res = PlantGatekeeperService.verify_plant(buf.getvalue())
    assert res["is_plant"] is True
    assert res["confidence"] > 0.5


def test_plant_gatekeeper_accepts_yellow_leaf():
    """Verify yellowed/chlorosis plant foliage is confirmed as a plant."""
    leaf = Image.new("RGB", (300, 300), color=(175, 160, 45))
    buf = io.BytesIO()
    leaf.save(buf, format="JPEG")
    res = PlantGatekeeperService.verify_plant(buf.getvalue())
    assert res["is_plant"] is True


@pytest.mark.asyncio
async def test_disease_detect_rejects_non_plant_with_proper_contract():
    """Verify end-to-end detect_disease contract when non-plant is supplied."""
    desk = Image.new("RGB", (300, 300), color=(220, 220, 220))
    buf = io.BytesIO()
    desk.save(buf, format="JPEG")

    res = await DiseaseService.detect_disease(
        image_bytes=buf.getvalue(),
        db=None,
        response_language="en"
    )

    assert res["is_plant_image"] is False
    assert res["can_analyze"] is False
    assert res["disease_name"] == "No Plant Detected"
    assert res["diagnosis_status"] == "no_plant"
    assert len(res["treatment_suggestions"]) == 0
    assert len(res["store_recommendations"]) == 0


@pytest.mark.asyncio
async def test_api_endpoint_non_plant_rejection():
    """Verify POST /disease/detect returns success=true with No Plant Detected data payload."""
    """Verify POST /api/v1/disease/detect returns success=true with No Plant Detected data payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        desk = Image.new("RGB", (300, 300), color=(230, 230, 230))
        buf = io.BytesIO()
        desk.save(buf, format="JPEG")

        response = await client.post(
            "/api/v1/disease/detect",
            files={"image": ("desk.jpg", buf.getvalue(), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert result["disease_name"] == "No Plant Detected"
        assert result["is_plant_image"] is False
        assert result["can_analyze"] is False
        assert result["diagnosis_status"] == "no_plant"
