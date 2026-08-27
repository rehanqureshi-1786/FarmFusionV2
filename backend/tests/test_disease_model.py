"""
Model validation test suite for Disease Detection Model V2 (38-Class EfficientNet-B3) & V1 Fallback.
"""
import io
import json
import time
from pathlib import Path
import pytest
from PIL import Image
import torch

from app.core.config import settings
from app.services.disease_ml_service import DiseaseMLService


def test_model_artifacts_exist():
    """Verify all required model artifact files exist on disk for both V2 and V1."""
    base_dir = Path(__file__).resolve().parents[1]

    # V2 primary artifacts
    v2_dir = base_dir / "app" / "ml_models" / "disease" / "v2"
    assert (v2_dir / "disease_model_v2_38class.pth").exists(), "V2 weights missing"
    assert (v2_dir / "disease_label_mapping_v2_38class.json").exists(), "V2 label mapping missing"
    assert (v2_dir / "disease_model_metadata_v2_38class.json").exists(), "V2 metadata missing"

    # V1 fallback artifacts
    v1_dir = base_dir / "app" / "ml_models" / "disease" / "v1"
    assert (v1_dir / "disease_model_v1.pth").exists(), "V1 weights missing"
    assert (v1_dir / "disease_label_mapping.json").exists(), "V1 label mapping missing"
    assert (v1_dir / "disease_model_metadata.json").exists(), "V1 metadata missing"


def test_v2_38class_label_mapping():
    """Verify that V2 mapping loads exactly 38 classes without hardcoding."""
    base_dir = Path(__file__).resolve().parents[1]
    mapping_path = base_dir / "app" / "ml_models" / "disease" / "v2" / "disease_label_mapping_v2_38class.json"
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    classes = data.get("class_names", [])
    assert len(classes) == 38
    assert len(data.get("class_to_idx", {})) == 38
    assert "Tomato___Late_blight" in classes
    assert "Apple___Apple_scab" in classes
    assert "Corn_(maize)___Northern_Leaf_Blight" in classes


def test_v2_disease_model_initialization_and_inference(capsys):
    """Verify singleton initialization, metadata reading, CPU/GPU inference, top-3 predictions, and timing."""
    # Ensure fresh initialization
    initialized = DiseaseMLService.initialize(force_reload=True)
    assert initialized is True
    assert DiseaseMLService.is_model_available() is True

    info = DiseaseMLService.get_model_info()
    assert info["version"] == "v2_38class"
    assert info["num_classes"] == 38
    assert len(info["classes"]) == 38

    # Create sample synthetic leaf image
    img = Image.new("RGB", (300, 300), color=(40, 150, 40))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    t0 = time.perf_counter()
    result = DiseaseMLService.predict(img_bytes, crop_hint="Tomato")
    inference_time_ms = (time.perf_counter() - t0) * 1000

    assert result is not None
    assert "class_name" in result
    assert "class_index" in result
    assert "confidence" in result
    assert "confidence_level" in result
    assert "confidence_tier" in result
    assert "top_predictions" in result
    assert len(result["top_predictions"]) == 3
    assert "entropy" in result
    assert "is_reliable" in result
    assert result["model_version"] == "v2_38class"
    assert result["inference_source"] == "ML_VISION"

    # Print formatted diagnostic report matching Step 12 specification
    print("\n" + "=" * 50)
    print("FARMFUSION DISEASE MODEL VALIDATION REPORT")
    print("=" * 50)
    print(f"Model:             {info['version']}")
    print(f"Architecture:      {info['architecture']}")
    print(f"Number of classes: {info['num_classes']}")
    print(f"Image size:        {info['image_size']}x{info['image_size']}")
    print(f"Predicted class:   {result['class_name']}")
    print(f"Confidence:        {result['confidence']:.4f}")
    print(f"Confidence level:  {result['confidence_level']}")
    print(f"Top-3 predictions: {[p['class_name'] for p in result['top_predictions']]}")
    print(f"Inference time:    {inference_time_ms:.2f} ms")
    print(f"Device:            {info['device']}")
    print("=" * 50)


def test_confidence_safety_tiers():
    """Verify confidence tier calculation rules."""
    assert DiseaseMLService.calculate_confidence_tier(0.95) == "high"
    assert DiseaseMLService.calculate_confidence_tier(0.75) == "high"
    assert DiseaseMLService.calculate_confidence_tier(0.74) == "medium"
    assert DiseaseMLService.calculate_confidence_tier(0.45) == "medium"
    assert DiseaseMLService.calculate_confidence_tier(0.44) == "low"
    assert DiseaseMLService.calculate_confidence_tier(0.30) == "low"
    assert DiseaseMLService.calculate_confidence_tier(0.29) == "unclear"
    assert DiseaseMLService.calculate_confidence_tier(0.05) == "unclear"


def test_v1_fallback_behavior(monkeypatch):
    """Verify that service falls back to V1 when V2 path is not present."""
    # Point V2 to a non-existent path to trigger V1 fallback
    monkeypatch.setattr(settings, "disease_model_path", "app/ml_models/disease/v2/non_existent.pth")
    initialized = DiseaseMLService.initialize(force_reload=True)
    assert initialized is True

    info = DiseaseMLService.get_model_info()
    assert info["version"] == "v1_15class"
    assert info["num_classes"] == 15

    # Run inference with fallback model
    img = Image.new("RGB", (300, 300), color=(50, 160, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = DiseaseMLService.predict(buf.getvalue())
    assert res is not None
    assert res["model_version"] == "v1_15class"
    assert len(res["top_predictions"]) == 3

    # Restore V2
    monkeypatch.undo()
    DiseaseMLService.initialize(force_reload=True)
    assert DiseaseMLService.get_model_info()["version"] == "v2_38class"
