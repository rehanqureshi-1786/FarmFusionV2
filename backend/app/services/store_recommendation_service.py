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
        active_ingredients: Optional[List[str]] = None,
        product_categories: Optional[List[str]] = None,
    ) -> dict:
        source = (source or "browse").lower().strip()
        if source == "crop":
            return {"success": True, "source": source, "items": StoreRecommendationService._for_crop(crop or "")}
        if source == "disease":
            return {
                "success": True,
                "source": source,
                "items": StoreRecommendationService._for_disease(
                    disease_name or "",
                    crop_hint,
                    active_ingredients=active_ingredients,
                    product_categories=product_categories,
                ),
            }
        return {"success": True, "source": "browse", "items": StoreRecommendationService._browse()}

    @staticmethod
    def _for_disease(
        disease_name: str,
        crop_hint: Optional[str],
        active_ingredients: Optional[List[str]] = None,
        product_categories: Optional[List[str]] = None,
    ) -> List[dict]:
        d = _norm(disease_name)
        ch = _norm(crop_hint or "")
        items: List[dict] = []

        # 1. Targeted recommendations based on active ingredients from ICAR knowledge base
        if active_ingredients:
            for active in active_ingredients[:3]:
                act_norm = _norm(active)
                if not act_norm:
                    continue
                if "copper" in act_norm or "mancozeb" in act_norm or "metalaxyl" in act_norm:
                    items.append({
                        "title": f"{active} Formulation",
                        "subtitle": f"Recommended active ingredient for {disease_name}",
                        "category": "Fungicide / Bactericide",
                        "image_url": IMG["spray"],
                        "shop_url": _amz(f"{active} fungicide agriculture India 500g"),
                    })
                elif "streptocycline" in act_norm:
                    items.append({
                        "title": "Streptocycline Bactericide (90:10)",
                        "subtitle": f"Antibacterial agricultural formulation for {disease_name}",
                        "category": "Bactericide",
                        "image_url": IMG["spray"],
                        "shop_url": _amz("streptocycline agricultural bactericide India"),
                    })
                elif "propiconazole" in act_norm or "tebuconazole" in act_norm or "tricyclazole" in act_norm:
                    items.append({
                        "title": f"{active} Systemic Fungicide",
                        "subtitle": f"Effective against rusts and blights in {crop_hint or 'crops'}",
                        "category": "Systemic Fungicide",
                        "image_url": IMG["spray"],
                        "shop_url": _amz(f"{active} systemic fungicide agriculture India"),
                    })
                elif "trichoderma" in act_norm or "pseudomonas" in act_norm:
                    items.append({
                        "title": f"Bio-control {active}",
                        "subtitle": "Organic beneficial bio-fungicide for seed & soil treatment",
                        "category": "Bio-pesticide",
                        "image_url": IMG["fertilizer"],
                        "shop_url": _amz(f"{active} organic bio fungicide farming India"),
                    })
                elif "neem" in act_norm:
                    items.append({
                        "title": "Neem Oil 10000 PPM (Azadirachtin)",
                        "subtitle": "Organic bio-pesticide and insect vector deterrent",
                        "category": "Organic Crop Care",
                        "image_url": IMG["spray"],
                        "shop_url": _amz("neem oil 10000 ppm cold pressed agriculture India"),
                    })
                else:
                    items.append({
                        "title": f"{active} Crop Protection",
                        "subtitle": f"Targeted active ingredient for {disease_name}",
                        "category": "Crop Protection",
                        "image_url": IMG["spray"],
                        "shop_url": _amz(f"{active} agriculture plant care India"),
                    })

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
                "scab",
                "mold",
            )
        )
        insect = any(x in d for x in ("borer", "worm", "caterpillar", "aphid", "jassid", "whitefly", "mite", "insect", "pest", "spider"))
        bacterial = any(x in d for x in ("bacterial", "wilt", "canker", "blight", "spot"))

        if fungal and not items:
            items.append(
                {
                    "title": "Systemic / Contact Fungicide",
                    "subtitle": "Use as per label; wear PPE. Prefer extension-office advice.",
                    "category": "Fungicide",
                    "image_url": IMG["spray"],
                    "shop_url": _amz(f"fungicide for plants {' '.join(filter(None, [ch, disease_name]))}".strip()),
                }
            )
            items.append(
                {
                    "title": "Copper Oxychloride 50% WP",
                    "subtitle": "Broad-spectrum protection for fungal spots & blights",
                    "category": "Fungicide",
                    "image_url": IMG["spray"],
                    "shop_url": _amz("copper oxychloride 50 wp fungicide agriculture India"),
                }
            )

        if (insect or "curl_virus" in d or "yellow_leaf_curl" in d) and not any("neem" in it["title"].lower() for it in items):
            items.append(
                {
                    "title": "Neem Oil 10000 PPM Spray",
                    "subtitle": "Organic-first insect vector & mite control",
                    "category": "Bio-pesticide",
                    "image_url": IMG["spray"],
                    "shop_url": _amz(f"neem oil 10000 ppm insecticide plants {' '.join(filter(None, [ch]))}".strip()),
                }
            )
            items.append(
                {
                    "title": "Yellow Sticky Traps (Pack of 25)",
                    "subtitle": "Mass-trapping for whiteflies, aphids & thrips",
                    "category": "Vector Trapping",
                    "image_url": IMG["generic"],
                    "shop_url": _amz("yellow sticky traps agriculture whitefly traps"),
                }
            )

        if bacterial and not any("copper" in it["title"].lower() for it in items):
            items.append(
                {
                    "title": "Copper-based Agricultural Bactericide",
                    "subtitle": "Synergistic bacterial control formulation",
                    "category": "Bactericide",
                    "image_url": IMG["spray"],
                    "shop_url": _amz("copper oxychloride streptocycline agriculture India"),
                }
            )

        # Essential safety & application gear
        items.append(
            {
                "title": "Pesticide Spraying PPE Safety Kit",
                "subtitle": "Chemical-resistant mask, goggles, and nitrile gloves",
                "category": "Farmer Safety",
                "image_url": IMG["generic"],
                "shop_url": _amz("pesticide spraying PPE safety kit mask gloves goggles"),
            }
        )
        items.append(
            {
                "title": "16L Battery Knapsack Sprayer",
                "subtitle": "Continuous uniform pressure for foliar fungicide application",
                "category": "Application Equipment",
                "image_url": IMG["generic"],
                "shop_url": _amz("16 liter battery knapsack sprayer agriculture"),
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
        return out[:6]
