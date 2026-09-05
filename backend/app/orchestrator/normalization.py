"""
Deterministic Agricultural Vocabulary Normalization for FarmFusion.

Provides robust, bidirectional entity mapping across Hindi, Hinglish, English,
and Indian regional languages (Punjabi, Gujarati, Marathi, Telugu, Tamil, etc.).
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

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


# =============================================================================
# 5. SEMANTIC TEMPORAL NORMALIZATION (First-class time entity — F7 fix)
#    Maps multilingual relative-day expressions to a canonical TemporalAnchor so
#    the planner/tools resolve the ACTUAL requested date instead of defaulting to
#    today. This is a vocabulary→semantic normalization, NOT a string patcher.
# =============================================================================

# Ordered probes: (surface token, RelativeDay value, day_offset). Longer/more
# specific phrases first so "day after tomorrow" wins over "day" and "agle 7 din"
# beats "agle din".
_RELATIVE_PROBES: List[Tuple[str, str, int]] = [
    ("day after tomorrow", "DAY_AFTER_TOMORROW", 2),
    ("agle 7 din", "NEXT_7_DAYS", 0),
    ("अगले 7 दिन", "NEXT_7_DAYS", 0),
    ("next 7 days", "NEXT_7_DAYS", 0),
    ("अगले सात दिन", "NEXT_7_DAYS", 0),
    ("this week", "THIS_WEEK", 0),
    ("इस हफ्ते", "THIS_WEEK", 0),
    ("next week", "NEXT_WEEK", 7),
    ("agle hafte", "NEXT_WEEK", 7),
    ("अगले हफ्ते", "NEXT_WEEK", 7),
    ("next month", "NEXT_MONTH", 30),
    ("अगले महीने", "NEXT_MONTH", 30),
    ("agle mahine", "NEXT_MONTH", 30),
    ("next day", "TOMORROW", 1),
    ("agle din", "TOMORROW", 1),
    ("अगले दिन", "TOMORROW", 1),
    ("parson", "DAY_AFTER_TOMORROW", 2),
    ("parso", "DAY_AFTER_TOMORROW", 2),
    ("परसों", "DAY_AFTER_TOMORROW", 2),
    ("tomorrow", "TOMORROW", 1),
    ("kal", "TOMORROW", 1),
    ("कल", "TOMORROW", 1),
    ("next day", "TOMORROW", 1),
    # Regional-language tomorrow today tokens
    ("আগামীকাল", "TOMORROW", 1),
    ("நாளை", "TOMORROW", 1),
    ("రేపు", "TOMORROW", 1),
    ("ಮುಂದಿನ ದಿನ", "TOMORROW", 1),
    ("morrow", "TOMORROW", 1),
    ("आज", "TODAY", 0),
    ("aaj", "TODAY", 0),
    ("abhi", "TODAY", 0),
    ("अभी", "TODAY", 0),
    ("today", "TODAY", 0),
    ("current", "TODAY", 0),
    ("currently", "TODAY", 0),
    ("இன்று", "TODAY", 0),
    ("ఈ రోజు", "TODAY", 0),
    ("আজ", "TODAY", 0),
]

_MONTHS_EN = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
              "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
              "december": 12, "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
              "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12}
_HINDI_MONTHS = {"जनवरी": 1, "फरवरी": 2, "मार्च": 3, "अप्रैल": 4, "मई": 5, "जून": 6,
                 "जुलाई": 7, "अगस्त": 8, "सितंबर": 9, "अक्टूबर": 10, "नवंबर": 11, "दिसंबर": 12}
_NATIVE_DIGITS = str.maketrans({
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4", "५": "5", "६": "6", "७": "7",
    "८": "8", "९": "9", "০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4", "৫": "5",
    "৬": "6", "৭": "7", "৮": "8", "৯": "9", "૦": "0", "૧": "1", "૨": "2", "૩": "3",
    "૪": "4", "૫": "5", "૬": "6", "૭": "7", "૮": "8", "૯": "9"})


def _extract_explicit_date(cleaned: str) -> Optional[str]:
    """Resolve explicit dates: '15 September', '15 sept', '2026-09-15', '१५ सितंबर'."""
    iso = re.search(r"(20\d{2})[-/.](1[0-2]|0[1-9])[-/.](3[01]|[12]\d|0[1-9])", cleaned)
    if iso:
        return f"{iso.group(1)}-{int(iso.group(2)):02d}-{int(iso.group(3)):02d}"
    for m in re.finditer(r"(\d{1,2})\s*(%s)(?:\s*(20\d{2}))?" % "|".join(_MONTHS_EN), cleaned):
        day = int(m.group(1).translate(_NATIVE_DIGITS))
        if 1 <= day <= 31:
            year = int(m.group(3)) if m.group(3) else datetime.now().year
            return f"{year}-{_MONTHS_EN[m.group(2)]:02d}-{day:02d}"
    for hname, hnum in _HINDI_MONTHS.items():
        m = re.search(r"(\d{1,2})\s*" + hname, cleaned)
        if m:
            day = int(m.group(1).translate(_NATIVE_DIGITS))
            if 1 <= day <= 31:
                return f"{datetime.now().year}-{hnum:02d}-{day:02d}"
    return None


def resolve_time_context(text: str, reference_date: Optional[str] = None) -> Dict[str, Any]:
    """Canonical temporal resolution. Returns fields matching ``TimeContext``."""
    empty = {
        "relative_day": "UNSPECIFIED", "reference_date": reference_date,
        "resolved_date": None, "horizon_days": 1, "forecast_days": None,
        "explicit_date": None, "is_relative": False, "raw_hint": None,
    }
    if not text:
        return empty
    cleaned = text.strip().lower()

    try:
        ref_dt = datetime.strptime(reference_date, "%Y-%m-%d").date() if reference_date else date.today()
    except (ValueError, TypeError):
        ref_dt = date.today()

    base = dict(empty)
    base["reference_date"] = ref_dt.isoformat()
    base["resolved_date"] = ref_dt.isoformat()

    explicit = _extract_explicit_date(cleaned)
    if explicit:
        base.update({"relative_day": "EXPLICIT_DATE", "resolved_date": explicit,
                     "explicit_date": explicit, "is_relative": False, "raw_hint": explicit})
        return base

    for probe, rd, offset in _RELATIVE_PROBES:
        if probe in cleaned:
            target = ref_dt + timedelta(days=offset)
            multi_day = rd in ("NEXT_7_DAYS", "NEXT_WEEK", "THIS_WEEK")
            base.update({
                "relative_day": rd,
                "resolved_date": target.isoformat(),
                "horizon_days": 7 if multi_day else 1,
                "forecast_days": 7 if rd in ("NEXT_7_DAYS", "NEXT_WEEK") else None,
                "is_relative": True,
                "raw_hint": probe,
            })
            return base

    return base
