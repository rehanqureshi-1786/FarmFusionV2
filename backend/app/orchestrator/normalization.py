"""
Deterministic Agricultural Vocabulary Normalization for FarmFusion.

Provides robust, bidirectional entity mapping across Hindi, Hinglish, English,
and Indian regional languages (Punjabi, Gujarati, Marathi, Telugu, Tamil, etc.).
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

# =============================================================================
# 1. CROP DICTIONARY (Surface Forms -> Canonical English Title)
# =============================================================================

CROP_SYNONYMS = {
    # Wheat
    "wheat": "Wheat", "gehu": "Wheat", "gehun": "Wheat", "गेहूं": "Wheat", "गेहु": "Wheat",
    "kanak": "Wheat", "ਕਣਕ": "Wheat", "ghav": "Wheat", "ghau": "Wheat", "ઘઉં": "Wheat",
    "godhuma": "Wheat", "godhumai": "Wheat", "gothambu": "Wheat", "gandum": "Wheat", "گندم": "Wheat",

    # Paddy / Rice
    "rice": "Paddy", "paddy": "Paddy", "dhan": "Paddy", "धान": "Paddy", "chawal": "Paddy",
    "चावल": "Paddy", "bhat": "Paddy", "भात": "Paddy", "dangar": "Paddy", "ડાંગર": "Paddy",
    "nellu": "Paddy", "వరి": "Paddy", "ভাত": "Paddy", "vari": "Paddy",

    # Cotton
    "cotton": "Cotton", "kapas": "Cotton", "कपास": "Cotton", "kapasiya": "Cotton",
    "kapaas": "Cotton", "paruthi": "Cotton", "பருத்தி": "Cotton", "pratti": "Cotton",
    "kapus": "Cotton", "कापूस": "Cotton", "ru": "Cotton", "रू": "Cotton", "કપાસ": "Cotton",
    "કપાસના": "Cotton", "કપાસનો": "Cotton", "કપાસનું": "Cotton", "કપાસની": "Cotton",


    # Onion
    "onion": "Onion", "pyaz": "Onion", "pyaaz": "Onion", "प्याज": "Onion", "kanda": "Onion",
    "कांदा": "Onion", "कांद्याचा": "Onion", "dungri": "Onion", "ડુંગળી": "Onion", "vengayam": "Onion", "ulli": "Onion",

    # Potato
    "potato": "Potato", "aloo": "Potato", "alu": "Potato", "आलू": "Potato", "batata": "Potato",
    "बटाटा": "Potato", "urulaikizhangu": "Potato", "bangaladumpa": "Potato",

    # Tomato
    "tomato": "Tomato", "tamatar": "Tomato", "टमाटर": "Tomato", "thakkali": "Tomato",
    "tameta": "Tomato", "ટમેટા": "Tomato", "tamata": "Tomato",

    # Mustard
    "mustard": "Mustard", "sarso": "Mustard", "sarson": "Mustard", "सरसों": "Mustard",
    "rai": "Mustard", "राई": "Mustard", "kadugu": "Mustard", "aavalu": "Mustard", "mohri": "Mustard",

    # Gram / Chickpea
    "gram": "Gram", "chana": "Gram", "चना": "Gram", "chane": "Gram", "harbara": "Gram",
    "हरभरा": "Gram", "kadala": "Gram", "senagalu": "Gram", "kondai kadalai": "Gram",

    # Moong / Green Gram
    "moong": "Moong", "mung": "Moong", "मूंग": "Moong", "green gram": "Moong", "mag": "Moong", "मग": "Moong",

    # Soybean
    "soybean": "Soybean", "soyabean": "Soybean", "सोयाबीन": "Soybean", "soya": "Soybean",

    # Maize
    "maize": "Maize", "corn": "Maize", "makka": "Maize", "मक्का": "Maize", "bhutta": "Maize",
    "भुट्टा": "Maize", "makai": "Maize", "મકાઈ": "Maize", "cholam": "Maize", "mokka jonnalu": "Maize",

    # Groundnut
    "groundnut": "Groundnut", "peanut": "Groundnut", "mungfali": "Groundnut", "मूंगफली": "Groundnut",
    "singdana": "Groundnut", "सींगदाना": "Groundnut", "bhungfali": "Groundnut", "kadale": "Groundnut",
    "verusenaga": "Groundnut", "nelakadalai": "Groundnut", "shengdana": "Groundnut",

    # Pearl Millet (Bajra)
    "bajra": "Bajra", "pearl millet": "Bajra", "बाजरा": "Bajra", "bajro": "Bajra",
    "sajjalu": "Bajra", "kambu": "Bajra", "sajje": "Bajra",

    # Garlic
    "garlic": "Garlic", "lahsun": "Garlic", "लहसुन": "Garlic", "poondu": "Garlic",
    "vellulli": "Garlic", "lasun": "Garlic", "લસણ": "Garlic",

    # Sugarcane
    "sugarcane": "Sugarcane", "ganna": "Sugarcane", "गन्ना": "Sugarcane", "karumbu": "Sugarcane",
    "cheruku": "Sugarcane", "oos": "Sugarcane", "ऊस": "Sugarcane", "sherdi": "Sugarcane",

    # Chilli
    "chilli": "Chilli", "chili": "Chilli", "mirch": "Chilli", "मिर्च": "Chilli",
    "mirchi": "Chilli", "milagai": "Chilli", "marapakaya": "Chilli",
}

# =============================================================================
# 2. MANDI / MARKET DICTIONARY
# =============================================================================

MARKET_SYNONYMS = {
    "jaipur": "Jaipur", "जयपुर": "Jaipur",
    "udaipur": "Udaipur", "उदयपुर": "Udaipur",
    "kota": "Kota", "कोटा": "Kota",
    "jodhpur": "Jodhpur", "जोधपुर": "Jodhpur",
    "bikaner": "Bikaner", "बीकानेर": "Bikaner",
    "nagaur": "Nagaur", "नागौर": "Nagaur",
    "alwar": "Alwar", "अलवर": "Alwar",
    "ganganagar": "Ganganagar", "गंगानगर": "Ganganagar", "sriganganagar": "Ganganagar",
    "pratapgarh": "Pratapgarh", "प्रतापगढ़": "Pratapgarh",
    "fatehnagar": "Fatehnagar", "फतेहनगर": "Fatehnagar",
    "sendhwa": "Sendhwa", "सेंधवा": "Sendhwa",
    "kalapipal": "Kalapipal", "कालापीपल": "Kalapipal",
    "indore": "Indore", "इंदौर": "Indore",
    "bhopal": "Bhopal", "भोपाल": "Bhopal",
    "ujjain": "Ujjain", "उज्जैन": "Ujjain",
    "mandsaur": "Mandsaur", "मंदसौर": "Mandsaur",
    "neemuch": "Neemuch", "नीमच": "Neemuch",
    "nashik": "Nashik", "नासिक": "Nashik", "नाशिक": "Nashik", "नाशिकमध्ये": "Nashik",
    "pune": "Pune", "पुणे": "Pune", "पुण्यात": "Pune", "पुण्यामध्ये": "Pune",
    "mumbai": "Mumbai", "मुंबई": "Mumbai", "मुंबईत": "Mumbai",
    "nagpur": "Nagpur", "नागपुर": "Nagpur", "नागपूर": "Nagpur",
    "rajkot": "Rajkot", "राजकोट": "Rajkot", "રાજકોટ": "Rajkot",
    "surat": "Surat", "सूरत": "Surat", "સુરત": "Surat",
    "ahmedabad": "Ahmedabad", "अहमदाबाद": "Ahmedabad", "અમદાવાદ": "Ahmedabad", "અમદાવાદમાં": "Ahmedabad",
    "ludhiana": "Ludhiana", "लुधियाना": "Ludhiana", "ਲੁਧਿਆਣਾ": "Ludhiana", "ਲੁਧਿਆਣੇ": "Ludhiana",
    "amritsar": "Amritsar", "अमृतसर": "Amritsar", "ਅੰਮ੍ਰਿਤਸਰ": "Amritsar",
    "khanna": "Khanna", "खन्ना": "Khanna", "ਖੰਨਾ": "Khanna",
    "karnal": "Karnal", "करनाल": "Karnal",
    "delhi": "Delhi", "दिल्ली": "Delhi",
    "lucknow": "Lucknow", "लखनऊ": "Lucknow",
    "agra": "Agra", "आगरा": "Agra",
    "patna": "Patna", "पटना": "Patna",
    "kolkata": "Kolkata", "कोलकाता": "Kolkata", "কলকাতা": "Kolkata", "কলকাতায়": "Kolkata",
    "hyderabad": "Hyderabad", "हैदराबाद": "Hyderabad", "హైదరాబాద్": "Hyderabad",
    "bengaluru": "Bengaluru", "बेंगलुरु": "Bengaluru", "bangalore": "Bengaluru", "ಬೆಂಗಳೂರು": "Bengaluru",
    "chennai": "Chennai", "चेन्नई": "Chennai", "சென்னை": "Chennai",
    "coimbatore": "Coimbatore", "कोयंबटूर": "Coimbatore",
}

# =============================================================================
# 3. SOIL TYPE SYNONYMS
# =============================================================================

SOIL_SYNONYMS = {
    "black": "Black Soil", "kali": "Black Soil", "काली": "Black Soil", "regur": "Black Soil", "रेगुर": "Black Soil",
    "sandy": "Sandy Soil", "retili": "Sandy Soil", "रेतीली": "Sandy Soil", "balui": "Sandy Soil", "बलुई": "Sandy Soil",
    "red": "Red Soil", "lal": "Red Soil", "लाल": "Red Soil",
    "alluvial": "Alluvial Soil", "domat": "Alluvial Soil", "दोमट": "Alluvial Soil", "matiyari": "Alluvial Soil",
    "clay": "Clay Soil", "chikni": "Clay Soil", "चिकनी": "Clay Soil", "chikni mitti": "Clay Soil",
    "loam": "Loam Soil", "loamy": "Loam Soil",
}


# =============================================================================
# 4. EXTRACTION FUNCTIONS
# =============================================================================

def normalize_crop_name(text: str) -> Optional[str]:
    """Find and normalize crop name mentioned anywhere in text."""
    if not text:
        return None
    cleaned = text.lower()
    # Direct match first
    if cleaned in CROP_SYNONYMS:
        return CROP_SYNONYMS[cleaned]
    # Word boundary / token match
    tokens = re.findall(r'[^\s,?.!।॥/()]+', cleaned, re.UNICODE)
    for token in tokens:
        if token in CROP_SYNONYMS:
            return CROP_SYNONYMS[token]
    # Check multi-word synonyms (e.g., "soy bean", "chana dal", "red gram")
    for synonym, canonical in CROP_SYNONYMS.items():
        if " " in synonym and synonym in cleaned:
            return canonical
        elif len(synonym) >= 4 and re.search(r'(?<!\w)' + re.escape(synonym) + r'(?!\w)', cleaned):
            return canonical
    return None



def extract_markets(text: str) -> List[str]:
    """Extract all distinct recognized mandi / city names mentioned in text."""
    if not text:
        return []
    cleaned = text.lower()
    found: List[str] = []
    # Token check
    tokens = re.findall(r'[^\s,?.!।॥/()]+', cleaned, re.UNICODE)
    for token in tokens:
        if token in MARKET_SYNONYMS:
            canonical = MARKET_SYNONYMS[token]
            if canonical not in found:
                found.append(canonical)
    # Substring check for cities not cleanly separated
    for synonym, canonical in MARKET_SYNONYMS.items():
        if len(synonym) >= 4 and synonym in cleaned:
            if canonical not in found:
                found.append(canonical)
    return found


def normalize_soil_type(text: str) -> Optional[str]:
    """Extract and normalize soil classification."""
    if not text:
        return None
    cleaned = text.lower()
    for syn, canonical in SOIL_SYNONYMS.items():
        if syn in cleaned:
            return canonical
    return None


def extract_forecast_days(text: str) -> Optional[int]:
    """Extract forecast duration in days."""
    if not text:
        return None
    cleaned = text.lower()
    # Explicit digit matches: e.g. "7 din", "7 days", "10 din", "3 din"
    digit_match = re.search(r'(\d+)\s*(?:din|days|दिन|दिवस|day)', cleaned)
    if digit_match:
        val = int(digit_match.group(1))
        return min(max(val, 1), 30)

    # Phrasing matches
    if any(w in cleaned for w in ["हफ्ते", "हफ्ता", "week", "seven days", "सात दिन", "1 week", "one week"]):
        return 7
    if any(w in cleaned for w in ["दो हफ्ते", "2 weeks", "fortnight", "पखवाड़ा"]):
        return 14
    if any(w in cleaned for w in ["तीन दिन", "3 days", "3 din"]):
        return 3
    if any(w in cleaned for w in ["महीने", "month", "30 days"]):
        return 30
    if any(w in cleaned for w in ["कल", "tomorrow", "दो दिन", "48 घंटे", "48 hours"]):
        return 2
    return None


def extract_timeframe(text: str) -> Optional[str]:
    """Extract temporal context from query."""
    if not text:
        return None
    cleaned = text.lower()
    if any(w in cleaned for w in ["आज", "today", "aaj"]):
        return "today"
    if any(w in cleaned for w in ["कल", "tomorrow", "kal"]):
        return "tomorrow"
    if any(w in cleaned for w in ["परसों", "day after tomorrow", "parso"]):
        return "day_after_tomorrow"
    if any(w in cleaned for w in ["अगले हफ्ते", "next week", "agle hafte"]):
        return "next_week"
    if any(w in cleaned for w in ["अगले 7 दिन", "next 7 days", "agle 7 din"]):
        return "next_7_days"
    if any(w in cleaned for w in ["इस महीने", "this month"]):
        return "this_month"
    return None
