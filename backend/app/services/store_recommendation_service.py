"""Curated Agri Store recommendations with Amazon India search links (no PA-API required)."""
from __future__ import annotations

import re
from typing import List, Optional
from urllib.parse import quote_plus

AMAZON_IN_SEARCH = "https://www.amazon.in/s?k={q}"

# Stable Unsplash crops (400px)
IMG = {
    "wheat": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&q=80",
    "rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&q=80",
    "onion": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400&q=80",
    "mustard": "https://images.unsplash.com/photo-1563223023-eb56e696fbe5?w=400&q=80",
    "potato": "https://images.unsplash.com/photo-1518977673343-a4a623db80db?w=400&q=80",
    "tomato": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&q=80",
    "cotton": "https://images.unsplash.com/photo-1625246333195-f89889981f88?w=400&q=80",
    "generic": "https://images.unsplash.com/photo-1595856403248-12c5bda25b90?w=400&q=80",
    "seeds": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&q=80",
    "fertilizer": "https://images.unsplash.com/photo-1625246333195-f89889981f88?w=400&q=80",
    "spray": "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400&q=80",
}


def _amz(q: str) -> str:
    return AMAZON_IN_SEARCH.format(q=quote_plus(q))


def _norm(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return " ".join(s.split())


class StoreRecommendationService:
    @staticmethod
    def build(
        source: str,
        crop: Optional[str] = None,
        disease_name: Optional[str] = None,
        crop_hint: Optional[str] = None,
    ) -> dict:
        source = (source or "browse").lower().strip()
        if source == "crop":
            return {"success": True, "source": source, "items": StoreRecommendationService._for_crop(crop or "")}
        if source == "disease":
            return {
                "success": True,
                "source": source,
                "items": StoreRecommendationService._for_disease(disease_name or "", crop_hint),
            }
        return {"success": True, "source": "browse", "items": StoreRecommendationService._browse()}

    @staticmethod
    def _browse() -> List[dict]:
        return [
            {
                "title": "Organic NPK fertilizer",
                "subtitle": "Balanced nutrition for field crops",
                "category": "Fertilizer",
                "image_url": IMG["fertilizer"],
                "shop_url": _amz("NPK fertilizer organic farming India 50kg"),
            },
            {
                "title": "Certified wheat seeds",
                "subtitle": "High-yield varieties",
                "category": "Seeds",
                "image_url": IMG["wheat"],
                "shop_url": _amz("wheat seeds certified farming India"),
            },
            {
                "title": "Neem oil spray",
                "subtitle": "Organic pest care",
                "category": "Crop care",
                "image_url": IMG["spray"],
                "shop_url": _amz("neem oil for plants spray organic"),
            },
            {
                "title": "Garden hand tools set",
                "subtitle": "Daily farm & kitchen garden",
                "category": "Tools",
                "image_url": IMG["generic"],
                "shop_url": _amz("agriculture hand tools kit India"),
            },
        ]

    @staticmethod
    def _for_crop(crop: str) -> List[dict]:
        c = _norm(crop)
        if not c:
            return StoreRecommendationService._browse()
        # Use first meaningful token for display
        display = crop.strip()[:60]
        seed_q = f"{display} seeds certified organic farming India"
        fert_q = f"NPK fertilizer for {display} crop India"
        care_q = f"bio pesticide organic {display} plants India"
        mulch_q = f"mulch sheet agriculture {display} India"
        return [
            {
                "title": f"Best match: {display} seeds",
                "subtitle": "Certified / high germination — check reviews & seller rating",
                "category": "Seeds",
                "image_url": IMG.get("seeds") or IMG["generic"],
                "shop_url": _amz(seed_q),
            },
            {
                "title": f"Fertilizer for {display}",
                "subtitle": "NPK & micronutrients suited to your top recommendation",
                "category": "Fertilizer",
                "image_url": IMG["fertilizer"],
                "shop_url": _amz(fert_q),
            },
            {
                "title": f"Crop protection for {display}",
                "subtitle": "Organic neem / bio options (read label for your crop)",
                "category": "Protection",
                "image_url": IMG["spray"],
                "shop_url": _amz(care_q),
            },
            {
                "title": "Mulch & water-saving",
                "subtitle": "Supports soil moisture for long-season crops",
                "category": "Supplies",
                "image_url": IMG["generic"],
                "shop_url": _amz(mulch_q),
            },
        ]

    @staticmethod
    def _for_disease(disease_name: str, crop_hint: Optional[str]) -> List[dict]:
        d = _norm(disease_name)
        ch = _norm(crop_hint or "")
        items: List[dict] = []

        fungal = any(
            x in d
            for x in (
                "rust",
                "mildew",
                "blight",
                "rot",
                "fungal",
                "fungus",
                "spot",
                "smut",
                "anthracnose",
                "downy",
                "powdery",
            )
        )
        insect = any(x in d for x in ("borer", "worm", "caterpillar", "aphid", "jassid", "whitefly", "mite", "insect", "pest"))
        bacterial = any(x in d for x in ("bacterial", "wilt", "canker", "leaf spot"))

        if fungal:
            items.append(
                {
                    "title": "Systemic / contact fungicide",
                    "subtitle": "Use as per label; wear PPE. Prefer extension-office advice.",
                    "category": "Treatment",
                    "image_url": IMG["spray"],
                    "shop_url": _amz(f"fungicide for plants {' '.join(filter(None, [ch, disease_name]))}".strip()),
                }
            )
            items.append(
                {
                    "title": "Copper oxychloride / Bordeaux mixture",
                    "subtitle": "Common for fungal spots & blights (follow dosage)",
                    "category": "Treatment",
                    "image_url": IMG["spray"],
                    "shop_url": _amz("copper oxychloride fungicide agriculture India"),
                }
            )

        if insect:
            items.append(
                {
                    "title": "Neem oil / bio insecticide",
                    "subtitle": "Organic-first option; rotate actives if needed",
                    "category": "Treatment",
                    "image_url": IMG["spray"],
                    "shop_url": _amz(f"neem oil insecticide plants {' '.join(filter(None, [ch]))}".strip()),
                }
            )

        if bacterial:
            items.append(
                {
                    "title": "Copper-based bactericide",
                    "subtitle": "Often used for bacterial leaf issues — confirm with local expert",
                    "category": "Treatment",
                    "image_url": IMG["spray"],
                    "shop_url": _amz("bactericide copper agriculture India"),
                }
            )

        # Always useful for diseased plants
        items.append(
            {
                "title": "Sticky traps & monitoring",
                "subtitle": "Helps confirm insect pressure in the field",
                "category": "Supplies",
                "image_url": IMG["generic"],
                "shop_url": _amz("yellow sticky trap agriculture insects"),
            }
        )
        items.append(
            {
                "title": "PPE: mask, gloves, goggles",
                "subtitle": "Essential when spraying chemicals",
                "category": "Safety",
                "image_url": IMG["generic"],
                "shop_url": _amz("pesticide spraying PPE kit gloves mask"),
            }
        )

        # De-duplicate by shop_url
        seen = set()
        out: List[dict] = []
        for it in items:
            u = it["shop_url"]
            if u not in seen:
                seen.add(u)
                out.append(it)

        if not out:
            q = " ".join(filter(None, [disease_name, crop_hint]))
            out = [
                {
                    "title": "Treatment search for your diagnosis",
                    "subtitle": disease_name[:120] if disease_name else "Agriculture crop care",
                    "category": "Treatment",
                    "image_url": IMG["spray"],
                    "shop_url": _amz(f"{q} agriculture treatment India"),
                },
                {
                    "title": "Neem oil for plants",
                    "subtitle": "Broad organic support for many issues",
                    "category": "Treatment",
                    "image_url": IMG["spray"],
                    "shop_url": _amz("neem oil for plants organic spray India"),
                },
            ]
        return out[:8]
