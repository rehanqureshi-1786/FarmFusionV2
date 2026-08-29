"""
Language Registry and Agricultural Vocabulary Normalization for FarmFusion.
Data-driven configuration covering Tier 1 Indian scheduled languages and Tier 2 regional dialects.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class LanguageDefinition(BaseModel):
    code: str
    name: str
    native_name: str
    script: str
    parent_language: Optional[str] = None
    asr_supported: bool = True
    tts_supported: bool = True
    nlu_supported: bool = True
    response_supported: bool = True
    dialects: List[str] = Field(default_factory=list)
    bhashini_code: str


# Canonical Language Registry
SUPPORTED_LANGUAGES: Dict[str, LanguageDefinition] = {
    "hi": LanguageDefinition(
        code="hi",
        name="Hindi",
        native_name="हिन्दी",
        script="Devanagari",
        bhashini_code="hi",
        dialects=["mewari", "marwari", "bhojpuri", "awadhi", "haryanvi", "rajasthani"],
    ),
    "en": LanguageDefinition(
        code="en",
        name="English",
        native_name="English",
        script="Latin",
        bhashini_code="en",
        dialects=["indian_english"],
    ),
    "mr": LanguageDefinition(
        code="mr",
        name="Marathi",
        native_name="मराठी",
        script="Devanagari",
        bhashini_code="mr",
        dialects=["varhadi", "nagpuri"],
    ),
    "gu": LanguageDefinition(
        code="gu",
        name="Gujarati",
        native_name="ગુજરાતી",
        script="Gujarati",
        bhashini_code="gu",
        dialects=["kathiawari", "surati"],
    ),
    "pa": LanguageDefinition(
        code="pa",
        name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
        script="Gurmukhi",
        bhashini_code="pa",
        dialects=["majhi", "malwai"],
    ),
    "bn": LanguageDefinition(
        code="bn",
        name="Bengali",
        native_name="বাংলা",
        script="Bengali",
        bhashini_code="bn",
        dialects=["rhad", "banga"],
    ),
    "te": LanguageDefinition(
        code="te",
        name="Telugu",
        native_name="తెలుగు",
        script="Telugu",
        bhashini_code="te",
        dialects=["coastal", "rayalaseema", "telangana"],
    ),
    "ta": LanguageDefinition(
        code="ta",
        name="Tamil",
        native_name="தமிழ்",
        script="Tamil",
        bhashini_code="ta",
        dialects=["kongu", "madurai"],
    ),
    "kn": LanguageDefinition(
        code="kn",
        name="Kannada",
        native_name="ಕನ್ನಡ",
        script="Kannada",
        bhashini_code="kn",
        dialects=["mysore", "dharwad"],
    ),
    "ml": LanguageDefinition(
        code="ml",
        name="Malayalam",
        native_name="മലയാളം",
        script="Malayalam",
        bhashini_code="ml",
        dialects=["central", "travancore"],
    ),
    "or": LanguageDefinition(
        code="or",
        name="Odia",
        native_name="ଓଡ଼ିଆ",
        script="Odia",
        bhashini_code="or",
        dialects=["sambalpuri", "kataki"],
    ),
    "as": LanguageDefinition(
        code="as",
        name="Assamese",
        native_name="অসমীয়া",
        script="Assamese",
        bhashini_code="as",
        dialects=["kamrupi", "goalpariya"],
    ),
}

# Agricultural Vocabulary Normalization dictionary
CROP_SYNONYMS: Dict[str, str] = {
    # Wheat
    "गेहूं": "Wheat", "gehun": "Wheat", "gehu": "Wheat", "ghav": "Wheat", "kanak": "Wheat", "gothambu": "Wheat",
    # Rice / Paddy
    "धान": "Rice", "चावल": "Rice", "chawal": "Rice", "dhan": "Rice", "bhat": "Rice", "paddy": "Rice", "nellu": "Rice",
    # Groundnut / Peanut
    "मूंगफली": "Groundnut (Peanut)", "mungfali": "Groundnut (Peanut)", "moongphali": "Groundnut (Peanut)",
    "peanut": "Groundnut (Peanut)", "groundnut": "Groundnut (Peanut)", "singdana": "Groundnut (Peanut)", "kadale": "Groundnut (Peanut)",
    # Pearl Millet / Bajra
    "बाजरा": "Pearl Millet (Bajra)", "bajra": "Pearl Millet (Bajra)", "bajri": "Pearl Millet (Bajra)", "sajjalu": "Pearl Millet (Bajra)", "kambu": "Pearl Millet (Bajra)",
    # Cotton
    "कपास": "Cotton", "kapas": "Cotton", "rooi": "Cotton", "cotton": "Cotton", "patti": "Cotton",
    # Mustard
    "सरसों": "Mustard", "sarson": "Mustard", "rai": "Mustard", "mustard": "Mustard", "kadugu": "Mustard",
    # Soybean
    "सोयाबीन": "Soybean", "soyabean": "Soybean", "soybean": "Soybean",
    # Sugarcane
    "गन्ना": "Sugarcane", "ganna": "Sugarcane", "sherdi": "Sugarcane", "oos": "Sugarcane", "karumbu": "Sugarcane", "cheruku": "Sugarcane",
    # Chickpea / Chana
    "चना": "Chickpea (Gram)", "chana": "Chickpea (Gram)", "gram": "Chickpea (Gram)", "chickpea": "Chickpea (Gram)", "harbara": "Chickpea (Gram)",
    # Green Gram / Moong
    "मूंग": "Green Gram (Moong)", "moong": "Green Gram (Moong)", "mung": "Green Gram (Moong)", "pesalu": "Green Gram (Moong)",
    # Maize / Corn
    "मक्का": "Maize", "makka": "Maize", "makki": "Maize", "corn": "Maize", "maize": "Maize", "bhutta": "Maize", "jola": "Maize",
}

SOIL_SYNONYMS: Dict[str, str] = {
    "रेतीली": "Sandy Soil", "बलुई": "Sandy Soil", "sandy": "Sandy Soil", "retili": "Sandy Soil", "sand": "Sandy Soil",
    "काली": "Black Soil", "काली मिट्टी": "Black Soil", "black": "Black Soil", "regur": "Black Soil", "kali": "Black Soil",
    "लाल": "Red Soil", "लाल मिट्टी": "Red Soil", "red": "Red Soil", "laal": "Red Soil",
    "दोमट": "Alluvial Soil", "जलोढ़": "Alluvial Soil", "alluvial": "Alluvial Soil", "loam": "Alluvial Soil", "domat": "Alluvial Soil",
    "चिकनी": "Clay Soil", "clay": "Clay Soil", "chikni": "Clay Soil",
}


def normalize_crop_name(name: str) -> Optional[str]:
    """Map any colloquial, Hindi, or regional crop name to canonical English name."""
    if not name:
        return None
    cleaned = name.lower().strip()
    return CROP_SYNONYMS.get(cleaned) or name.title()


def normalize_soil_name(name: str) -> Optional[str]:
    """Map colloquial or regional soil names to standard category."""
    if not name:
        return None
    cleaned = name.lower().strip()
    return SOIL_SYNONYMS.get(cleaned) or name.title()
