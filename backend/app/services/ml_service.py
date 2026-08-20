"""
ML Service - Crop Recommendation Inference (trained XGBoost).

Loads the pre-trained XGBoost model + LabelEncoder exactly ONCE at module import
(process lifetime) and reuses them for every request. The model is NOT retrained
here and the trained artifacts under ``app/ml_models/`` are never modified.

FEATURE ENGINEERING (must match training EXACTLY):
    NPK_sum                = N + P + K
    N_to_P_ratio           = N / (P + 1e-6)
    temp_humidity_interaction = temperature * humidity / 100

Input features (order fixed, 10 columns):
    N, P, K, temperature, humidity, ph, rainfall,
    NPK_sum, N_to_P_ratio, temp_humidity_interaction
"""
from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

import joblib
import numpy as np

from app.core.config import get_settings, Settings

logger = logging.getLogger(__name__)

# Feature ordering as expected by the trained model (from crop_model_metadata.json).
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
    Loads the trained XGBoost classifier and label encoder lazily (first call)
    and caches them for the process lifetime.
    """

    def __init__(self) -> None:
        self._model = None
        self._label_encoder = None
        self._metadata: Optional[Dict] = None

    # ------------------------------------------------------------------ #
    # Loading (once)
    # ------------------------------------------------------------------ #
    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        settings: Settings = get_settings()
        logger.info(
            "loading_crop_ml_artifacts model=%s encoder=%s",
            settings.crop_model_path,
            settings.crop_label_encoder_path,
        )
        self._model = joblib.load(settings.crop_model_path)
        self._label_encoder = joblib.load(settings.crop_label_encoder_path)
        try:
            with open(settings.crop_model_metadata_path, "r", encoding="utf-8") as fh:
                self._metadata = json.load(fh)
        except (OSError, json.JSONDecodeError):
            logger.warning("could_not_load_crop_metadata path=%s", settings.crop_model_metadata_path)
            self._metadata = None
        logger.info(
            "crop_ml_artifacts_loaded n_features=%s",
            getattr(self._model, "n_features_in_", None),
        )

    def is_available(self) -> bool:
        """True if the trained artifacts could be loaded (no-op otherwise)."""
        try:
            self._ensure_loaded()
            return True
        except Exception as exc:  # noqa: BLE001 - surface as unavailable
            logger.exception("crop_ml_service_unavailable: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    # Feature engineering (must remain EXACT)
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
    ) -> list:
        """Build the exact 10-feature vector expected by the model."""
        npk_sum = nitrogen + phosphorus + potassium
        n_to_p_ratio = nitrogen / (phosphorus + 1e-6)
        temp_humidity_interaction = temperature * humidity / 100.0
        return [
            nitrogen,
            phosphorus,
            potassium,
            temperature,
            humidity,
            ph,
            rainfall,
            npk_sum,
            n_to_p_ratio,
            temp_humidity_interaction,
        ]

    # ------------------------------------------------------------------ #
    # Inference
    # ------------------------------------------------------------------ #
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
    ) -> List[Dict]:
        """
        Run ``model.predict_proba`` and return the ``top_k`` candidate crops.

        The model's output column index maps directly onto the LabelEncoder
        ``classes_`` order (index 0 -> classes_[0], etc.).

        Returns a list of dicts:
            {"crop_name", "model_class_id", "probability"}
        """
        self._ensure_loaded()

        features = self.build_feature_vector(
            nitrogen, phosphorus, potassium,
            temperature, humidity, ph, rainfall,
        )
        proba = self._model.predict_proba(np.asarray([features], dtype=float))[0]
        order = np.argsort(proba)[::-1][:top_k]

        candidates: List[Dict] = []
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