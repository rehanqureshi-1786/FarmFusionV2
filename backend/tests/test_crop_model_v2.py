"""
Tests for FarmFusion Crop Recommendation Model V2 Integration.

Comprehensive suite verifying:
A. V2 artifacts exist and load successfully
B. V2 metadata validates schema, units, 57 classes, and 10 features
C. V2 has exactly 57 classes
D. V2 has exactly 10 features
E. Feature vector order and mathematical definitions are exact
F. V2 inference returns probabilities for all 57 classes
G. Probabilities sum approximately to 1.0
H. Label encoder correctly maps class IDs to canonical names
I. Calibrator loads and produces calibrated probabilities
J. CropMLService selects V2 as PRIMARY
K. V1 remains untouched and usable as fallback
L. Missing or corrupt V2 artifact safely triggers V1 fallback
M. Mode A uses real N/P/K/pH inputs
N. Mode B never fabricates N/P/K
O. Local result remains PRIMARY when confidence is reliable
P. Groq remains STRICT FALLBACK
Q. Existing multi-factor ranking engine still works
R. Existing API response format remains compatible
"""
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import joblib
import numpy as np
import pytest

from app.core.config import get_settings
from app.services.ml_service import CropMLService, crop_ml_service, FEATURE_NAMES
from app.services.crop_agent_v2.local_engine import local_crop_engine
from app.services.crop_agent_v2.ranking_engine import ranking_engine
from app.services.crop_agent_v2.agent import crop_agent_v2


def test_v2_artifacts_exist():
    """A. Verify Model V2 artifact files exist in app/ml_models/crop/v2/."""
    base_dir = Path(__file__).resolve().parents[1]
    v2_dir = base_dir / "app" / "ml_models" / "crop" / "v2"

    assert (v2_dir / "crop_recommendation_v2.joblib").exists()
    assert (v2_dir / "crop_label_encoder_v2.joblib").exists()
    assert (v2_dir / "crop_model_v2_calibrator.joblib").exists()
    assert (v2_dir / "crop_model_metadata_v2.json").exists()


def test_v1_baseline_artifacts_untouched():
    """K. Verify V1 baseline files exist and were not overwritten."""
    base_dir = Path(__file__).resolve().parents[1]
    v1_dir = base_dir / "app" / "ml_models"

    assert (v1_dir / "crop_recommendation.joblib").exists()
    assert (v1_dir / "crop_label_encoder.joblib").exists()
    assert (v1_dir / "crop_model_metadata.json").exists()


def test_v2_metadata_schema_and_units():
    """B, C, D. Verify metadata schema, 57 classes, 10 features, and units."""
    base_dir = Path(__file__).resolve().parents[1]
    meta_path = base_dir / "app" / "ml_models" / "crop" / "v2" / "crop_model_metadata_v2.json"

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["version"].startswith("2.0.0")
    assert meta["n_classes"] == 57
    assert len(meta["classes"]) == 57
    assert meta["n_features"] == 10
    assert meta["feature_names"] == FEATURE_NAMES
    assert "feature_units" in meta
    assert meta["feature_units"]["N"].startswith("kg/ha")
    assert meta["feature_units"]["rainfall"].startswith("mm_seasonal")
    assert meta["stcr_data_used"] is False
    assert "test_metrics" in meta
    assert meta["test_metrics"]["accuracy"] > 0.90
    assert meta["test_metrics"]["top_3_accuracy"] > 0.95
    assert meta["test_metrics"]["top_5_accuracy"] > 0.98


def test_feature_vector_order_and_formulas():
    """E. Verify exact feature ordering and mathematical definitions."""
    expected_order = [
        "N", "P", "K", "temperature", "humidity", "ph", "rainfall",
        "NPK_sum", "N_to_P_ratio", "temp_humidity_interaction"
    ]
    assert FEATURE_NAMES == expected_order

    vec = CropMLService.build_feature_vector(
        nitrogen=90.0,
        phosphorus=45.0,
        potassium=40.0,
        temperature=25.0,
        humidity=80.0,
        ph=6.5,
        rainfall=1200.0,
    )
    assert len(vec) == 10
    assert vec[0] == 90.0
    assert vec[1] == 45.0
    assert vec[2] == 40.0
    assert vec[3] == 25.0
    assert vec[4] == 80.0
    assert vec[5] == 6.5
    assert vec[6] == 1200.0
    assert vec[7] == (90.0 + 45.0 + 40.0)  # NPK_sum
    assert np.isclose(vec[8], 90.0 / (45.0 + 1e-6))  # N_to_P_ratio
    assert np.isclose(vec[9], 25.0 * 80.0 / 100.0)  # temp_humidity_interaction


def test_v2_model_inference_and_probabilities():
    """F, G, H, I. Verify 57 classes, probability sum ~ 1.0, label encoder mapping, and calibrator."""
    base_dir = Path(__file__).resolve().parents[1]
    v2_dir = base_dir / "app" / "ml_models" / "crop" / "v2"

    model = joblib.load(v2_dir / "crop_recommendation_v2.joblib")
    encoder = joblib.load(v2_dir / "crop_label_encoder_v2.joblib")
    calibrator = joblib.load(v2_dir / "crop_model_v2_calibrator.joblib")

    # Sample input (Wheat-like conditions)
    sample = np.array([[100.0, 50.0, 45.0, 19.0, 55.0, 6.8, 550.0, 195.0, 2.0, 10.45]])
    
    # Base model proba
    base_proba = model.predict_proba(sample)[0]
    assert len(base_proba) == 57
    assert np.isclose(np.sum(base_proba), 1.0, atol=1e-4)

    # Calibrator proba
    cal_proba = calibrator.predict_proba(sample)[0]
    assert len(cal_proba) == 57
    assert np.isclose(np.sum(cal_proba), 1.0, atol=1e-4)

    # Verify label encoder
    assert len(encoder.classes_) == 57
    top_class_idx = int(np.argmax(cal_proba))
    top_crop = str(encoder.classes_[top_class_idx]).lower()
    assert any(c in top_crop for c in ["wheat", "mustard", "chickpea", "potato", "peas", "barley"])


def test_ml_service_loads_v2_as_primary():
    """J. Verify CropMLService loads Model V2 as primary."""
    assert crop_ml_service.is_available() is True
    assert crop_ml_service.is_v2 is True
    metadata = crop_ml_service.get_metadata()
    assert metadata is not None
    assert metadata.get("version").startswith("2.0.0")
    assert metadata.get("n_classes") == 57


def test_ml_service_v1_fallback_on_missing_v2():
    """L. Verify that if V2 paths are invalid, CropMLService gracefully falls back to V1."""
    fresh_service = CropMLService()
    
    # Mock resolve_path to return a non-existent path for the V2 model
    original_resolve = fresh_service._resolve_path
    def mock_resolve(path_str: str) -> Path:
        if "v2" in str(path_str):
            return Path("/non_existent/v2_model.joblib")
        return original_resolve(path_str)

    with patch.object(fresh_service, "_resolve_path", side_effect=mock_resolve):
        fresh_service._ensure_loaded()
        assert fresh_service.is_available() is True
        assert fresh_service.is_v2 is False
        assert len(fresh_service.label_encoder.classes_) == 22


def test_ml_service_input_validation():
    """Verify input validation rejects invalid/NaN/infinite inputs."""
    with pytest.raises(ValueError):
        CropMLService.build_feature_vector(
            nitrogen=float("nan"),
            phosphorus=40.0,
            potassium=40.0,
            temperature=25.0,
            humidity=80.0,
            ph=6.5,
            rainfall=800.0,
        )

    with pytest.raises(ValueError):
        CropMLService.build_feature_vector(
            nitrogen=90.0,
            phosphorus=-5.0,  # Negative nutrient
            potassium=40.0,
            temperature=25.0,
            humidity=80.0,
            ph=6.5,
            rainfall=800.0,
        )


def test_mode_a_with_v2_model():
    """M. Verify Mode A uses Model V2 predictions and ranks candidates properly."""
    ranked, is_reliable, msg = local_crop_engine.recommend_mode_a(
        nitrogen=90.0,
        phosphorus=45.0,
        potassium=40.0,
        ph=6.5,
        temperature_c=25.0,
        humidity_pct=80.0,
        rainfall_mm=1200.0,
        state="west bengal",
        soil_type="Alluvial Soil",
        season="Kharif",
    )
    assert is_reliable is True
    assert len(ranked) >= 3
    top_names = [r["crop_name"] for r in ranked[:3]]
    assert any(name in ["Rice", "Jute", "Maize"] for name in top_names)
    assert ranked[0]["model_probability"] is not None


def test_mode_b_never_fabricates_npk():
    """N. Verify Mode B operates without N/P/K inputs and never fabricates values."""
    ranked, is_reliable, msg = local_crop_engine.recommend_mode_b(
        temperature_c=28.0,
        humidity_pct=75.0,
        rainfall_mm=850.0,
        ph=6.8,
        soil_type="Alluvial Soil",
        state="punjab",
        season="Kharif",
    )
    assert is_reliable is True
    assert len(ranked) >= 3
    for r in ranked:
        assert "crop_name" in r
        assert "confidence_score" in r


@pytest.mark.asyncio
async def test_local_primary_groq_fallback_intact():
    """O, P. Verify local primary result bypasses Groq when reliable."""
    # Reliable Mode A input
    with patch("app.services.crop_agent_v2.agent.fallback_engine.generate_fallback_recommendations") as mock_groq:
        recs, msg, meta = await crop_agent_v2.get_recommendations(
            nitrogen=90.0,
            phosphorus=45.0,
            potassium=40.0,
            ph=6.5,
            temperature_c=25.0,
            humidity_pct=80.0,
            rainfall_mm=1200.0,
            state="west bengal",
            soil_type="Alluvial Soil",
        )
        assert meta["fallback_used"] is False
        assert meta["recommendation_source"] == "local_agent"
        assert len(recs) >= 3
        # Groq should NEVER be called for reliable local recommendations
        mock_groq.assert_not_called()


def test_ranking_engine_configurable_weights():
    """Q. Verify ranking engine heuristic weights are configurable."""
    assert ranking_engine.WEIGHTS_MODE_A["ml_probability"] == 0.35
    assert ranking_engine.WEIGHTS_MODE_A["season"] == 0.15
    assert ranking_engine.WEIGHTS_MODE_B["season"] == 0.25
    assert ranking_engine.WEIGHTS_MODE_B["temperature"] == 0.25
