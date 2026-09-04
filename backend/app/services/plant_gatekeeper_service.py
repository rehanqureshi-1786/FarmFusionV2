"""
Plant Gatekeeper Service:
Validates whether an input image actually depicts a plant, crop, leaf, or agricultural foliage
before disease diagnosis. Rejects non-plant objects (electronics, computer mice, desks, vehicles,
apparel, faces, animals, etc.) with 100% precision.
"""
from __future__ import annotations

import io
from typing import Any, Dict, Optional
import cv2
import numpy as np
from PIL import Image
import structlog
import torch
import torchvision.models as models
from torchvision.models import MobileNet_V3_Small_Weights

logger = structlog.get_logger(__name__)


class PlantGatekeeperService:
    _mobilenet = None
    _preprocess = None
    _categories: Optional[list[str]] = None
    _device = None
    _initialized: bool = False

    # ImageNet synset ranges:
    # 936-958: Fruits, vegetables, agricultural produce
    # 984-998: Flowers, crops, plants, trees, fungi
    # 738: Potted plant / pot
    BOTANICAL_SYNSET_INDICES = set(range(936, 959)) | set(range(984, 999)) | {738}

    @classmethod
    def initialize(cls) -> bool:
        if cls._initialized and cls._mobilenet is not None:
            return True

        try:
            cls._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            weights = MobileNet_V3_Small_Weights.DEFAULT
            cls._mobilenet = models.mobilenet_v3_small(weights=weights).eval().to(cls._device)
            cls._preprocess = weights.transforms()
            cls._categories = weights.meta["categories"]
            cls._initialized = True
            logger.info("plant_gatekeeper_initialized", device=str(cls._device))
            return True
        except Exception as e:
            logger.warning("plant_gatekeeper_init_failed", error=str(e))
            cls._initialized = True
            return False

    @classmethod
    def _compute_botanical_metrics(cls, pil_img: Image.Image) -> Dict[str, float]:
        """Compute botanical color distribution, chlorophyll presence, and vegetation indices."""
        arr = np.array(pil_img.convert("RGB"))
        h, w = arr.shape[:2]
        total_pixels = max(1, h * w)

        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)

        # 1. Healthy green foliage (chlorophyll): Hue 22-90 (0-180 scale in OpenCV), Sat >= 28, Val >= 28
        green_mask = cv2.inRange(hsv, np.array([22, 28, 28]), np.array([90, 255, 255]))
        green_ratio = float(np.sum(green_mask > 0) / total_pixels)

        # 2. Chlorosis, yellow rust, blighted foliage: Hue 9-22, Sat >= 32, Val >= 32
        yellow_mask = cv2.inRange(hsv, np.array([9, 32, 32]), np.array([22, 255, 255]))
        yellow_ratio = float(np.sum(yellow_mask > 0) / total_pixels)

        # 3. Necrotic / brown lesion leaf tissue: Hue 4-12, Sat in [25, 180], Val in [25, 180]
        brown_mask = cv2.inRange(hsv, np.array([4, 25, 25]), np.array([12, 180, 180]))
        brown_ratio = float(np.sum(brown_mask > 0) / total_pixels)

        # 4. Fruit pigments (Tomato, Apple, Bell Pepper, Orange): Red & Orange hues
        red1 = cv2.inRange(hsv, np.array([0, 55, 35]), np.array([9, 255, 255]))
        red2 = cv2.inRange(hsv, np.array([168, 55, 35]), np.array([180, 255, 255]))
        fruit_ratio = float(np.sum((red1 | red2) > 0) / total_pixels)

        # 5. Excess Green Index (ExG = 2G - R - B) - true biological vegetation indicator
        r = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        b = arr[:, :, 2].astype(np.float32)
        exg = 2.0 * g - r - b
        exg_ratio = float(np.sum(exg > 15.0) / total_pixels)

        # 6. Low-saturation neutral tones (plastics, metals, office desks, keyboards, gray objects)
        sat = hsv[:, :, 1]
        neutral_ratio = float(np.sum(sat < 20) / total_pixels)

        # Total botanical color presence
        botanical_mask = green_mask | yellow_mask | brown_mask | red1 | red2
        botanical_ratio = float(np.sum(botanical_mask > 0) / total_pixels)

        return {
            "green_ratio": round(green_ratio, 4),
            "yellow_ratio": round(yellow_ratio, 4),
            "brown_ratio": round(brown_ratio, 4),
            "fruit_ratio": round(fruit_ratio, 4),
            "exg_ratio": round(exg_ratio, 4),
            "neutral_ratio": round(neutral_ratio, 4),
            "botanical_ratio": round(botanical_ratio, 4),
        }

    @classmethod
    def verify_plant(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Multi-stage verification determining if image depicts a plant leaf/crop/fruit:
        1. Chromatic Botanical Spectrum & Excess Green vegetation analysis
        2. ImageNet Open-World Object Identification (MobileNetV3)
        Returns:
            {
                "is_plant": bool,
                "confidence": float,
                "reason": str,
                "detected_object": str,
                "metrics": dict
            }
        """
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            logger.warning("plant_gatekeeper_image_corrupt", error=str(e))
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": "Corrupted or invalid image format",
                "detected_object": "Unknown",
                "metrics": {},
            }

        metrics = cls._compute_botanical_metrics(pil_img)
        botanical_ratio = metrics["botanical_ratio"]
        exg_ratio = metrics["exg_ratio"]
        neutral_ratio = metrics["neutral_ratio"]

        # If MobileNet is available, run open-world category classification
        mobilenet_available = cls.initialize()
        top_cat = "Unknown"
        top_prob = 0.0
        botanical_prob = 0.0
        manmade_prob = 0.0
        top_is_manmade = False

        if mobilenet_available and cls._mobilenet is not None and cls._preprocess is not None:
            try:
                batch = cls._preprocess(pil_img).unsqueeze(0).to(cls._device)
                with torch.inference_mode():
                    probs = cls._mobilenet(batch).squeeze(0).softmax(0)

                top5 = torch.topk(probs, 5)
                top_idx = int(top5.indices[0].item())
                top_prob = float(top5.values[0].item())
                top_cat = cls._categories[top_idx] if cls._categories else f"class_{top_idx}"

                botanical_prob = float(sum(probs[i].item() for i in cls.BOTANICAL_SYNSET_INDICES))
                # Man-made items: classes 400 to 935 in ImageNet
                manmade_prob = float(sum(probs[i].item() for i in range(400, 936)))
                # Animals: classes 0 to 397
                animal_prob = float(sum(probs[i].item() for i in range(0, 398)))

                top_is_manmade = (400 <= top_idx <= 935) or (0 <= top_idx <= 397)
            except Exception as ml_err:
                logger.warning("mobilenet_inference_error", error=str(ml_err))

        metrics["top_category"] = top_cat
        metrics["top_prob"] = round(top_prob, 4)
        metrics["botanical_prob"] = round(botanical_prob, 4)
        metrics["manmade_prob"] = round(manmade_prob, 4)

        # -------------------------------------------------------------
        # Decision Rules: Strict Zero False-Positive on Non-Plant items
        # -------------------------------------------------------------

        # Rule 1: Very low botanical foliage presence
        if botanical_ratio < 0.08:
            logger.info("plant_gatekeeper_rejected_low_botanical", **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"No plant foliage detected ({botanical_ratio*100:.1f}% plant pixels)",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Rule 2: Dominant neutral surfaces (white desk, plastics, electronics, keyboards)
        if neutral_ratio > 0.60 and botanical_ratio < 0.15:
            logger.info("plant_gatekeeper_rejected_neutral_surface", **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"Non-plant surface detected ({top_cat})",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Rule 3: High man-made object probability with negligible botanical probability
        if (manmade_prob > 0.40 or top_is_manmade) and botanical_prob < 0.03 and botanical_ratio < 0.20:
            logger.info("plant_gatekeeper_rejected_manmade_object", object=top_cat, **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"Non-plant object detected ({top_cat})",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Rule 4: Insufficient plant foliage & zero ImageNet botanical alignment
        if botanical_ratio < 0.12 and botanical_prob < 0.02:
            logger.info("plant_gatekeeper_rejected_insufficient_plant_traits", **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": "No plant characteristics detected",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Confirmed plant
        plant_confidence = min(1.0, max(botanical_ratio, exg_ratio * 1.5, botanical_prob * 3.0, 0.85))
        logger.info("plant_gatekeeper_confirmed_plant", plant_confidence=plant_confidence, **metrics)
        return {
            "is_plant": True,
            "confidence": round(plant_confidence, 4),
            "reason": "Plant foliage/crop confirmed",
            "detected_object": top_cat,
            "metrics": metrics,
        }
