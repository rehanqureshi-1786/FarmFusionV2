"""
Unit tests for EnvironmentalSuitabilityService.

Verifies transparent ICAR/FAO agronomic evaluation without pseudo-ML confidences.
Tests all 4 farmer-selectable soil types: Sandy Soil, Black Soil, Red Soil, Alluvial Soil.
"""
import pytest
from app.services.environmental_suitability_service import environmental_suitability_service


def test_sandy_soil_arid_climate():
    """Sandy Soil + Arid climate (low rainfall, warm temp, Kharif) should evaluate drought-hardy crops."""
    results = environmental_suitability_service.evaluate(
        temperature_c=30.0,
        humidity_percent=45.0,
        annual_rainfall_mm=380.0,
        soil_type="Sandy Soil",
        ph=7.2,
        texture={"sand": 75.0, "clay": 10.0, "silt": 15.0},
        season="Kharif",
        state="Rajasthan",
    )
    assert len(results) > 0
    crop_names = [r["crop_name"] for r in results]
    assert any("Bajra" in name or "Pearl Millet" in name for name in crop_names)
    assert any("Groundnut" in name or "Moong" in name for name in crop_names)

    top = results[0]
    assert top["suitability_level"] in ["Highly Suitable", "Suitable"]
    assert len(top["contributing_factors"]) > 0


def test_black_soil_kharif_monsoon():
    """Black Soil + Monsoon rainfall (high moisture, warm temp, Kharif)."""
    results = environmental_suitability_service.evaluate(
        temperature_c=26.0,
        humidity_percent=80.0,
        annual_rainfall_mm=940.0,
        soil_type="Black Soil",
        ph=7.4,
        texture={"sand": 20.0, "clay": 55.0, "silt": 25.0},
        season="Kharif",
        state="Maharashtra",
    )
    assert len(results) > 0
    crop_names = [r["crop_name"] for r in results]
    assert any("Cotton" in name or "Soybean" in name or "Rice" in name for name in crop_names)


def test_alluvial_soil_rabi():
    """Alluvial Soil + Rabi season (cool winter, moderate rainfall)."""
    results = environmental_suitability_service.evaluate(
        temperature_c=18.0,
        humidity_percent=60.0,
        annual_rainfall_mm=550.0,
        soil_type="Alluvial Soil",
        ph=6.8,
        texture={"sand": 35.0, "clay": 30.0, "silt": 35.0},
        season="Rabi",
        state="Punjab",
    )
    assert len(results) > 0
    crop_names = [r["crop_name"] for r in results]
    assert any("Wheat" in name or "Mustard" in name or "Chickpea" in name for name in crop_names)


def test_red_soil_kharif():
    """Red Soil + Moderate rainfall, Kharif season."""
    results = environmental_suitability_service.evaluate(
        temperature_c=28.0,
        humidity_percent=65.0,
        annual_rainfall_mm=700.0,
        soil_type="Red Soil",
        ph=6.2,
        texture={"sand": 50.0, "clay": 25.0, "silt": 25.0},
        season="Kharif",
        state="Karnataka",
    )
    assert len(results) > 0
    crop_names = [r["crop_name"] for r in results]
    assert any("Maize" in name or "Pigeonpea" in name or "Groundnut" in name for name in crop_names)


def test_missing_environmental_inputs():
    """Graceful degradation when SoilGrids or Weather is unavailable."""
    results = environmental_suitability_service.evaluate(
        temperature_c=None,
        humidity_percent=None,
        annual_rainfall_mm=None,
        soil_type="Sandy Soil",
        ph=None,
        texture=None,
        season="Kharif",
        state=None,
    )
    assert isinstance(results, list)
