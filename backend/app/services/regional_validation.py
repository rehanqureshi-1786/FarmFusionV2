"""
Regional Validation Layer (separate from the ML model).

This is a deliberately lightweight, transparent scoring layer that adjusts a
candidate crop's ranking using known regional agronomic preferences. It is NOT
scientific proof of validity for "all India" — it is only a soft bonus/penalty
on top of the trained model, and it is neutral (score 1.0) when the state is
unknown or not provided.

The XGBoost model remains the source of crop probabilities; regional
validation only re-ranks those probabilities for the final top-3.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

# Per-state soft preference weights (multipliers applied to model probability).
# 1.0 = neutral, >1.0 = boost, <1.0 = penalty. Values are kept modest so the
# ML ranking is never fully overridden.
STATE_PREFERENCE: Dict[str, Dict[str, float]] = {
    "rajasthan": {
        "mothbeans": 1.3, "mungbean": 1.2, "blackgram": 1.2, "chickpea": 1.2,
        "pigeonpeas": 1.15, "lentil": 1.1, "maize": 1.05, "muskmelon": 1.15,
        "watermelon": 1.1, "cotton": 1.05,
        "rice": 0.6, "banana": 0.7, "coconut": 0.6, "coffee": 0.6,
        "orange": 0.9,
    },
    "punjab": {
        "rice": 1.1, "maize": 1.15, "chickpea": 1.15, "lentil": 1.1,
        "apple": 0.9, "banana": 0.8, "coffee": 0.6, "coconut": 0.7,
    },
    "haryana": {
        "maize": 1.1, "chickpea": 1.15, "lentil": 1.1, "cotton": 1.1,
        "rice": 1.05, "coffee": 0.6, "coconut": 0.7,
    },
    "uttar pradesh": {
        "rice": 1.2, "maize": 1.15, "chickpea": 1.1, "lentil": 1.15,
        "pigeonpeas": 1.1, "banana": 1.05, "mango": 1.1, "watermelon": 1.05,
        "coffee": 0.7, "coconut": 0.8,
    },
    "bihar": {
        "rice": 1.2, "maize": 1.15, "lentil": 1.2, "chickpea": 1.1,
        "jute": 1.1, "pigeonpeas": 1.1, "banana": 1.0,
        "coffee": 0.7, "coconut": 0.8,
    },
    "west bengal": {
        "rice": 1.25, "jute": 1.3, "lentil": 1.1, "banana": 1.1,
        "coffee": 0.8, "coconut": 1.0,
    },
    "assam": {
        "rice": 1.2, "jute": 1.1, "banana": 1.05,
        "coffee": 0.8, "coconut": 1.0,
    },
    "maharashtra": {
        "cotton": 1.25, "pigeonpeas": 1.15, "mungbean": 1.1,
        "blackgram": 1.1, "chickpea": 1.1, "banana": 1.15, "grapes": 1.2,
        "pomegranate": 1.15, "mango": 1.1, "muskmelon": 1.1, "watermelon": 1.05,
        "coffee": 0.9,
    },
    "karnataka": {
        "coffee": 1.25, "grapes": 1.2, "cotton": 1.15, "rice": 1.1,
        "maize": 1.15, "banana": 1.15, "mango": 1.1, "coconut": 1.1,
        "chickpea": 1.05, "pigeonpeas": 1.1, "blackgram": 1.05,
        "muskmelon": 1.05, "watermelon": 1.0,
    },
    "tamil nadu": {
        "rice": 1.2, "banana": 1.2, "coconut": 1.25, "cotton": 1.05,
        "maize": 1.1, "mango": 1.1, "blackgram": 1.05, "papaya": 1.1,
        "watermelon": 1.1, "coffee": 1.0,
    },
    "kerala": {
        "coconut": 1.3, "coffee": 1.05, "banana": 1.2, "rice": 1.1,
        "papaya": 1.1,
        "apple": 0.6,
    },
    "andhra pradesh": {
        "rice": 1.2, "cotton": 1.15, "mango": 1.1, "blackgram": 1.1,
        "mungbean": 1.05, "pigeonpeas": 1.1, "watermelon": 1.05,
        "coffee": 0.9,
    },
    "telangana": {
        "rice": 1.1, "cotton": 1.2, "maize": 1.15, "pigeonpeas": 1.1,
        "mango": 1.05,
        "coffee": 0.9, "coconut": 0.9,
    },
    "gujarat": {
        "cotton": 1.2, "mungbean": 1.15, "chickpea": 1.1, "blackgram": 1.1,
        "watermelon": 1.15, "muskmelon": 1.1,
        "rice": 0.85, "coconut": 0.9, "coffee": 0.8,
    },
    "madhya pradesh": {
        "chickpea": 1.2, "maize": 1.1, "pigeonpeas": 1.15, "mungbean": 1.1,
        "blackgram": 1.1, "lentil": 1.1, "cotton": 1.05,
        "coffee": 0.85, "coconut": 0.8,
    },
    "odisha": {
        "rice": 1.25, "jute": 1.05, "maize": 1.05, "banana": 1.0,
        "mungbean": 1.0, "blackgram": 1.0,
        "coffee": 0.85, "coconut": 0.9,
    },
}

# Broad-region fallbacks (used only when the specific state is unknown).
REGION_OF_STATE: Dict[str, str] = {
    # North
    "jammu and kashmir": "north", "himachal pradesh": "north",
    "uttarakhand": "north", "delhi": "north",
    # West
    "goa": "west", "rajasthan": "west", "gujarat": "west",
    # Central
    "chhattisgarh": "central", "maharashtra": "central",
    # South
    "kerala": "south", "karnataka": "south", "tamil nadu": "south",
    "andhra pradesh": "south", "telangana": "south",
    # East
    "west bengal": "east", "bihar": "east", "jharkhand": "east",
    "odisha": "east", "assam": "east", "sikkim": "east",
}

REGION_PREFERENCE: Dict[str, Dict[str, float]] = {
    "north": {"apple": 1.15, "chickpea": 1.1, "lentil": 1.1, "maize": 1.1,
              "rice": 1.05, "coffee": 0.7, "coconut": 0.7, "banana": 0.9},
    "west": {"cotton": 1.1, "mungbean": 1.1, "blackgram": 1.1, "chickpea": 1.1,
             "watermelon": 1.05, "muskmelon": 1.05, "rice": 0.85,
             "coffee": 0.85, "coconut": 0.9},
    "central": {"chickpea": 1.1, "pigeonpeas": 1.1, "maize": 1.1,
                "cotton": 1.1, "mungbean": 1.05},
    "south": {"rice": 1.1, "coconut": 1.15, "coffee": 1.1, "banana": 1.1,
              "mango": 1.05, "grapes": 1.05},
    "east": {"rice": 1.15, "jute": 1.15, "lentil": 1.05, "banana": 1.0,
             "coffee": 0.85, "coconut": 0.9},
}


def _preference_weight(state: str, crop: str) -> float:
    """Return the regional weight for a crop in a state (1.0 if unknown)."""
    key = (state or "").strip().lower()
    state_cfg = STATE_PREFERENCE.get(key)
    if state_cfg:
        return state_cfg.get(crop, 1.0)
    region = REGION_OF_STATE.get(key)
    if region:
        region_cfg = REGION_PREFERENCE.get(region)
        if region_cfg:
            return region_cfg.get(crop, 1.0)
    return 1.0


def apply(
    state: str,
    candidates: List[Dict],
    season: str,
) -> Tuple[List[Dict], List[str]]:
    """
    Re-rank ML candidates by ``probability * regional_weight``.

    Args:
        state: Optional state name (empty/None => neutral).
        candidates: list of {"crop_name", "probability", "model_class_id"}.
        season: current season name (informational only for now).

    Returns:
        (augmented_candidates, warnings)
        Each candidate gains "regional_score" (the multiplier) and "final_score".
    """
    warnings: List[str] = []
    state_key = (state or "").strip()
    if not state_key:
        warnings.append(
            "State not provided; regional validation kept neutral (score 1.0)."
        )
    elif state_key.lower() not in STATE_PREFERENCE and state_key.lower() not in REGION_OF_STATE:
        warnings.append(
            f"State '{state}' not recognized; regional validation kept neutral (score 1.0)."
        )

    ranked: List[Dict] = []
    for cand in candidates:
        crop = cand["crop_name"]
        weight = _preference_weight(state, crop)
        regional_score = round(weight, 4)
        final_score = round(float(cand["probability"]) * weight, 5)
        ranked.append({
            "crop_name": crop,
            "model_class_id": cand.get("model_class_id"),
            "model_probability": float(cand["probability"]),
            "regional_score": regional_score,
            "final_score": final_score,
        })

    ranked.sort(key=lambda item: item["final_score"], reverse=True)
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
    return ranked, warnings