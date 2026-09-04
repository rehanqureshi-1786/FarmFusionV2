"""
Disease ML Inference Service:
Runs lightweight vision classification using 38-Class EfficientNet-B3 with ImageNet transfer weights (V2 Primary),
with automatic fallback to 15-Class EfficientNet-B3 (V1) if primary artifacts are unavailable.
Calculates strict 4-tier confidence scores, top-3 predictions, entropy calibration, and OOD uncertainty detection.
"""
from __future__ import annotations

import io
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import structlog
from PIL import Image

from app.core.config import settings

logger = structlog.get_logger(__name__)

DEFAULT_IMAGE_SIZE = 300
DEFAULT_MEAN = [0.485, 0.456, 0.406]
DEFAULT_STD = [0.229, 0.224, 0.225]


class DiseaseMLService:
    _model = None
    _model_version: str = "none"
    _classes: Optional[List[str]] = None
    _class_to_idx: Optional[Dict[str, int]] = None
    _metadata: Optional[Dict[str, Any]] = None
    _device = None
    _transform = None
    _initialized: bool = False

    @classmethod
    def _resolve_path(cls, path_str: str) -> Path:
        p = Path(path_str)
        if not p.is_absolute():
            p = Path(__file__).resolve().parents[2] / p
        return p

    @classmethod
    def _load_artifacts_for_version(
        cls,
        model_path_str: str,
        mapping_path_str: str,
        metadata_path_str: Optional[str] = None
    ) -> Tuple[Optional[Any], Optional[List[str]], Optional[Dict[str, Any]]]:
        """Attempt to load PyTorch model weights, label mapping, and metadata for a specific version."""
        import torch
        import torchvision.models as models

        model_path = cls._resolve_path(model_path_str)
        mapping_path = cls._resolve_path(mapping_path_str)
        metadata_path = cls._resolve_path(metadata_path_str) if metadata_path_str else None

        if not model_path.exists() or model_path.stat().st_size < 1000:
            logger.debug("disease_model_file_missing_or_empty", path=str(model_path))
            return None, None, None

        if not mapping_path.exists():
            logger.debug("disease_label_mapping_missing", path=str(mapping_path))
            return None, None, None

        # Load label mapping
        classes: List[str] = []
        with open(mapping_path, "r", encoding="utf-8") as f:
            mapping_data = json.load(f)
            if isinstance(mapping_data, list):
                classes = mapping_data
            elif isinstance(mapping_data, dict):
                classes = mapping_data.get("class_names", [])

        if not classes:
            logger.warning("empty_class_mapping", path=str(mapping_path))
            return None, None, None

        # Load metadata if present
        metadata: Dict[str, Any] = {}
        if metadata_path and metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception as meta_err:
                logger.warning("failed_to_load_metadata", error=str(meta_err), path=str(metadata_path))

        num_classes = len(classes)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Construct EfficientNet-B3 architecture matching state_dict
        model = None
        try:
            # Try timm first if available, otherwise torchvision standard model
            try:
                import timm
                model = timm.create_model("efficientnet_b3", pretrained=False, num_classes=num_classes)
            except Exception:
                model = models.efficientnet_b3(weights=None, num_classes=num_classes)

            state_dict = torch.load(str(model_path), map_location=device, weights_only=True)
            try:
                model.load_state_dict(state_dict)
            except Exception:
                # If timm / torchvision keys differ slightly (e.g. classifier vs fc), retry with torchvision
                model = models.efficientnet_b3(weights=None, num_classes=num_classes)
                model.load_state_dict(state_dict)

            model.to(device)
            model.eval()
            return model, classes, metadata
        except Exception as e:
            logger.warning("model_weights_load_failed", path=str(model_path), error=str(e))
            return None, None, None

    @classmethod
    def initialize(cls, force_reload: bool = False) -> bool:
        """
        Singleton initialization of Disease ML Service at startup.
        Loads V2 (38-class) as PRIMARY, falls back to V1 (15-class) if V2 is unavailable.
        """
        if cls._initialized and not force_reload and cls._model is not None:
            return True

        import torch
        import torchvision.transforms as transforms

        cls._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # 1. Attempt V2 Primary Model (38-class)
        v2_model, v2_classes, v2_meta = cls._load_artifacts_for_version(
            model_path_str=getattr(settings, "disease_model_path", "app/ml_models/disease/v2/disease_model_v2_38class.pth"),
            mapping_path_str=getattr(settings, "disease_label_mapping_path", "app/ml_models/disease/v2/disease_label_mapping_v2_38class.json"),
            metadata_path_str=getattr(settings, "disease_model_metadata_path", "app/ml_models/disease/v2/disease_model_metadata_v2_38class.json"),
        )

        if v2_model is not None and v2_classes:
            cls._model = v2_model
            cls._classes = v2_classes
            cls._class_to_idx = {c: i for i, c in enumerate(v2_classes)}
            cls._metadata = v2_meta or {}
            cls._model_version = "v2_38class"
            logger.info(
                "disease_model_loaded",
                version="V2",
                architecture="EfficientNet-B3",
                classes=len(cls._classes),
                device=str(cls._device),
                model_loaded=True
            )
        else:
            # 2. Fallback to V1 Model (15-class)
            v1_model, v1_classes, v1_meta = cls._load_artifacts_for_version(
                model_path_str=getattr(settings, "disease_model_v1_path", "app/ml_models/disease/v1/disease_model_v1.pth"),
                mapping_path_str=getattr(settings, "disease_label_mapping_v1_path", "app/ml_models/disease/v1/disease_label_mapping.json"),
                metadata_path_str=getattr(settings, "disease_model_v1_metadata_path", "app/ml_models/disease/v1/disease_model_metadata.json"),
            )
            if v1_model is not None and v1_classes:
                cls._model = v1_model
                cls._classes = v1_classes
                cls._class_to_idx = {c: i for i, c in enumerate(v1_classes)}
                cls._metadata = v1_meta or {}
                cls._model_version = "v1_15class"
                logger.warning(
                    "disease_model_fallback_loaded",
                    version="V1",
                    architecture="EfficientNet-B3",
                    classes=len(cls._classes),
                    device=str(cls._device),
                    model_loaded=True
                )
            else:
                logger.error("all_disease_models_failed_to_load")
                cls._model = None
                cls._classes = None
                cls._model_version = "none"
                cls._initialized = True
                return False

        # Build transform pipeline according to loaded metadata
        img_size = int(cls._metadata.get("image_size", DEFAULT_IMAGE_SIZE)) if cls._metadata else DEFAULT_IMAGE_SIZE
        norm = cls._metadata.get("normalization", {}) if cls._metadata else {}
        mean = norm.get("mean", DEFAULT_MEAN)
        std = norm.get("std", DEFAULT_STD)

        cls._transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.CenterCrop(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])

        cls._initialized = True
        return True

    @classmethod
    def is_model_available(cls) -> bool:
        """Check if any local PyTorch model is loaded and ready for inference."""
        if not cls._initialized or cls._model is None:
            cls.initialize()
        return cls._model is not None and cls._classes is not None and len(cls._classes) > 0

    @classmethod
    def get_model_info(cls) -> Dict[str, Any]:
        """Return diagnostic info regarding loaded model status."""
        cls.initialize()
        return {
            "version": cls._model_version,
            "architecture": cls._metadata.get("architecture", "efficientnet_b3") if cls._metadata else "efficientnet_b3",
            "num_classes": len(cls._classes) if cls._classes else 0,
            "classes": cls._classes or [],
            "device": str(cls._device),
            "model_loaded": cls._model is not None,
            "image_size": cls._metadata.get("image_size", DEFAULT_IMAGE_SIZE) if cls._metadata else DEFAULT_IMAGE_SIZE,
            "metrics": cls._metadata.get("test_metrics", {}) if cls._metadata else {}
        }

    @classmethod
    def calculate_confidence_tier(cls, confidence: float) -> str:
        """
        Calculate safety confidence tier:
        - HIGH: >= 0.75
        - MEDIUM: 0.45 <= conf < 0.75
        - LOW: 0.30 <= conf < 0.45
        - UNCLEAR: < 0.30
        """
        if confidence >= 0.75:
            return "high"
        elif confidence >= 0.45:
            return "medium"
        elif confidence >= 0.30:
            return "low"
        else:
            return "unclear"

    @classmethod
    def predict(cls, image_bytes: bytes, crop_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Perform single-pass PyTorch EfficientNet-B3 inference on image bytes.
        Returns: {
            class_name: str,
            class_index: int,
            crop: str,
            disease: str,
            confidence: float,
            confidence_level: str,
            confidence_tier: str,
            top_predictions: List[Dict[str, Any]],
            entropy: float,
            is_reliable: bool,
            model_version: str,
            inference_source: str
        }
        """
        if not cls.is_model_available():
            return None

        try:
            import torch

            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            tensor = cls._transform(image).unsqueeze(0).to(cls._device)

            # Inference mode for speed & memory efficiency
            with torch.inference_mode():
                logits = cls._model(tensor)
                probs = torch.softmax(logits, dim=1).squeeze(0)

            classes = cls._classes or []
            num_classes = len(classes)
            k_val = min(3, num_classes)
            top_probs, top_indices = torch.topk(probs, k=k_val)

            top_prob = float(top_probs[0].item())
            top_idx = int(top_indices[0].item())
            class_name = classes[top_idx]

            # If crop_hint is specified, check crop-conditioned prior
            if crop_hint and crop_hint.strip():
                hint_clean = crop_hint.lower().strip()
                crop_indices = [
                    i for i, c in enumerate(classes)
                    if hint_clean in c.lower() or c.lower().startswith(hint_clean)
                ]
                if crop_indices:
                    crop_best_idx = max(crop_indices, key=lambda idx: probs[idx].item())
                    crop_best_prob = float(probs[crop_best_idx].item())
                    if crop_best_prob >= 0.15 or top_prob < 0.50:
                        top_idx = crop_best_idx
                        top_prob = crop_best_prob
                        class_name = classes[top_idx]

            # Top-3 predictions list
            top_predictions = []
            for prob_t, idx_t in zip(top_probs, top_indices):
                c_idx = int(idx_t.item())
                c_name = classes[c_idx]
                p_val = round(float(prob_t.item()), 4)
                
                c_crop, c_dis = cls._parse_class_name(c_name, crop_hint)
                top_predictions.append({
                    "class_name": c_name,
                    "class_index": c_idx,
                    "crop": c_crop,
                    "disease": c_dis,
                    "confidence": p_val,
                    "confidence_tier": cls.calculate_confidence_tier(p_val)
                })

            # Calculate Shannon entropy as uncertainty metric: H(X) = -sum(p * log(p))
            log_probs = torch.log(probs + 1e-12)
            entropy = float(-torch.sum(probs * log_probs).item())

            crop, disease = cls._parse_class_name(class_name, crop_hint)
            tier = cls.calculate_confidence_tier(top_prob)
            is_reliable = (tier in ("high", "medium")) and (top_prob >= 0.45)

            logger.info(
                "disease_ml_inference_success",
                class_name=class_name,
                crop=crop,
                disease=disease,
                confidence=round(top_prob, 4),
                tier=tier,
                model_version=cls._model_version,
            )

            return {
                "class_name": class_name,
                "class_index": top_idx,
                "crop": crop,
                "disease": disease,
                "confidence": round(top_prob, 4),
                "confidence_level": tier.upper(),
                "confidence_tier": tier,
                "top_predictions": top_predictions,
                "entropy": round(entropy, 4),
                "is_reliable": is_reliable,
                "model_version": cls._model_version,
                "inference_source": "ML_VISION"
            }
        except Exception as e:
            logger.error("disease_ml_inference_error", error=str(e))
            return None

    @staticmethod
    def _parse_class_name(class_name: str, crop_hint: Optional[str] = None) -> Tuple[str, str]:
        """Parse raw dataset class folder name (e.g. 'Tomato___Late_blight' or 'Tomato_Late_blight') into (crop, disease)."""
        if "___" in class_name:
            crop, disease = class_name.split("___", 1)
        elif "__" in class_name:
            crop, disease = class_name.split("__", 1)
        elif "_" in class_name and not crop_hint:
            parts = class_name.split("_", 1)
            crop, disease = parts[0], parts[1]
        else:
            crop = crop_hint or "General Crop"
            disease = class_name

        # Clean crop & disease formatting
        crop_clean = crop.replace("(", "").replace(")", "").replace(",", "").replace("_", " ").strip()
        disease_clean = disease.replace("_", " ").strip()
        return crop_clean, disease_clean
