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


def test_plant_gatekeeper_rejects_person_foreground():
    """Verify person portrait with background foliage is rejected with 'No Plant Detected'."""
    from pathlib import Path
    img_path = Path(r"C:\Users\janar\.gemini\antigravity-ide\brain\47946171-010f-4bc2-b10b-4e46edf0a9d3\.user_uploaded\media_1788505580340.jpg")
    if img_path.exists():
        with open(img_path, "rb") as f:
            res = PlantGatekeeperService.verify_plant(f.read())
        assert res["is_plant"] is False
        assert "Person" in res["reason"] or "Non-plant" in res["reason"]


@pytest.mark.asyncio
async def test_disease_localization_hindi():
    """Verify full localization in Hindi for early blight, advice, and store subtitles."""
    from app.services.disease_translation import localize_disease_response
    sample = {
        "disease_name": "Early Blight",
        "crop_type": "Tomato",
        "treatment_suggestions": [
            "Biological: Foliar application of Trichoderma viride @ 5 g/L or Pseudomonas fluorescens @ 5 g/L",
            "Chemical: Foliar spray of Mancozeb 75% WP @ 2.5 g/L or Chlorothalonil 75% WP @ 2.0 g/L as preventive spray"
        ],
        "prevention_tips": [
            "Stake tomato plants and mulch soil surface to prevent soil splash onto lower foliage",
            "Prune bottom leaves (15-20 cm above ground) to improve air circulation"
        ],
        "store_recommendations": [
            {"title": "Mancozeb", "subtitle": "Targeted active ingredient for Early Blight"}
        ]
    }
    localized = localize_disease_response(sample, "hi")
    assert localized["disease_name"] == "अगेती झुलसा रोग"
    assert localized["crop_type"] == "टमाटर"
    assert "ट्राइकोडर्मा विरिडी" in localized["treatment_suggestions"][0]
    assert "मैंकोजेब" in localized["treatment_suggestions"][1]
    assert "मल्चिंग" in localized["prevention_tips"][0]
    assert "छंटाई" in localized["prevention_tips"][1]
    assert "लक्षित सक्रिय घटक" in localized["store_recommendations"][0]["subtitle"]


def test_plant_gatekeeper_accepts_diseased_spotted_leaf():
    """Verify diseased leaf with black necrotic lesions and yellow halo is accepted as plant."""
    from pathlib import Path
    img_path = Path(r"C:\Users\janar\.gemini\antigravity-ide\brain\a852f880-3edf-4b9b-bfff-8f0740f00db2\.user_uploaded\media_1788533156246.png")
    if img_path.exists():
        orig = Image.open(img_path).convert("RGB")
        w, h = orig.size
        crop = orig.crop((int(0.05 * w), int(0.12 * h), int(0.95 * w), int(0.35 * h)))
        buf = io.BytesIO()
        crop.save(buf, format="JPEG")
        res = PlantGatekeeperService.verify_plant(buf.getvalue())
        assert res["is_plant"] is True
        assert res["confidence"] > 0.6

