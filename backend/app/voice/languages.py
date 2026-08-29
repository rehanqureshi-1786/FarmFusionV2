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
    dialect_understanding: bool = True
    dialect_response: bool = False
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
        dialects=[
            "mewari", "marwari", "dhundhari", "harauti", "shekhawati", "rajasthani",
            "bhojpuri", "maithili", "haryanvi", "awadhi", "bundeli", "chhattisgarhi",
            "kumaoni", "garhwali"
        ],
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
        dialects=["varhadi", "nagpuri", "konkani_marathi"],
    ),
    "gu": LanguageDefinition(
        code="gu",
        name="Gujarati",
        native_name="ગુજરાતી",
        script="Gujarati",
        bhashini_code="gu",
        dialects=["kathiawari", "surati", "charotari"],
    ),
    "pa": LanguageDefinition(
        code="pa",
        name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
        script="Gurmukhi",
        bhashini_code="pa",
        dialects=["majhi", "malwai", "doabi", "puadhi"],
    ),
    "bn": LanguageDefinition(
        code="bn",
        name="Bengali",
        native_name="বাংলা",
        script="Bengali",
        bhashini_code="bn",
        dialects=["rhad", "banga", "virendri"],
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
        dialects=["kongu", "madurai", "nellai", "chennai"],
    ),
    "kn": LanguageDefinition(
        code="kn",
        name="Kannada",
        native_name="ಕನ್ನಡ",
        script="Kannada",
        bhashini_code="kn",
        dialects=["mysore", "dharwad", "tulu_kannada", "kodava_kannada"],
    ),
    "ml": LanguageDefinition(
        code="ml",
        name="Malayalam",
        native_name="മലയാളം",
        script="Malayalam",
        bhashini_code="ml",
        dialects=["central", "travancore", "malabar"],
    ),
    "or": LanguageDefinition(
        code="or",
        name="Odia",
        native_name="ଓଡ଼ିଆ",
        script="Odia",
        bhashini_code="or",
        dialects=["sambalpuri", "kataki", "balasori"],
    ),
    "as": LanguageDefinition(
        code="as",
        name="Assamese",
        native_name="অসমীয়া",
        script="Assamese",
        bhashini_code="as",
        dialects=["kamrupi", "goalpariya", "eastern_assamese"],
    ),
}

# Dialect mapping to parent language codes
DIALECT_PARENT_MAP: Dict[str, str] = {
    "mewari": "hi",
    "marwari": "hi",
    "dhundhari": "hi",
    "harauti": "hi",
    "shekhawati": "hi",
    "rajasthani": "hi",
    "bhojpuri": "hi",
    "maithili": "hi",
    "haryanvi": "hi",
    "awadhi": "hi",
    "bundeli": "hi",
    "chhattisgarhi": "hi",
    "kumaoni": "hi",
    "garhwali": "hi",
    "malwai": "pa",
    "doabi": "pa",
    "varhadi": "mr",
    "kathiawari": "gu",
    "tulu": "kn",
    "kodava": "kn",
    "konkani": "mr",
}

# Agricultural Vocabulary Normalization dictionary
CROP_SYNONYMS: Dict[str, str] = {
    # Pearl Millet / Bajra (Rajasthan / Gujarat / Haryana)
    "बाजरा": "Pearl Millet (Bajra)", "बाजरो": "Pearl Millet (Bajra)", "बाजरी": "Pearl Millet (Bajra)",
    "bajra": "Pearl Millet (Bajra)", "bajri": "Pearl Millet (Bajra)", "bajro": "Pearl Millet (Bajra)",
    "sajjalu": "Pearl Millet (Bajra)", "kambu": "Pearl Millet (Bajra)", "bajra crop": "Pearl Millet (Bajra)",

    # Wheat
    "गेहूं": "Wheat", "gehun": "Wheat", "gehu": "Wheat", "ghav": "Wheat", "kanak": "Wheat",
    "gothambu": "Wheat", "godhuma": "Wheat", "godhumai": "Wheat", "gahum": "Wheat",

    # Rice / Paddy
    "धान": "Rice (Paddy)", "चावल": "Rice (Paddy)", "chawal": "Rice (Paddy)", "dhan": "Rice (Paddy)",
    "bhat": "Rice (Paddy)", "paddy": "Rice (Paddy)", "rice": "Rice (Paddy)", "nellu": "Rice (Paddy)",
    "dangar": "Rice (Paddy)", "bhatto": "Rice (Paddy)", "chavval": "Rice (Paddy)",

    # Groundnut / Peanut
    "मूंगफली": "Groundnut (Peanut)", "mungfali": "Groundnut (Peanut)", "moongphali": "Groundnut (Peanut)",
    "peanut": "Groundnut (Peanut)", "groundnut": "Groundnut (Peanut)", "singdana": "Groundnut (Peanut)",
    "kadale": "Groundnut (Peanut)", "nelakadalai": "Groundnut (Peanut)", "verusenaga": "Groundnut (Peanut)",
    "bhungfali": "Groundnut (Peanut)", "moongfali": "Groundnut (Peanut)",

    # Cotton
    "कपास": "Cotton", "kapas": "Cotton", "rooi": "Cotton", "cotton": "Cotton", "patti": "Cotton",
    "kapus": "Cotton", "paruthi": "Cotton", "pratti": "Cotton", "narma": "Cotton",

    # Mustard / Rapeseed
    "सरसों": "Mustard (Sarson)", "sarson": "Mustard (Sarson)", "rai": "Mustard (Sarson)",
    "mustard": "Mustard (Sarson)", "kadugu": "Mustard (Sarson)", "aavalu": "Mustard (Sarson)",
    "sasive": "Mustard (Sarson)", "sarso": "Mustard (Sarson)", "toria": "Mustard (Sarson)",

    # Soybean
    "सोयाबीन": "Soybean", "soyabean": "Soybean", "soybean": "Soybean", "soya": "Soybean",

    # Sugarcane
    "गन्ना": "Sugarcane", "ganna": "Sugarcane", "sherdi": "Sugarcane", "oos": "Sugarcane",
    "karumbu": "Sugarcane", "cheruku": "Sugarcane", "kabbu": "Sugarcane", "eekh": "Sugarcane",

    # Chickpea / Chana
    "चना": "Chickpea (Gram / Chana)", "chana": "Chickpea (Gram / Chana)", "gram": "Chickpea (Gram / Chana)",
    "chickpea": "Chickpea (Gram / Chana)", "harbara": "Chickpea (Gram / Chana)", "kadale_kalu": "Chickpea (Gram / Chana)",
    "kondaikadala": "Chickpea (Gram / Chana)", "chhola": "Chickpea (Gram / Chana)", "boot": "Chickpea (Gram / Chana)",

    # Green Gram / Moong
    "मूंग": "Green Gram (Moong)", "moong": "Green Gram (Moong)", "mung": "Green Gram (Moong)",
    "pesalu": "Green Gram (Moong)", "pasi_payiru": "Green Gram (Moong)", "hesaru_kalu": "Green Gram (Moong)",
    "mug": "Green Gram (Moong)",

    # Maize / Corn
    "मक्का": "Maize (Corn)", "makka": "Maize (Corn)", "makki": "Maize (Corn)", "corn": "Maize (Corn)",
    "maize": "Maize (Corn)", "bhutta": "Maize (Corn)", "jola": "Maize (Corn)", "mokka_jonna": "Maize (Corn)",

    # Sorghum / Jowar
    "ज्वार": "Sorghum (Jowar)", "jowar": "Sorghum (Jowar)", "jawar": "Sorghum (Jowar)",
    "cholam": "Sorghum (Jowar)", "jonnalu": "Sorghum (Jowar)", "jola_grain": "Sorghum (Jowar)",

    # Onion
    "प्याज": "Onion", "pyaj": "Onion", "onion": "Onion", "kanda": "Onion", "dungri": "Onion",
    "vengayam": "Onion", "ullipayalu": "Onion", "irulli": "Onion",

    # Potato
    "आलू": "Potato", "alu": "Potato", "batata": "Potato", "potato": "Potato",
    "urulaikizhangu": "Potato", "bangaladumpa": "Potato", "alugadde": "Potato",

    # Tomato
    "टमाटर": "Tomato", "tamatar": "Tomato", "tomato": "Tomato", "thakkali": "Tomato", "tamata": "Tomato",

    # Garlic
    "लहसुन": "Garlic", "lahsun": "Garlic", "garlic": "Garlic", "lasun": "Garlic", "poondu": "Garlic",
    "vellulli": "Garlic", "bellulli": "Garlic",
}

SOIL_SYNONYMS: Dict[str, str] = {
    "रेतीली": "Sandy Soil", "बलुई": "Sandy Soil", "sandy": "Sandy Soil", "retili": "Sandy Soil",
    "sand": "Sandy Soil", "रेत": "Sandy Soil", "बलुआ": "Sandy Soil", "रेतवाली": "Sandy Soil",
    "काली": "Black Soil", "काली मिट्टी": "Black Soil", "black": "Black Soil", "regur": "Black Soil",
    "kali": "Black Soil", "काली दोमट": "Black Soil",
    "लाल": "Red Soil", "लाल मिट्टी": "Red Soil", "red": "Red Soil", "laal": "Red Soil",
    "दोमट": "Alluvial Soil", "जलोढ़": "Alluvial Soil", "alluvial": "Alluvial Soil", "loam": "Alluvial Soil",
    "domat": "Alluvial Soil", "चिकनी दोमट": "Alluvial Soil",
    "चिकनी": "Clay Soil", "clay": "Clay Soil", "chikni": "Clay Soil", "मटियार": "Clay Soil",
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


def resolve_language_code(code_or_dialect: str) -> str:
    """Resolve a dialect or language code to its canonical supported language code."""
    if not code_or_dialect:
        return "hi"
    cleaned = code_or_dialect.lower().strip()
    if cleaned in SUPPORTED_LANGUAGES:
        return cleaned
    if cleaned in DIALECT_PARENT_MAP:
        return DIALECT_PARENT_MAP[cleaned]
    return "hi"
