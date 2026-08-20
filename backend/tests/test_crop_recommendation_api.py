"""
Tests for the "No Soil Report" crop recommendation flow.

Covers:
- the new FastAPI endpoint (validation, failure without fabrication, happy path)
- the ML service (top-5 predict_proba candidates)
- the season engine (Kharif / Rabi / Zaid)
- the regional validation layer (re-ranking + neutral fallback)
- soil service behavior (SoilGrids pH/texture, N/P/K unavailable)
- historical rainfall feature (not 7-day forecast)
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# --------------------------------------------------------------------------- #
# Endpoint tests
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_no_soil_report_validation_error():
    """Missing required latitude should return a 422 validation error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/crop-recommendation/no-soil-report",
            json={"longitude": 74.2179},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_no_soil_report_npk_unavailable(monkeypatch):
    """
    If N/P/K are not available (no compatible source), the endpoint must fail
    cleanly with 503 (no invented values).
    """
    import app.services.no_soil_crop_service as svc

    # SoilGrids returns success for pH/texture but npk_available=False
    async def fake_soil_npk_unavailable(lat, lon):
        return {
            "success": True,
            "ph": 6.5,
            "texture": {"clay": 25.0, "sand": 45.0, "silt": 30.0},
            "texture_class": "loam",
            "source": "SoilGrids (ISRIC)",
            "depth_used": "0-5cm",
            "warnings": ["pH and texture from SoilGrids; N/P/K not available."],
            "N": None,
            "P": None,
            "K": None,
            "npk_available": False,
        }

    async def fake_weather(lat, lon, season):
        return {
            "temperature_c": 29.8,
            "humidity_percent": 64.0,
            "rainfall_mm": 380.0,
            "rainfall_source": "Open-Meteo ERA5-Land (seasonal)",
            "current_conditions": "partly cloudy",
            "source": "open-meteo",
        }

    async def fake_explain(candidates, context, language="en"):
        return "Test explanation of the structured ML candidates."

    monkeypatch.setattr(svc.soil_service, "get_soil_nutrients", fake_soil_npk_unavailable)
    monkeypatch.setattr(svc, "_resolve_weather", fake_weather)
    monkeypatch.setattr(svc.crop_agent, "explain_structured_recommendations", fake_explain)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/crop-recommendation/no-soil-report",
            json={"latitude": 27.0238, "longitude": 74.2179, "state": "Rajasthan"},
        )
    assert response.status_code == 503
    detail = response.json()["detail"].lower()
    assert "nutrient" in detail or "n/p/k" in detail


@pytest.mark.asyncio
async def test_no_soil_report_soil_failure_no_fabrication(monkeypatch):
    """If the soil API fails completely, the endpoint must fail cleanly (no invented values)."""
    import app.services.no_soil_crop_service as svc

    async def fake_soil_failure(lat, lon):
        return {
            "success": False,
            "source": "SoilGrids",
            "error": "SoilGrids API timed out.",
        }

    monkeypatch.setattr(svc.soil_service, "get_soil_nutrients", fake_soil_failure)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/crop-recommendation/no-soil-report",
            json={"latitude": 27.0238, "longitude": 74.2179, "state": "Rajasthan"},
        )
    assert response.status_code == 503
    assert "soil" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_no_soil_report_happy_path_with_npk(monkeypatch):
    """
    Full pipeline with mocked soil (including N/P/K) and weather returns top 3 crops.
    This test simulates a scenario where N/P/K ARE available (e.g., from a future
    compatible source or manual entry).
    """
    import app.services.no_soil_crop_service as svc

    async def fake_soil_with_npk(lat, lon):
        return {
            "success": True,
            "N": 92.0,
            "P": 44.0,
            "K": 45.0,
            "ph": 6.3,
            "texture": {"clay": 25.0, "sand": 45.0, "silt": 30.0},
            "texture_class": "loam",
            "source": "Test Source (with N/P/K)",
            "depth_used": "0-5cm",
            "warnings": [],
            "npk_available": True,
        }

    async def fake_weather(lat, lon, season):
        return {
            "temperature_c": 29.8,
            "humidity_percent": 64.0,
            "rainfall_mm": 380.0,
            "rainfall_source": "Open-Meteo ERA5-Land (seasonal)",
            "current_conditions": "partly cloudy",
            "source": "open-meteo",
        }

    async def fake_explain(candidates, context, language="en"):
        return "Test explanation of the structured ML candidates."

    monkeypatch.setattr(svc.soil_service, "get_soil_nutrients", fake_soil_with_npk)
    monkeypatch.setattr(svc, "_resolve_weather", fake_weather)
    monkeypatch.setattr(svc.crop_agent, "explain_structured_recommendations", fake_explain)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/crop-recommendation/no-soil-report",
            json={"latitude": 27.0238, "longitude": 74.2179, "state": "Rajasthan"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["soil_source"] == "Test Source (with N/P/K)"
    assert data["season"] in ("Kharif", "Rabi", "Zaid")
    assert data["season_window"]
    assert len(data["top_crops"]) == 3
    for crop in data["top_crops"]:
        assert 0.0 <= crop["model_probability"] <= 1.0
        assert crop["regional_score"] > 0
    assert data["explanation"] == "Test explanation of the structured ML candidates."
    # Should NOT contain the old 7-day forecast warning
    assert not any("7-day forecast" in w for w in data["warnings"])
    # Should contain seasonal rainfall warning
    assert any("seasonal" in w.lower() or "historical" in w.lower() for w in data["warnings"])


# --------------------------------------------------------------------------- #
# Service unit tests
# --------------------------------------------------------------------------- #
def test_ml_service_top5_candidates():
    """predict_proba must return top-5 crops sorted by probability."""
    from app.services.ml_service import crop_ml_service

    candidates = crop_ml_service.predict_top_candidates(
        nitrogen=90, phosphorus=42, potassium=43,
        temperature=26, humidity=66, ph=6.4, rainfall=202, top_k=5,
    )
    assert len(candidates) == 5
    probabilities = [c["probability"] for c in candidates]
    assert probabilities == sorted(probabilities, reverse=True)
    assert all(0.0 <= c["probability"] <= 1.0 for c in candidates)


def test_season_service_boundaries():
    """Kharif = June-Oct, Rabi = Nov-Mar, Zaid = Apr-May."""
    from app.services.season_service import season_service

    assert season_service.get_current_season(month=1) == "Rabi"
    assert season_service.get_current_season(month=3) == "Rabi"
    assert season_service.get_current_season(month=4) == "Zaid"
    assert season_service.get_current_season(month=5) == "Zaid"
    assert season_service.get_current_season(month=6) == "Kharif"
    assert season_service.get_current_season(month=10) == "Kharif"
    assert season_service.get_current_season(month=11) == "Rabi"


def test_regional_validation_reranks():
    """Regional layer must re-rank by weight and stay neutral for unknown states."""
    from app.services.regional_validation import apply

    candidates = [
        {"crop_name": "rice", "probability": 0.6, "model_class_id": 20},
        {"crop_name": "mothbeans", "probability": 0.3, "model_class_id": 13},
        {"crop_name": "coffee", "probability": 0.1, "model_class_id": 5},
    ]

    ranked, warnings = apply("Rajasthan", candidates, "Kharif")
    assert ranked[0]["crop_name"] == "mothbeans"  # boosted (1.3) above rice (0.6 penalty)
    assert ranked[1]["crop_name"] == "rice"
    assert warnings == []

    ranked_neutral, warnings_neutral = apply("", candidates, "Kharif")
    assert all(item["regional_score"] == 1.0 for item in ranked_neutral)
    assert len(warnings_neutral) == 1


# --------------------------------------------------------------------------- #
# Soil Service tests
# --------------------------------------------------------------------------- #
def test_soil_service_sanitize_ph():
    """pH validation should reject out-of-range values."""
    from app.services.soil_service import SoilService
    assert SoilService._sanitize_value("ph", 6.5) is True
    assert SoilService._sanitize_value("ph", 0.0) is True
    assert SoilService._sanitize_value("ph", 14.0) is True
    assert SoilService._sanitize_value("ph", -0.1) is False
    assert SoilService._sanitize_value("ph", 14.1) is False
    assert SoilService._sanitize_value("ph", None) is False


def test_soil_service_sanitize_npk():
    """NPK validation should reject negative or absurdly high values."""
    from app.services.soil_service import SoilService
    assert SoilService._sanitize_value("N", 92.0) is True
    assert SoilService._sanitize_value("N", 0.0) is True
    assert SoilService._sanitize_value("N", -1.0) is False
    assert SoilService._sanitize_value("N", 10001) is False
    assert SoilService._sanitize_value("N", None) is False


def test_soil_service_texture_classification():
    """Texture classification should return reasonable USDA classes."""
    from app.services.soil_service import SoilService
    # Loam (clay ~20, sand ~40, silt ~40) - this is silt_loam per USDA
    assert SoilService._classify_texture(20.0, 40.0, 40.0) == "silt_loam"
    # Clay (clay >= 40)
    assert SoilService._classify_texture(50.0, 20.0, 30.0) == "clay"
    # Sand (sand >= 90)
    assert SoilService._classify_texture(5.0, 92.0, 3.0) == "sand"
    # Sandy loam
    assert SoilService._classify_texture(10.0, 65.0, 25.0) == "sandy_loam"
    # None when components missing
    assert SoilService._classify_texture(None, 40.0, 30.0) is None
