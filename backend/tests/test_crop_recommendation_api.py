"""
Tests for the "No Soil Report" crop recommendation and Environmental Suitability flow.

Covers:
- FastAPI endpoint (validation, provenance fields, environmental suitability without pseudo-ML percentages)
- ML service (top-5 predict_proba candidates for Mode A soil report flow)
- Season engine (Kharif / Rabi / Zaid)
- Regional validation layer
- SoilGrids pH/texture and explicit UNAVAILABLE status for N/P/K
- Historical ERA5-Land annual rainfall (previous complete calendar year)
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
async def test_no_soil_report_environmental_suitability(monkeypatch):
    """
    Mode B No-Soil-Report:
    - N/P/K are explicitly UNAVAILABLE (no mock N/P/K or ML model invocation)
    - Returns full data provenance for location, weather, rainfall, soil, nutrients
    - Returns transparent environmental suitability recommendations
    """
    import app.services.no_soil_crop_service as svc

    async def fake_soil_nutrients(lat, lon):
        return {
            "success": True,
            "soil_data_available": True,
            "ph": 6.5,
            "ph_source": "SoilGrids (ISRIC)",
            "texture": {"clay": 25.0, "sand": 45.0, "silt": 30.0},
            "texture_class": "loam",
            "source": "SoilGrids (ISRIC)",
            "depth_used": "0-5cm",
            "warnings": ["pH and texture from SoilGrids (ISRIC); N/P/K not available."],
            "N": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "P": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "K": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "npk_available": False,
        }

    async def fake_current_weather(lat, lon):
        return {
            "success": True,
            "temperature_c": 29.8,
            "humidity_percent": 64.0,
            "weather": "Partly cloudy",
        }

    async def fake_annual_rainfall(lat, lon):
        return {
            "success": True,
            "annual_rainfall_mm": 833.8,
            "rainfall_source": "Open-Meteo ERA5-Land",
            "rainfall_period": "2025",
        }

    monkeypatch.setattr(svc.soil_service, "get_soil_nutrients", fake_soil_nutrients)
    monkeypatch.setattr(svc.WeatherService, "get_current_weather", fake_current_weather)
    monkeypatch.setattr(svc.WeatherService, "get_annual_rainfall", fake_annual_rainfall)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/crop-recommendation/no-soil-report",
            json={
                "latitude": 27.0238,
                "longitude": 74.2179,
                "state": "Rajasthan",
                "farmer_selected_soil_type": "Sandy Soil",
                "location_name": "Nagaur, Rajasthan, India",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["recommendation_mode"] == "ENVIRONMENTAL_SUITABILITY"
    assert data["recommendation_available"] is True
    assert data["location"]["display_name"] == "Nagaur, Rajasthan, India"
    assert data["location"]["source"] == "Device GPS"
    assert data["weather"]["temperature"]["value"] == 29.8
    assert data["weather"]["temperature"]["source"] == "Open-Meteo"
    assert data["rainfall"]["annual_rainfall"]["value"] == 833.8
    assert data["rainfall"]["annual_rainfall"]["period"] == "2025"
    assert data["soil"]["farmer_selected_type"] == "Sandy Soil"
    assert data["soil"]["ph"]["value"] == 6.5
    assert data["soil"]["ph"]["status"] == "ESTIMATED"
    assert data["soil"]["ph"]["estimated"] is True
    assert data["soil"]["ph"]["source"] == "SoilGrids (ISRIC)"
    assert data["soil"]["depth_used"] == "0-5cm"
    assert data["nutrients"]["nitrogen"]["value"] is None
    assert data["nutrients"]["nitrogen"]["status"] == "UNAVAILABLE"
    assert data["nutrients"]["nitrogen"]["requires_soil_test"] is True
    assert data["nutrients"]["phosphorus"]["value"] is None
    assert data["nutrients"]["phosphorus"]["status"] == "UNAVAILABLE"
    assert data["nutrients"]["phosphorus"]["requires_soil_test"] is True
    assert data["nutrients"]["potassium"]["value"] is None
    assert data["nutrients"]["potassium"]["status"] == "UNAVAILABLE"
    assert data["nutrients"]["potassium"]["requires_soil_test"] is True
    assert "soil_parameters" in data
    assert data["soil_parameters"]["ph"]["value"] == 6.5
    assert data["soil_parameters"]["ph"]["estimated"] is True
    assert data["soil_parameters"]["ph"]["available"] is True
    assert data["soil_parameters"]["nitrogen"]["value"] is None
    assert data["soil_parameters"]["nitrogen"]["available"] is False
    assert len(data["recommendations"]) > 0
    top_rec = data["recommendations"][0]
    assert top_rec["suitability_level"] in ["Highly Suitable", "Suitable", "Moderately Suitable"]
    assert len(top_rec["contributing_factors"]) > 0


@pytest.mark.asyncio
async def test_no_soil_report_soil_failure_graceful_provenance(monkeypatch):
    """If SoilGrids API fails completely, soil_data_available is False with explicit UNAVAILABLE statuses."""
    import app.services.no_soil_crop_service as svc

    async def fake_soil_failure(lat, lon):
        return {
            "success": False,
            "soil_data_available": False,
            "source": "SoilGrids",
            "error": "SoilGrids API timed out.",
            "warnings": ["SoilGrids data unavailable for this location."],
            "N": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "P": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "K": {"value": None, "source": None, "status": "UNAVAILABLE"},
            "npk_available": False,
        }

    async def fake_current_weather(lat, lon):
        return {
            "success": True,
            "temperature_c": 25.0,
            "humidity_percent": 50.0,
            "weather": "Clear",
        }

    async def fake_annual_rainfall(lat, lon):
        return {
            "success": True,
            "annual_rainfall_mm": 500.0,
            "rainfall_source": "Open-Meteo ERA5-Land",
            "rainfall_period": "2025",
        }

    monkeypatch.setattr(svc.soil_service, "get_soil_nutrients", fake_soil_failure)
    monkeypatch.setattr(svc.WeatherService, "get_current_weather", fake_current_weather)
    monkeypatch.setattr(svc.WeatherService, "get_annual_rainfall", fake_annual_rainfall)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/crop-recommendation/no-soil-report",
            json={"latitude": 27.0238, "longitude": 74.2179, "state": "Rajasthan"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["soil"]["soil_data_available"] is False
    assert data["soil"]["ph"]["value"] is None
    assert data["soil"]["ph"]["status"] == "UNAVAILABLE"
    assert data["soil_parameters"]["ph"]["value"] is None
    assert data["soil_parameters"]["ph"]["available"] is False
    assert data["soil_parameters"]["nitrogen"]["value"] is None
    assert data["nutrients"]["nitrogen"]["value"] is None
    assert data["nutrients"]["nitrogen"]["status"] == "UNAVAILABLE"
    assert data["soil"]["soil_data_available"] is False
    assert data["soil"]["ph"]["status"] == "UNAVAILABLE"
    assert data["soil"]["ph"]["value"] is None
    assert data["nutrients"]["nitrogen"]["status"] == "UNAVAILABLE"


# --------------------------------------------------------------------------- #
# Service unit tests
# --------------------------------------------------------------------------- #
def test_ml_service_top5_candidates():
    """Mode A: ML model predict_proba must return top-5 crops sorted by probability."""
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
    assert len(ranked) == 3
    assert ranked[0]["crop_name"] == "mothbeans"
