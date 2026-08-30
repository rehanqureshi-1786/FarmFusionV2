"""
FarmFusion Canonical Semantic Layer.
Provides a language-independent structured representation for all agricultural intents and typed entities.
All languages and dialects map to this common semantic representation before invoking FarmFusion tools.
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CanonicalIntent(str, Enum):
    WEATHER = "weather"
    CROP_RECOMMENDATION = "crop_recommendation"
    MANDI = "mandi"
    DISEASE = "disease"
    SCHEME = "scheme"
    SOIL = "soil"
    CROP_CARE = "crop_care"
    NAVIGATION = "navigation"
    REPEAT_LAST = "repeat_last"
    SPEECH_CONTROL = "speech_control"
    WHAT_IF = "what_if"
    GREETING_HELP = "greeting_help"
    CONSEQUENTIAL_ACTION = "consequential_action"
    LANGUAGE_PREFERENCE = "language_preference"
    DIALECT_PREFERENCE = "dialect_preference"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    UNKNOWN = "unknown"


class WaterAvailability(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SoilType(str, Enum):
    BLACK_SOIL = "BLACK_SOIL"
    SANDY_SOIL = "SANDY_SOIL"
    RED_SOIL = "RED_SOIL"
    ALLUVIAL_SOIL = "ALLUVIAL_SOIL"
    CLAY_SOIL = "CLAY_SOIL"
    LOAMY_SOIL = "LOAMY_SOIL"


class CanonicalCrop(str, Enum):
    PEARL_MILLET = "PEARL_MILLET"  # बाजरा, बाजरी, बाजरो, Bajra, Pearl Millet
    WHEAT = "WHEAT"                # गेहूं, कनक, Wheat
    MUSTARD = "MUSTARD"            # सरसों, राई, Mustard
    COTTON = "COTTON"              # कपास, रुई, Cotton
    GROUNDNUT = "GROUNDNUT"        # मूंगफली, सींगदाना, Groundnut, Peanut
    SOYBEAN = "SOYBEAN"            # सोयाबीन, Soybean
    PADDY = "PADDY"                # धान, चावल, Paddy, Rice
    MAIZE = "MAIZE"                # मक्का, मक्की, Maize, Corn
    GRAM = "GRAM"                  # चना, ছোলা, Gram, Chickpea
    BARLEY = "BARLEY"              # जौ, Barley
    SUGARCANE = "SUGARCANE"        # गन्ना, Sugarcane
    PULSES = "PULSES"              # दालें, Pulses


class CanonicalAgriculturalEntities(BaseModel):
    crop: Optional[CanonicalCrop] = None
    crop_name_raw: Optional[str] = None
    water_availability: Optional[WaterAvailability] = None
    soil_type: Optional[SoilType] = None
    disease_name: Optional[str] = None
    fertilizer: Optional[str] = None
    operation: Optional[str] = None
    scheme_name: Optional[str] = None
    location: Optional[str] = None
    mandi_name: Optional[str] = None
    destination_screen: Optional[str] = None
    speech_speed: Optional[str] = None
    target_language: Optional[str] = None
    target_dialect: Optional[str] = None
    rainfall_modifier: Optional[str] = None
    additional_slots: Dict[str, Any] = Field(default_factory=dict)


class ConfidenceBreakdown(BaseModel):
    asr_confidence: float = 1.0
    language_confidence: float = 1.0
    dialect_confidence: Optional[float] = None
    intent_confidence: float = 0.85
    entity_confidence: float = 0.85
    overall_confidence: float = 0.85


class CanonicalSemanticFrame(BaseModel):
    """
    Language-independent semantic representation of farmer speech/text.
    Consistently consumed by FarmFusion's typed ToolRegistry.
    """
    raw_input: str
    detected_language: str = "hi"
    detected_dialect: Optional[str] = None
    intent: CanonicalIntent = CanonicalIntent.UNKNOWN
    entities: CanonicalAgriculturalEntities = Field(default_factory=CanonicalAgriculturalEntities)
    confidence: float = 0.85
    confidence_breakdown: ConfidenceBreakdown = Field(default_factory=ConfidenceBreakdown)
    safety_classification: str = "READ_ONLY" # READ_ONLY or CONSEQUENTIAL
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    source_layer: str = "LOCAL_FAST_PATH"     # LOCAL_FAST_PATH, MULTILINGUAL_CASCADE, CLOUD_FALLBACK


# ============================================================================
# CANONICAL VOCABULARY MAPPER
# ============================================================================

SURFACE_TO_CANONICAL_CROP: Dict[str, CanonicalCrop] = {
    # Pearl Millet (Bajra)
    "बाजरा": CanonicalCrop.PEARL_MILLET,
    "बाजरी": CanonicalCrop.PEARL_MILLET,
    "बाजरो": CanonicalCrop.PEARL_MILLET,
    "bajra": CanonicalCrop.PEARL_MILLET,
    "pearl millet": CanonicalCrop.PEARL_MILLET,
    "kambu": CanonicalCrop.PEARL_MILLET,
    "sajje": CanonicalCrop.PEARL_MILLET,
    "bajri": CanonicalCrop.PEARL_MILLET,

    # Wheat
    "गेहूं": CanonicalCrop.WHEAT,
    "गेंहू": CanonicalCrop.WHEAT,
    "कनक": CanonicalCrop.WHEAT,
    "कणक": CanonicalCrop.WHEAT,
    "wheat": CanonicalCrop.WHEAT,
    "godhumai": CanonicalCrop.WHEAT,
    "godhi": CanonicalCrop.WHEAT,
    "gehu": CanonicalCrop.WHEAT,

    # Mustard
    "सरसों": CanonicalCrop.MUSTARD,
    "राई": CanonicalCrop.MUSTARD,
    "mustard": CanonicalCrop.MUSTARD,
    "sarson": CanonicalCrop.MUSTARD,
    "kadugu": CanonicalCrop.MUSTARD,
    "sasive": CanonicalCrop.MUSTARD,

    # Cotton
    "कपास": CanonicalCrop.COTTON,
    "कापूस": CanonicalCrop.COTTON,
    "रूई": CanonicalCrop.COTTON,
    "cotton": CanonicalCrop.COTTON,
    "kapas": CanonicalCrop.COTTON,
    "paruthi": CanonicalCrop.COTTON,
    "patthi": CanonicalCrop.COTTON,
    "hatti": CanonicalCrop.COTTON,

    # Groundnut
    "मूंगफली": CanonicalCrop.GROUNDNUT,
    "मूँगफली": CanonicalCrop.GROUNDNUT,
    "सींगदाना": CanonicalCrop.GROUNDNUT,
    "भूंगली": CanonicalCrop.GROUNDNUT,
    "groundnut": CanonicalCrop.GROUNDNUT,
    "peanut": CanonicalCrop.GROUNDNUT,
    "kadalai": CanonicalCrop.GROUNDNUT,
    "shenga": CanonicalCrop.GROUNDNUT,

    # Soybean
    "सोयाबीन": CanonicalCrop.SOYBEAN,
    "soybean": CanonicalCrop.SOYBEAN,
    "soyabean": CanonicalCrop.SOYBEAN,

    # Paddy / Rice
    "धान": CanonicalCrop.PADDY,
    "चावल": CanonicalCrop.PADDY,
    "ਝੋਨਾ": CanonicalCrop.PADDY,
    "paddy": CanonicalCrop.PADDY,
    "rice": CanonicalCrop.PADDY,
    "dhan": CanonicalCrop.PADDY,
    "nellu": CanonicalCrop.PADDY,
    "bhatta": CanonicalCrop.PADDY,

    # Maize
    "मक्का": CanonicalCrop.MAIZE,
    "मक्की": CanonicalCrop.MAIZE,
    "maize": CanonicalCrop.MAIZE,
    "corn": CanonicalCrop.MAIZE,
    "makka": CanonicalCrop.MAIZE,
    "makki": CanonicalCrop.MAIZE,
    "cholam": CanonicalCrop.MAIZE,
    "musukina jola": CanonicalCrop.MAIZE,

    # Gram / Chickpea
    "चना": CanonicalCrop.GRAM,
    "चने": CanonicalCrop.GRAM,
    "ছোলা": CanonicalCrop.GRAM,
    "gram": CanonicalCrop.GRAM,
    "chickpea": CanonicalCrop.GRAM,
    "chana": CanonicalCrop.GRAM,
    "konda kadalai": CanonicalCrop.GRAM,
    "kadale": CanonicalCrop.GRAM,
}


def map_to_canonical_crop(surface_text: str) -> Optional[CanonicalCrop]:
    """Map any regional surface word to canonical crop enum."""
    text_lower = surface_text.lower().strip()
    if text_lower in SURFACE_TO_CANONICAL_CROP:
        return SURFACE_TO_CANONICAL_CROP[text_lower]
    for key, crop_enum in SURFACE_TO_CANONICAL_CROP.items():
        if key in text_lower:
            return crop_enum
    return None
