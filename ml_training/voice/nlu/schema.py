"""
Canonical Schema & Intents for FarmFusion Agricultural Natural Language Understanding (NLU).
"""
from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class CanonicalIntent(str, Enum):
    WEATHER = "weather"
    CROP_RECOMMENDATION = "crop_recommendation"
    CROP_CARE = "crop_care"
    DISEASE = "disease"
    MANDI = "mandi"
    SCHEME = "scheme"
    SOIL = "soil"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    NAVIGATION = "navigation"
    REPEAT = "repeat_last"
    SPEECH_CONTROL = "speech_control"
    CLARIFICATION = "clarification"
    WHAT_IF = "what_if"
    GREETING_HELP = "greeting_help"
    CONSEQUENTIAL_ACTION = "consequential_action"
    LANGUAGE_PREFERENCE = "language_preference"
    DIALECT_PREFERENCE = "dialect_preference"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"


CANONICAL_SLOT_TYPES = {
    "crop": ["wheat", "rice", "cotton", "mustard", "pearl_millet", "gram", "maize", "groundnut", "soybean", "sugarcane"],
    "location": ["location_name", "district", "state", "pincode"],
    "soil_type": ["black_soil", "alluvial_soil", "red_soil", "sandy_soil", "clay_soil", "loamy_soil"],
    "commodity": ["wheat", "mustard", "cotton", "soybean", "chana", "paddy", "bajra"],
    "disease_name": ["blight", "rust", "tikka", "caterpillar", "whitefly"],
    "destination": ["home", "weather", "market_prices", "crop_recommendation", "disease_detection", "government_schemes"],
    "speech_rate": ["slow", "normal", "fast"],
}
