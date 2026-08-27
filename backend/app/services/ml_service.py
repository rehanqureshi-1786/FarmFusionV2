"""
ML Service - Crop Recommendation Inference (trained XGBoost V2 & V1 Fallback).

Loads the pre-trained XGBoost model, LabelEncoder, and Probability Calibrator exactly ONCE
at module import / first access (process lifetime) and reuses them for every request.
The trained artifacts under ``app/ml_models/`` are never modified.

PRIMARY MODEL (V2):
    - 57 Indian Crop Classes (SAU/ICAR Agro-Ecological Dataset grounded)
    - 10-feature vector with engineered stoichiometric and interaction features
    - Multi-class probability calibration via CalibratedClassifierCV

FALLBACK MODEL (V1):
    - 22-class baseline model loaded automatically if V2 is missing, corrupt, or incompatible.

FEATURE CONTRACT (must match training EXACTLY):
    1. N (kg/ha)
    2. P (kg/ha)
    3. K (kg/ha)
    4. temperature (°C)
    5. humidity (%)
    6. ph (0-14 scale)
    7. rainfall (mm seasonal)
    8. NPK_sum                = N + P + K
    9. N_to_P_ratio           = N / (P + 1e-6)
    10. temp_humidity_interaction = temperature * humidity / 100
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np

from app.core.config import get_settings, Settings

logger = logging.getLogger(__name__)

# Feature ordering as expected by the trained model (from crop_model_metadata_v2.json).
FEATURE_NAMES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
    "NPK_sum",
    "N_to_P_ratio",
    "temp_humidity_interaction",
]


class CropMLService:
    """
    Loads the trained XGBoost classifier, label encoder, and calibrator lazily (first call)
    and caches them for the process lifetime.
    """

    def __init__(self) -> None:
        self._model = None
        self._label_encoder = None
        self._calibrator = None
        self._metadata: Optional[Dict[str, Any]] = None
        self._is_v2: bool = False

    # ------------------------------------------------------------------ #
    # Loading & Verification
    # ------------------------------------------------------------------ #
    def _resolve_path(self, path_str: str) -> Path:
        p = Path(path_str)
        if not p.is_absolute():
            p = Path(__file__).resolve().parents[2] / p
        return p

    def _validate_v2_metadata(self, meta: Dict[str, Any], le: Any, model: Any) -> bool:
        """Validates that loaded V2 metadata and artifacts strictly match the production contract."""
        if not isinstance(meta, dict):
            return False

        version = meta.get("version", "")
        n_classes = meta.get("n_classes", 0)
        n_features = meta.get("n_features", 0)
        feature_names = meta.get("feature_names", [])

        if not str(version).startswith("2.0"):
            logger.warning("v2_metadata_validation_failed: unexpected version '%s'", version)
            return False

        if n_classes != 57 or len(getattr(le, "classes_", [])) != 57:
            logger.warning(
                "v2_metadata_validation_failed: expected 57 classes, got meta=%s, encoder=%s",
                n_classes,
                len(getattr(le, "classes_", [])),
            )
            return False

        if n_features != 10 or feature_names != FEATURE_NAMES:
            logger.warning(
                "v2_metadata_validation_failed: feature mismatch meta_n=%s expected_n=10",
                n_features,
            )
            return False

        return True

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return

        settings: Settings = get_settings()
        v2_model_path = self._resolve_path(settings.crop_model_path)
        v2_encoder_path = self._resolve_path(settings.crop_label_encoder_path)
        v2_meta_path = self._resolve_path(settings.crop_model_metadata_path)
        v2_calibrator_path = v2_model_path.parent / "crop_model_v2_calibrator.joblib"

        loaded_v2 = False
        try:
            if v2_model_path.exists() and v2_encoder_path.exists() and v2_meta_path.exists():
                model = joblib.load(v2_model_path)
                le = joblib.load(v2_encoder_path)
                with open(v2_meta_path, "r", encoding="utf-8") as fh:
                    meta = json.load(fh)

                if self._validate_v2_metadata(meta, le, model):
                    self._model = model
                    self._label_encoder = le
                    self._metadata = meta
                    self._is_v2 = True

                    # Attempt to load calibrator if available
                    if v2_calibrator_path.exists():
                        try:
                            self._calibrator = joblib.load(v2_calibrator_path)
                        except Exception as cal_err:
                            logger.warning("v2_calibrator_load_warning: %s, using base model", cal_err)
                            self._calibrator = None

                    loaded_v2 = True
                    logger.info(
                        "Crop ML V2 loaded successfully — %d classes, %d features",
                        len(self._label_encoder.classes_),
                        len(FEATURE_NAMES),
                    )
        except Exception as exc:
            logger.warning("v2_model_load_failed: %s", exc)

        if not loaded_v2:
            # Graceful Fallback to V1
            fallback_model_path = self._resolve_path(settings.crop_model_v1_path)
            fallback_encoder_path = self._resolve_path(settings.crop_label_encoder_v1_path)
            fallback_metadata_path = self._resolve_path(settings.crop_model_metadata_v1_path)

            logger.info("Crop ML V2 unavailable; using V1 fallback from %s", fallback_model_path)
            self._model = joblib.load(fallback_model_path)
            self._label_encoder = joblib.load(fallback_encoder_path)
            self._calibrator = None
            self._is_v2 = False
            try:
                with open(fallback_metadata_path, "r", encoding="utf-8") as fh:
                    self._metadata = json.load(fh)
            except Exception:
                self._metadata = {"version": "1.0.0", "n_classes": len(self._label_encoder.classes_)}

            logger.info(
                "Crop ML V1 fallback loaded — %d classes",
                len(getattr(self._label_encoder, "classes_", [])),
            )

    @property
    def is_v2(self) -> bool:
        """True if Model V2 is actively loaded."""
        self._ensure_loaded()
        return self._is_v2

    @property
    def model_version(self) -> str:
        """Version string of the loaded model."""
        self._ensure_loaded()
        if self._metadata and "version" in self._metadata:
            return str(self._metadata["version"])
        return "2.0.0" if self._is_v2 else "1.0.0"

    @property
    def label_encoder(self) -> Any:
        """Return the active label encoder."""
        self._ensure_loaded()
        return self._label_encoder

    def is_available(self) -> bool:
        """True if trained artifacts are loaded and ready."""
        try:
            self._ensure_loaded()
            return self._model is not None and self._label_encoder is not None
        except Exception as exc:  # noqa: BLE001
            logger.exception("crop_ml_service_unavailable: %s", exc)
            return False

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Return loaded model metadata dictionary."""
        try:
            self._ensure_loaded()
            return self._metadata
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Feature Engineering & Strict Validation
    # ------------------------------------------------------------------ #
    @staticmethod
    def build_feature_vector(
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float,
    ) -> List[float]:
        """
        Validates inputs and builds the exact 10-feature vector expected by the model.
        Raises ValueError if any numeric input is NaN, infinite, or physically invalid.
        """
        raw_vals = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
        for val in raw_vals:
            if val is None or not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                raise ValueError(f"Invalid numeric input feature for Crop ML inference: {val}")

        n_val = float(nitrogen)
        p_val = float(phosphorus)
        k_val = float(potassium)
        temp_val = float(temperature)
        hum_val = float(humidity)
        ph_val = float(ph)
        rain_val = float(rainfall)

        # Physical sanity checks
        if n_val < 0 or p_val < 0 or k_val < 0:
            raise ValueError(f"Nutrient values must be non-negative (N:{n_val}, P:{p_val}, K:{k_val})")
        if not (0.0 <= ph_val <= 14.0):
            raise ValueError(f"Soil pH must be between 0.0 and 14.0, got: {ph_val}")
        if not (-20.0 <= temp_val <= 60.0):
            raise ValueError(f"Temperature out of plausible range: {temp_val}°C")
        if not (0.0 <= hum_val <= 100.0):
            raise ValueError(f"Relative humidity must be between 0 and 100%, got: {hum_val}")
        if rain_val < 0:
            raise ValueError(f"Rainfall/water requirement must be non-negative, got: {rain_val}")

        # Exact mathematical definitions
        npk_sum = n_val + p_val + k_val
        n_to_p_ratio = n_val / (p_val + 1e-6)
        temp_humidity_interaction = temp_val * hum_val / 100.0

        return [
            n_val,
            p_val,
            k_val,
            temp_val,
            hum_val,
            ph_val,
            rain_val,
            npk_sum,
            n_to_p_ratio,
            temp_humidity_interaction,
        ]

    # ------------------------------------------------------------------ #
    # Inference
    # ------------------------------------------------------------------ #
    def predict_proba(self, features_dict: Dict[str, float]) -> List[float]:
        """
        Returns full calibrated probability vector across all classes for a feature dictionary.
        """
        self._ensure_loaded()
        vec = self.build_feature_vector(
            nitrogen=features_dict.get("N", features_dict.get("nitrogen", 0.0)),
            phosphorus=features_dict.get("P", features_dict.get("phosphorus", 0.0)),
            potassium=features_dict.get("K", features_dict.get("potassium", 0.0)),
            temperature=features_dict.get("temperature", 25.0),
            humidity=features_dict.get("humidity", 70.0),
            ph=features_dict.get("ph", 6.5),
            rainfall=features_dict.get("rainfall", 800.0),
        )
        sample = np.asarray([vec], dtype=float)
        if self._calibrator is not None:
            proba = self._calibrator.predict_proba(sample)[0]
        else:
            proba = self._model.predict_proba(sample)[0]
        return [float(p) for p in proba]

    def predict_top_candidates(
        self,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Run calibrated inference and return the ``top_k`` candidate crops with model probabilities.
        Returns a list of dicts:
            {"crop_name": str, "model_class_id": int, "probability": float}
        """
        self._ensure_loaded()

        features = self.build_feature_vector(
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
        )

        sample = np.asarray([features], dtype=float)

        # Use probability calibrator if loaded, otherwise base model
        if self._calibrator is not None:
            proba = self._calibrator.predict_proba(sample)[0]
        else:
            proba = self._model.predict_proba(sample)[0]

        order = np.argsort(proba)[::-1][:top_k]

        candidates: List[Dict[str, Any]] = []
        for idx in order:
            class_idx = int(idx)
            crop_name = str(self._label_encoder.classes_[class_idx])
            probability = float(proba[class_idx])
            candidates.append(
                {
                    "crop_name": crop_name,
                    "model_class_id": class_idx,
                    "probability": round(probability, 5),
                }
            )
        return candidates


# Module-level singleton: artifacts are loaded once and reused for the process lifetime.
crop_ml_service = CropMLService()