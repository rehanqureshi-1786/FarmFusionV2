"""
Test suite for Crop Disease Detection Agent & Knowledge Base Integration.
"""
import io
import pytest
from httpx import AsyncClient, ASGITransport
from PIL import Image

from app.main import app
from app.services.disease_knowledge_service import DiseaseKnowledgeService
from app.services.disease_ml_service import DiseaseMLService
from app.services.store_recommendation_service import StoreRecommendationService
from app.workflows.disease_workflow import run_disease_detection_workflow, DiseaseDetectionInput


def create_test_image_bytes(format="JPEG", size=(300, 300), color="green") -> bytes:
    """Generate in-memory valid image bytes for test requests."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 1. Knowledge Base Service Tests
# ---------------------------------------------------------------------------
def test_disease_knowledge_base_loaded():
    """Verify that knowledge base loads and contains canonical Indian crop diseases."""
    classes = DiseaseKnowledgeService.list_all_classes()
    assert len(classes) >= 10
    assert "Tomato___Late_blight" in classes
    assert "Wheat___Yellow_Rust" in classes
    assert "Cotton___Bacterial_Blight" in classes
    assert "Rice___Blast" in classes


def test_disease_knowledge_lookup_exact():
    """Verify exact disease lookup returns structured fields."""
    entry = DiseaseKnowledgeService.lookup("Late Blight", "Tomato")
    assert entry["disease"] == "Late Blight"
    assert entry["crop"] == "Tomato"
    assert len(entry["symptoms"]) > 0
    assert len(entry["chemical_control"]) > 0
    assert len(entry["active_ingredients"]) > 0
    assert "Metalaxyl + Mancozeb" in entry["active_ingredients"] or "Mancozeb" in entry["active_ingredients"]


def test_disease_knowledge_lookup_healthy():
    """Verify healthy crop lookup returns zero chemical treatments."""
    entry = DiseaseKnowledgeService.lookup("healthy", "Wheat")
    assert "healthy" in entry["disease"].lower()
    assert len(entry["active_ingredients"]) == 0
    assert "No chemical" in entry["chemical_control"][0] or "No chemical" in entry["treatment_notes"][0]


def test_disease_knowledge_lookup_unknown_fallback():
    """Verify unknown disease returns safe fallback without fabricated chemicals."""
    entry = DiseaseKnowledgeService.lookup("Fictional Martian Rot", "Corn")
    assert entry["scientific_name"] == "NOT_AVAILABLE"
    assert "Follow product label" in entry["chemical_control"][0]


# ---------------------------------------------------------------------------
# 2. Confidence Tier Calculation Tests
# ---------------------------------------------------------------------------
def test_confidence_tiers():
    """Verify confidence tier thresholds match safety guidelines."""
    assert DiseaseMLService.calculate_confidence_tier(0.92) == "high"
    assert DiseaseMLService.calculate_confidence_tier(0.75) == "high"
    assert DiseaseMLService.calculate_confidence_tier(0.74) == "medium"
    assert DiseaseMLService.calculate_confidence_tier(0.45) == "medium"
    assert DiseaseMLService.calculate_confidence_tier(0.44) == "low"
    assert DiseaseMLService.calculate_confidence_tier(0.30) == "low"
    assert DiseaseMLService.calculate_confidence_tier(0.29) == "unclear"
    assert DiseaseMLService.calculate_confidence_tier(0.0) == "unclear"


# ---------------------------------------------------------------------------
# 3. Store Recommendation Service Integration Tests
# ---------------------------------------------------------------------------
def test_store_recommendations_for_disease():
    """Verify store recommendations generate valid Amazon India search links."""
    recs = StoreRecommendationService.build(
        source="disease",
        disease_name="Bacterial Blight",
        crop_hint="Cotton",
        active_ingredients=["Copper Oxychloride", "Streptocycline"],
        product_categories=["Bactericide", "Copper Fungicide"]
    )
    assert recs["success"] is True
    assert len(recs["items"]) > 0
    first_item = recs["items"][0]
    assert "amazon.in" in first_item["shop_url"]
    assert len(first_item["title"]) > 0


# ---------------------------------------------------------------------------
# 4. Disease Workflow Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_disease_workflow_execution():
    """Verify end-to-end disease workflow execution."""
    img_bytes = create_test_image_bytes()
    inp = DiseaseDetectionInput(image_bytes=img_bytes, crop_name="Wheat", language="hi")
    res = await run_disease_detection_workflow(inp)
    assert res.disease_name is not None
    assert res.confidence >= 0.0
    assert res.confidence_tier in ("high", "medium", "low", "unclear")
    assert len(res.treatment_steps) > 0
    assert len(res.farmer_message) > 0


# ---------------------------------------------------------------------------
# 5. FastAPI Endpoint Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api_disease_detect_valid_image():
    """Test POST /api/v1/disease/detect with valid JPEG image."""
    img_bytes = create_test_image_bytes()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"image": ("leaf.jpg", img_bytes, "image/jpeg")}
        response = await ac.post("/api/v1/disease/detect?crop_type=Tomato", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        res_data = data["data"]
        assert "disease_name" in res_data
        assert "confidence_tier" in res_data
        assert res_data["confidence_tier"] in ("high", "medium", "low", "unclear")
        assert "treatment" in res_data
        assert "store_recommendations" in res_data
        assert "top_predictions" in res_data
        assert "model_version" in res_data
        assert "is_reliable" in res_data


@pytest.mark.asyncio
async def test_api_disease_detect_corrupt_image():
    """Test POST /api/v1/disease/detect rejects corrupted bytes with 400."""
    corrupt_bytes = b"NOT_A_REAL_IMAGE_DATA_CORRUPT"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"image": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}
        response = await ac.post("/api/v1/disease/detect", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "Corrupted or invalid image" in data["detail"]


@pytest.mark.asyncio
async def test_api_disease_info_endpoint():
    """Test GET /api/v1/disease/info/{disease_name}."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/disease/info/Late%20Blight?crop_type=Tomato")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["disease"] == "Late Blight"
