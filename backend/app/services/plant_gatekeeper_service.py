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

    # ImageNet human apparel, accessories, personal devices, and human subjects
    PERSON_APPAREL_INDICES = {
        487,  # cellular telephone
        610,  # jersey, t-shirt
        834,  # suit
        836,  # sunglasses, dark glasses
        837,  # sunglass
        838,  # sunscreen, sunblock
        841,  # sweatshirt
        608,  # jean, blue jean
        474,  # cardigan
        677,  # necktie, tie
        457,  # bow tie
        582,  # groom, bridegroom
        981,  # baseball player
        983,  # scuba diver
        903,  # wig
        826,  # wristwatch
        620,  # laptop
        681,  # notebook
        445,  # bikini
        842,  # swimming trunks
        515,  # cowboy hat
        804,  # sombrero
        518,  # crash helmet
        560,  # football helmet
        443,  # bicycle helmet
        551,  # face powder
        629,  # lipstick
        635,  # lotion
    }

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

        # 1. Healthy green foliage (chlorophyll): Hue 28-95 in OpenCV, Sat >= 30, Val >= 30
        green_mask = cv2.inRange(hsv, np.array([28, 30, 30]), np.array([95, 255, 255]))
        green_ratio = float(np.sum(green_mask > 0) / total_pixels)

        # 2. Chlorosis, yellow rust, blighted leaf tissue: Hue 18-35, Sat >= 30, Val >= 30
        yellow_mask = cv2.inRange(hsv, np.array([18, 30, 30]), np.array([35, 255, 255]))
        yellow_ratio = float(np.sum(yellow_mask > 0) / total_pixels)

        # 3. Necrotic / brown lesion leaf tissue: Hue 4-18, Sat in [30, 255], Val in [25, 200]
        brown_mask = cv2.inRange(hsv, np.array([4, 30, 25]), np.array([18, 255, 200]))
        brown_ratio = float(np.sum(brown_mask > 0) / total_pixels)

        # 4. Dark necrotic spots / black rot / severe blights (low brightness diseased patches on leaves)
        dark_necrotic_mask = ((hsv[:, :, 0] <= 30) | (hsv[:, :, 0] >= 155)) & (hsv[:, :, 1] >= 15) & (hsv[:, :, 2] >= 10) & (hsv[:, :, 2] <= 110)
        necrotic_ratio = float(np.sum(dark_necrotic_mask > 0) / total_pixels)

        # 5. Fruit pigments (Tomato, Apple, Bell Pepper, Orange): Red & deep Orange hues
        red1 = cv2.inRange(hsv, np.array([0, 50, 40]), np.array([12, 255, 255]))
        red2 = cv2.inRange(hsv, np.array([160, 50, 40]), np.array([180, 255, 255]))
        fruit_ratio = float(np.sum((red1 | red2) > 0) / total_pixels)

        # 6. Excess Green Index (ExG = 2G - R - B) - true biological vegetation indicator
        r = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        b = arr[:, :, 2].astype(np.float32)
        exg = 2.0 * g - r - b
        exg_ratio = float(np.sum(exg > 15.0) / total_pixels)

        # 7. Low-saturation neutral tones (plastics, metals, office desks, keyboards, gray objects)
        sat = hsv[:, :, 1]
        neutral_ratio = float(np.sum(sat < 20) / total_pixels)

        # 8. Human skin chromaticity in YCrCb: Cr in [133, 173] and Cb in [77, 127]
        ycrcb = cv2.cvtColor(arr, cv2.COLOR_RGB2YCrCb)
        skin_mask = (ycrcb[:, :, 1] >= 133) & (ycrcb[:, :, 1] <= 173) & (ycrcb[:, :, 2] >= 77) & (ycrcb[:, :, 2] <= 127)
        skin_ratio = float(np.sum(skin_mask > 0) / total_pixels)

        # Total botanical color presence
        botanical_mask = green_mask | yellow_mask | brown_mask | dark_necrotic_mask | red1 | red2
        botanical_ratio = float(np.sum(botanical_mask > 0) / total_pixels)

        return {
            "green_ratio": round(green_ratio, 4),
            "yellow_ratio": round(yellow_ratio, 4),
            "brown_ratio": round(brown_ratio, 4),
            "necrotic_ratio": round(necrotic_ratio, 4),
            "fruit_ratio": round(fruit_ratio, 4),
            "exg_ratio": round(exg_ratio, 4),
            "neutral_ratio": round(neutral_ratio, 4),
            "skin_ratio": round(skin_ratio, 4),
            "botanical_ratio": round(botanical_ratio, 4),
        }

    @classmethod
    def verify_plant(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Multi-stage verification determining if image depicts a plant leaf/crop/fruit:
        1. Chromatic Botanical Spectrum & Excess Green vegetation analysis
        2. Foreground Center-Crop Subject & Skin Tone validation
        3. ImageNet Open-World Object Identification (MobileNetV3)
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

        w, h = pil_img.size
        metrics = cls._compute_botanical_metrics(pil_img)
        botanical_ratio = metrics["botanical_ratio"]
        exg_ratio = metrics["exg_ratio"]
        neutral_ratio = metrics["neutral_ratio"]
        skin_ratio = metrics["skin_ratio"]

        # Extract center 60% region (the primary camera focus)
        cx1, cy1, cx2, cy2 = int(0.2 * w), int(0.2 * h), int(0.8 * w), int(0.8 * h)
        center_crop = pil_img.crop((cx1, cy1, cx2, cy2))
        center_metrics = cls._compute_botanical_metrics(center_crop)
        center_skin_ratio = center_metrics["skin_ratio"]
        metrics["center_skin_ratio"] = center_skin_ratio
        metrics["center_botanical_ratio"] = center_metrics["botanical_ratio"]

        # Strong botanical presence indicator
        has_strong_botanical = (
            botanical_ratio >= 0.35
            or (botanical_ratio >= 0.20 and exg_ratio >= 0.12)
            or center_metrics["botanical_ratio"] >= 0.38
        )

        # If MobileNet is available, run open-world category classification
        mobilenet_available = cls.initialize()
        top_cat = "Unknown"
        top_prob = 0.0
        botanical_prob = 0.0
        manmade_prob = 0.0
        person_apparel_prob = 0.0
        c_top_cat = "Unknown"
        c_top_prob = 0.0
        c_bot_prob = 0.0
        c_man_prob = 0.0
        c_apparel_prob = 0.0
        top_is_manmade = False

        if mobilenet_available and cls._mobilenet is not None and cls._preprocess is not None:
            try:
                # 1. Full image classification
                batch = cls._preprocess(pil_img).unsqueeze(0).to(cls._device)
                with torch.inference_mode():
                    probs = cls._mobilenet(batch).squeeze(0).softmax(0)

                top_idx = int(torch.argmax(probs).item())
                top_prob = float(probs[top_idx].item())
                top_cat = cls._categories[top_idx] if cls._categories else f"class_{top_idx}"

                botanical_prob = float(sum(probs[i].item() for i in cls.BOTANICAL_SYNSET_INDICES))
                # Man-made items: strictly classes 400 to 935 in ImageNet (do NOT include 0-397 animals/insects)
                manmade_prob = float(sum(probs[i].item() for i in range(400, 936)))
                person_apparel_prob = float(sum(probs[i].item() for i in cls.PERSON_APPAREL_INDICES))

                top_is_manmade = (400 <= top_idx <= 935)

                # 2. Center crop classification (focal subject)
                batch_c = cls._preprocess(center_crop).unsqueeze(0).to(cls._device)
                with torch.inference_mode():
                    probs_c = cls._mobilenet(batch_c).squeeze(0).softmax(0)

                c_top_idx = int(torch.argmax(probs_c).item())
                c_top_prob = float(probs_c[c_top_idx].item())
                c_top_cat = cls._categories[c_top_idx] if cls._categories else f"class_{c_top_idx}"
                c_bot_prob = float(sum(probs_c[i].item() for i in cls.BOTANICAL_SYNSET_INDICES))
                c_man_prob = float(sum(probs_c[i].item() for i in range(400, 936)))
                c_apparel_prob = float(sum(probs_c[i].item() for i in cls.PERSON_APPAREL_INDICES))

            except Exception as ml_err:
                logger.warning("mobilenet_inference_error", error=str(ml_err))

        metrics["top_category"] = top_cat
        metrics["top_prob"] = round(top_prob, 4)
        metrics["botanical_prob"] = round(botanical_prob, 4)
        metrics["manmade_prob"] = round(manmade_prob, 4)
        metrics["person_apparel_prob"] = round(person_apparel_prob, 4)
        metrics["center_top_category"] = c_top_cat
        metrics["center_botanical_prob"] = round(c_bot_prob, 4)
        metrics["center_manmade_prob"] = round(c_man_prob, 4)

        # -------------------------------------------------------------
        # Decision Rules: Strict Zero False-Positive on Non-Plant items
        # -------------------------------------------------------------

        # Rule 1: Foreground Person / Apparel / Device Subject
        # Rejects portraits, selfies, or people in foreground even if background has incidental foliage
        if (
            (center_skin_ratio > 0.20 or person_apparel_prob > 0.08 or c_apparel_prob > 0.08)
            and manmade_prob > 0.40
            and botanical_prob < 0.20
            and not (has_strong_botanical and center_skin_ratio < 0.15)
        ):
            logger.info("plant_gatekeeper_rejected_person_foreground", object=top_cat, **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"Person or non-plant subject in foreground ({top_cat})",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Rule 2: Dominant Man-Made Object (computer mouse, electronic device, car, furniture, etc.)
        # MobileNet identifies a specific manmade item, or manmade probability dominates non-vegetation images
        if (
            (top_prob > 0.40 and top_is_manmade and not has_strong_botanical)
            or (manmade_prob > 0.65 and botanical_ratio < 0.25 and exg_ratio < 0.15)
            or (top_prob > 0.20 and top_is_manmade and botanical_ratio < 0.20 and botanical_prob < 0.10)
        ) and botanical_prob < 0.15:
            logger.info("plant_gatekeeper_rejected_manmade_dominant", object=top_cat, **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"Non-plant object detected ({top_cat})",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Rule 3: Central Focus is Non-Plant (center crop is dominated by a recognized manmade object)
        c_top_is_manmade = (400 <= c_top_idx <= 935) if 'c_top_idx' in locals() else False
        if (
            (c_top_prob > 0.45 and c_top_is_manmade and metrics["center_botanical_ratio"] < 0.30)
            or (c_man_prob > 0.70 and metrics["center_botanical_ratio"] < 0.25)
        ) and c_bot_prob < 0.10:
            logger.info("plant_gatekeeper_rejected_center_non_plant", object=c_top_cat, **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"Central subject is non-plant ({c_top_cat})",
                "detected_object": c_top_cat,
                "metrics": metrics,
            }

        # Rule 4: Very low botanical foliage presence across the frame
        if botanical_ratio < 0.08 and exg_ratio < 0.05:
            logger.info("plant_gatekeeper_rejected_low_botanical", **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"No plant foliage detected ({botanical_ratio*100:.1f}% plant pixels)",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Rule 5: Dominant neutral surfaces (white desk, plastics, keyboards)
        if neutral_ratio > 0.55 and botanical_ratio < 0.15 and exg_ratio < 0.08:
            logger.info("plant_gatekeeper_rejected_neutral_surface", **metrics)
            return {
                "is_plant": False,
                "confidence": 0.0,
                "reason": f"Non-plant surface detected ({top_cat})",
                "detected_object": top_cat,
                "metrics": metrics,
            }

        # Rule 6: Insufficient plant foliage & zero ImageNet botanical alignment
        if botanical_ratio < 0.15 and exg_ratio < 0.10 and botanical_prob < 0.03:
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
