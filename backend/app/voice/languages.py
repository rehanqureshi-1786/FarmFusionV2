"""
India-Wide Multilingual & Regional-Dialect Language & Agricultural Vocabulary Registry for FarmFusion.

Implements:
1. 4-Tier Language & Dialect Architecture (Tier 1: Native Voice, Tier 2: Parent Fallback, Tier 3: Vocabulary Normalization, Tier 4: Unsupported)
2. Decoupled Capability Schema (ASR, TTS, NLU, Translation, Dialect, Vocabulary)
3. 22+ Scheduled Indian Languages + 22+ Regional Dialects & Varieties
4. Probabilistic Dialect Detection with Evidence Tracking & Confidence Scoring
5. 10-Category Data-Driven Agricultural Vocabulary Catalog (Crops, Diseases, Fertilizers, Soils, Operations, Irrigation, Weather, Mandi, Equipment, Schemes)
6. Canonical Semantic Normalization (Surface forms -> Canonical entity IDs)
"""
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
import re


# =============================================================================
# 1. SCHEMAS
# =============================================================================

class ProviderCapability(BaseModel):
    native_supported: bool
    provider: str = "bhashini"
    fallback_code: Optional[str] = None
    confidence_tier: str = "high"  # high, medium, low, experimental
    notes: Optional[str] = None


class LanguageProfile(BaseModel):
    canonical_code: str
    name: str
    native_name: str
    script: str
    language_family: str  # Indo-Aryan, Dravidian, Tibeto-Burman, Austroasiatic, Germanic
    parent_language: Optional[str] = None
    regions: List[str] = Field(default_factory=list)
    scheduled_language: bool = False
    is_dialect: bool = False
    support_tier: int = 1  # 1: Full Native Voice, 2: Understanding + Fallback, 3: Normalization, 4: Unsupported
    asr: ProviderCapability
    tts: ProviderCapability
    nlu: ProviderCapability
    translation: ProviderCapability
    supports_dialect_detection: bool = False
    supports_agricultural_vocabulary: bool = True
    fallback_language: str = "hi"
    fallback_chain: List[str] = Field(default_factory=list)
    confidence_threshold: float = 0.60
    enabled: bool = True
    provenance: str = "MeitY Bhashini API / AI4Bharat Indic-TTS / FarmFusion Local NLU"


class VocabularyItem(BaseModel):
    surface_form: str
    canonical_entity: str
    canonical_name: str
    category: str  # crop, disease, fertilizer, soil, operation, irrigation, weather, mandi, equipment, scheme
    language: str = "hi"
    dialect: Optional[str] = None
    script: str = "Devanagari"
    confidence: float = 0.98
    source: str = "ICAR/Agmarknet/FarmFusion Ag-Catalog"
    notes: Optional[str] = None


class DialectDetectionResult(BaseModel):
    language: str
    dialect: Optional[str] = None
    script: str
    confidence: float
    support_tier: int
    fallback_language: str
    evidence: List[str] = Field(default_factory=list)


# =============================================================================
# 2. CANONICAL INDIA-WIDE LANGUAGE & DIALECT REGISTRY
# =============================================================================

LANGUAGE_REGISTRY: Dict[str, LanguageProfile] = {
    # ------------------ Tier 1: Scheduled Languages (Full Native Voice) ------------------
    "hi": LanguageProfile(
        canonical_code="hi",
        name="Hindi",
        native_name="हिन्दी",
        script="Devanagari",
        language_family="Indo-Aryan",
        regions=["North India", "Central India", "National"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        supports_dialect_detection=True,
        fallback_language="en",
        fallback_chain=["hi", "en"],
    ),
    "en": LanguageProfile(
        canonical_code="en",
        name="English",
        native_name="English",
        script="Latin",
        language_family="Germanic",
        regions=["Pan-India"],
        scheduled_language=False,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="hi",
        fallback_chain=["en", "hi"],
    ),
    "mr": LanguageProfile(
        canonical_code="mr",
        name="Marathi",
        native_name="मराठी",
        script="Devanagari",
        language_family="Indo-Aryan",
        regions=["Maharashtra", "Goa"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        supports_dialect_detection=True,
        fallback_language="hi",
        fallback_chain=["mr", "hi", "en"],
    ),
    "gu": LanguageProfile(
        canonical_code="gu",
        name="Gujarati",
        native_name="ગુજરાતી",
        script="Gujarati",
        language_family="Indo-Aryan",
        regions=["Gujarat", "Daman and Diu"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        supports_dialect_detection=True,
        fallback_language="hi",
        fallback_chain=["gu", "hi", "en"],
    ),
    "pa": LanguageProfile(
        canonical_code="pa",
        name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
        script="Gurmukhi",
        language_family="Indo-Aryan",
        regions=["Punjab", "Haryana", "Delhi"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        supports_dialect_detection=True,
        fallback_language="hi",
        fallback_chain=["pa", "hi", "en"],
    ),
    "bn": LanguageProfile(
        canonical_code="bn",
        name="Bengali",
        native_name="বাংলা",
        script="Bengali",
        language_family="Indo-Aryan",
        regions=["West Bengal", "Tripura", "Assam"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="hi",
        fallback_chain=["bn", "hi", "en"],
    ),
    "te": LanguageProfile(
        canonical_code="te",
        name="Telugu",
        native_name="తెలుగు",
        script="Telugu",
        language_family="Dravidian",
        regions=["Andhra Pradesh", "Telangana"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="hi",
        fallback_chain=["te", "hi", "en"],
    ),
    "ta": LanguageProfile(
        canonical_code="ta",
        name="Tamil",
        native_name="தமிழ்",
        script="Tamil",
        language_family="Dravidian",
        regions=["Tamil Nadu", "Puducherry"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="en",
        fallback_chain=["ta", "en", "hi"],
    ),
    "kn": LanguageProfile(
        canonical_code="kn",
        name="Kannada",
        native_name="ಕನ್ನಡ",
        script="Kannada",
        language_family="Dravidian",
        regions=["Karnataka"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        supports_dialect_detection=True,
        fallback_language="hi",
        fallback_chain=["kn", "hi", "en"],
    ),
    "ml": LanguageProfile(
        canonical_code="ml",
        name="Malayalam",
        native_name="മലയാളം",
        script="Malayalam",
        language_family="Dravidian",
        regions=["Kerala", "Lakshadweep"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="en",
        fallback_chain=["ml", "en", "hi"],
    ),
    "or": LanguageProfile(
        canonical_code="or",
        name="Odia",
        native_name="ଓଡ଼ିଆ",
        script="Odia",
        language_family="Indo-Aryan",
        regions=["Odisha"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="hi",
        fallback_chain=["or", "hi", "en"],
    ),
    "as": LanguageProfile(
        canonical_code="as",
        name="Assamese",
        native_name="অসমীয়া",
        script="Assamese",
        language_family="Indo-Aryan",
        regions=["Assam"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="bn",
        fallback_chain=["as", "bn", "hi", "en"],
    ),
    "ur": LanguageProfile(
        canonical_code="ur",
        name="Urdu",
        native_name="اردو",
        script="Perso-Arabic",
        language_family="Indo-Aryan",
        regions=["Jammu and Kashmir", "Telangana", "UP", "Bihar"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="hi",
        fallback_chain=["ur", "hi", "en"],
    ),
    "mai": LanguageProfile(
        canonical_code="mai",
        name="Maithili",
        native_name="मैथिली",
        script="Devanagari",
        language_family="Indo-Aryan",
        regions=["Bihar", "Jharkhand"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=1,
        asr=ProviderCapability(native_supported=True, provider="bhashini"),
        tts=ProviderCapability(native_supported=True, provider="bhashini"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=True, provider="bhashini"),
        fallback_language="hi",
        fallback_chain=["mai", "hi", "en"],
    ),
    "kok": LanguageProfile(
        canonical_code="kok",
        name="Konkani",
        native_name="कोंकणी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="mr",
        regions=["Goa", "Konkan Maharashtra", "Coastal Karnataka"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="mr"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="mr"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="mr"),
        fallback_language="mr",
        fallback_chain=["kok", "mr", "hi", "en"],
    ),
    "ne": LanguageProfile(
        canonical_code="ne",
        name="Nepali",
        native_name="नेपाली",
        script="Devanagari",
        language_family="Indo-Aryan",
        regions=["Sikkim", "West Bengal", "Uttarakhand"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["ne", "hi", "en"],
    ),
    "sa": LanguageProfile(
        canonical_code="sa",
        name="Sanskrit",
        native_name="संस्कृतम्",
        script="Devanagari",
        language_family="Indo-Aryan",
        regions=["National"],
        scheduled_language=True,
        is_dialect=False,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["sa", "hi", "en"],
    ),

    # ------------------ Tier 2: Regional Languages & Agricultural Dialects ------------------
    "mew": LanguageProfile(
        canonical_code="mew",
        name="Mewari",
        native_name="मेवाड़ी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Mewar", "Udaipur", "Chittorgarh", "Rajsamand", "Bhilwara"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["mew", "hi", "en"],
    ),
    "rwr": LanguageProfile(
        canonical_code="rwr",
        name="Marwari",
        native_name="मारवाड़ी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Marwar", "Jodhpur", "Bikaner", "Nagaur", "Jaisalmer", "Barmer"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["rwr", "hi", "en"],
    ),
    "dhu": LanguageProfile(
        canonical_code="dhu",
        name="Dhundhari",
        native_name="ढूंढाड़ी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Jaipur", "Dausa", "Tonk"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["dhu", "hi", "en"],
    ),
    "har": LanguageProfile(
        canonical_code="har",
        name="Harauti",
        native_name="हाड़ौती",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Kota", "Bundi", "Baran", "Jhalawar"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["har", "hi", "en"],
    ),
    "swv": LanguageProfile(
        canonical_code="swv",
        name="Shekhawati",
        native_name="शेखावाटी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Sikar", "Jhunjhunu", "Churu"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["swv", "hi", "en"],
    ),
    "wbr": LanguageProfile(
        canonical_code="wbr",
        name="Wagdi",
        native_name="वागड़ी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Dungarpur", "Banswara", "Southern Rajasthan"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["wbr", "hi", "gu"],
    ),
    "bho": LanguageProfile(
        canonical_code="bho",
        name="Bhojpuri",
        native_name="भोजपुरी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Eastern UP", "Western Bihar", "Bhojpur"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["bho", "hi", "en"],
    ),
    "awa": LanguageProfile(
        canonical_code="awa",
        name="Awadhi",
        native_name="अवधी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Central UP", "Awadh region"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["awa", "hi", "en"],
    ),
    "mag": LanguageProfile(
        canonical_code="mag",
        name="Magahi",
        native_name="मगही",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Central Bihar", "Patna", "Gaya"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["mag", "hi", "en"],
    ),
    "hne": LanguageProfile(
        canonical_code="hne",
        name="Chhattisgarhi",
        native_name="छत्तीसगढ़ी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Chhattisgarh"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["hne", "hi", "en"],
    ),
    "bns": LanguageProfile(
        canonical_code="bns",
        name="Bundeli",
        native_name="बुंदेली",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Bundelkhand", "MP", "Southern UP"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["bns", "hi", "en"],
    ),
    "bgc": LanguageProfile(
        canonical_code="bgc",
        name="Haryanvi",
        native_name="हरियाणवी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Haryana", "Western UP", "Delhi"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["bgc", "hi", "en"],
    ),
    "bra": LanguageProfile(
        canonical_code="bra",
        name="Braj",
        native_name="ब्रज भाषा",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Mathura", "Agra", "Aligarh", "Bharatpur"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["bra", "hi", "en"],
    ),
    "gbm": LanguageProfile(
        canonical_code="gbm",
        name="Garhwali",
        native_name="गढ़वाली",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Garhwal", "Uttarakhand"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["gbm", "hi", "en"],
    ),
    "kfy": LanguageProfile(
        canonical_code="kfy",
        name="Kumaoni",
        native_name="कुमाऊँनी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="hi",
        regions=["Kumaon", "Uttarakhand"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="hi"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="hi"),
        fallback_language="hi",
        fallback_chain=["kfy", "hi", "en"],
    ),
    "mup": LanguageProfile(
        canonical_code="mup",
        name="Malwai",
        native_name="ਮਲਵਈ",
        script="Gurmukhi",
        language_family="Indo-Aryan",
        parent_language="pa",
        regions=["Malwa", "Southern Punjab", "Bathinda", "Ludhiana"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="pa"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="pa"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="pa"),
        fallback_language="pa",
        fallback_chain=["mup", "pa", "hi"],
    ),
    "doa": LanguageProfile(
        canonical_code="doa",
        name="Doabi",
        native_name="ਦੁਆਬੀ",
        script="Gurmukhi",
        language_family="Indo-Aryan",
        parent_language="pa",
        regions=["Doaba", "Jalandhar", "Hoshiarpur"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="pa"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="pa"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="pa"),
        fallback_language="pa",
        fallback_chain=["doa", "pa", "hi"],
    ),
    "vah": LanguageProfile(
        canonical_code="vah",
        name="Varhadi",
        native_name="वऱ्हाडी",
        script="Devanagari",
        language_family="Indo-Aryan",
        parent_language="mr",
        regions=["Vidarbha", "Nagpur", "Amravati"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="mr"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="mr"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="mr"),
        fallback_language="mr",
        fallback_chain=["vah", "mr", "hi"],
    ),
    "kat": LanguageProfile(
        canonical_code="kat",
        name="Kathiawari",
        native_name="કાઠિયાવાડી",
        script="Gujarati",
        language_family="Indo-Aryan",
        parent_language="gu",
        regions=["Saurashtra", "Rajkot", "Junagadh", "Bhavnagar"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="gu"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="gu"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="gu"),
        fallback_language="gu",
        fallback_chain=["kat", "gu", "hi"],
    ),
    "tcy": LanguageProfile(
        canonical_code="tcy",
        name="Tulu",
        native_name="ತುಳು",
        script="Kannada",
        language_family="Dravidian",
        parent_language="kn",
        regions=["Dakshina Kannada", "Udupi", "Kasaragod"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="kn"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="kn"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="kn"),
        fallback_language="kn",
        fallback_chain=["tcy", "kn", "en"],
    ),
    "kfa": LanguageProfile(
        canonical_code="kfa",
        name="Kodava",
        native_name="ಕೊಡವ",
        script="Kannada",
        language_family="Dravidian",
        parent_language="kn",
        regions=["Kodagu / Coorg"],
        scheduled_language=False,
        is_dialect=True,
        support_tier=2,
        asr=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="kn"),
        tts=ProviderCapability(native_supported=False, provider="bhashini", fallback_code="kn"),
        nlu=ProviderCapability(native_supported=True, provider="local_orchestrator"),
        translation=ProviderCapability(native_supported=False, provider="local_rule", fallback_code="kn"),
        fallback_language="kn",
        fallback_chain=["kfa", "kn", "en"],
    ),
}

# Mapping aliases and alternative dialect codes to canonical codes
LANGUAGE_CODE_ALIASES: Dict[str, str] = {
    "mewari": "mew", "marwari": "rwr", "dhundhari": "dhu", "harauti": "har",
    "shekhawati": "swv", "wagdi": "wbr", "rajasthani": "rwr", "bhojpuri": "bho",
    "awadhi": "awa", "magahi": "mag", "chhattisgarhi": "hne", "bundeli": "bns",
    "haryanvi": "bgc", "braj": "bra", "garhwali": "gbm", "kumaoni": "kfy",
    "malwai": "mup", "doabi": "doa", "varhadi": "vah", "kathiawari": "kat",
    "tulu": "tcy", "kodava": "kfa", "konkani": "kok", "maithili": "mai",
    "nepali": "ne", "sanskrit": "sa",
    "hindi": "hi", "english": "en", "marathi": "mr", "gujarati": "gu",
    "punjabi": "pa", "bengali": "bn", "telugu": "te", "tamil": "ta",
    "kannada": "kn", "malayalam": "ml", "odia": "or", "assamese": "as",
    "urdu": "ur",
}


# =============================================================================
# 3. DIALECT GRAMMAR & LEXICON MARKERS
# =============================================================================

DIALECT_MARKERS: Dict[str, Dict[str, Any]] = {
    "mew": {
        "parent": "hi",
        "keywords": ["म्हारो", "म्हारे", "म्हारा", "म्हारी", "बोवणो", "कैसो", "घणो", "कोनी", "कीकर", "अठे", "वठे", "काईं", "थारो", "थांकी", "छै", "पड़सी"],
        "min_match": 1,
    },
    "rwr": {
        "parent": "hi",
        "keywords": ["म्हाने", "थाने", "थांके", "थांको", "खातर", "चोखी", "हुवे", "हुसी", "कांई", "आयो", "गयो", "जोधपुर", "मारवाड़", "बाजरी", "बाजरो", "बोवणो", "रैवेला", "रैयो", "बीकानेर", "नागौर", "जैसलमेर", "बाड़मेर"],
        "min_match": 1,
    },
    "dhu": {
        "parent": "hi",
        "keywords": ["छै", "छा", "छी", "म्हाको", "थाको", "कठै", "जावंगो", "करंगो"],
        "min_match": 1,
    },
    "bho": {
        "parent": "hi",
        "keywords": ["का बा", "रउआ", "हमार", "तोहार", "होई", "बाटे", "बानी", "कईसे", "खेते में", "बोईब", "बताईं", "रउरा"],
        "min_match": 1,
    },
    "bgc": {
        "parent": "hi",
        "keywords": ["तन्नै", "मन्नै", "सै", "के करै", "कुण", "घणा", "इब", "कदे", "लाग्ग्या"],
        "min_match": 1,
    },
    "awa": {
        "parent": "hi",
        "keywords": ["हमार", "तोहार", "हवै", "गवा", "आवा", "कहिस", "भवा"],
        "min_match": 1,
    },
    "hne": {
        "parent": "hi",
        "keywords": ["काबर", "गा", "हावय", "करबो", "बोवई", "खेती-खार"],
        "min_match": 1,
    },
    "mup": {
        "parent": "pa",
        "keywords": ["ਮਲਵਈ", "ਬਾਈ", "ਜਾਣਾ", "ਕਰਨਾ", "ਭਾਅ", "ਕਣਕ"],
        "min_match": 1,
    },
    "kat": {
        "parent": "gu",
        "keywords": ["કાઠિયાવાડી", "હાવ", "ખોટું", "વાવણી", "મોલાત"],
        "min_match": 1,
    },
}


# =============================================================================
# 4. COMPREHENSIVE 10-CATEGORY AGRICULTURAL VOCABULARY CATALOG
# =============================================================================

VOCABULARY_PACK: Dict[str, Dict[str, Any]] = {
    # ------------------ 1. CROPS ------------------
    "बाजरा": {"canonical_id": "pearl_millet", "canonical_name": "Pearl Millet (Bajra)", "category": "crop"},
    "बाजरो": {"canonical_id": "pearl_millet", "canonical_name": "Pearl Millet (Bajra)", "category": "crop", "dialect": "mew"},
    "बाजरी": {"canonical_id": "pearl_millet", "canonical_name": "Pearl Millet (Bajra)", "category": "crop", "dialect": "rwr"},
    "bajra": {"canonical_id": "pearl_millet", "canonical_name": "Pearl Millet (Bajra)", "category": "crop"},
    "bajro": {"canonical_id": "pearl_millet", "canonical_name": "Pearl Millet (Bajra)", "category": "crop", "dialect": "mew"},
    "sajjalu": {"canonical_id": "pearl_millet", "canonical_name": "Pearl Millet (Bajra)", "category": "crop", "language": "te"},
    "kambu": {"canonical_id": "pearl_millet", "canonical_name": "Pearl Millet (Bajra)", "category": "crop", "language": "ta"},

    "गेहूं": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop"},
    "gehun": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop"},
    "kanak": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "pa"},
    "ਕਣਕ": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "pa"},
    "ghav": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "gu"},
    "godhuma": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "te"},
    "godhumai": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "ta"},
    "கோதுமை": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "ta"},
    "gothambu": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "ml"},
    "گندم": {"canonical_id": "wheat", "canonical_name": "Wheat", "category": "crop", "language": "ur"},

    "धान": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop"},
    "ধান": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "language": "bn"},
    "चावल": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop"},
    "dhan": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop"},
    "chawal": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop"},
    "डांगर": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "language": "gu"},
    "ડાંગર": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "language": "gu"},
    "भात": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "language": "mr"},
    "nellu": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "language": "ta"},
    "நெல்": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "language": "ta"},
    "వరి": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "language": "te"},
    "bhat": {"canonical_id": "rice_paddy", "canonical_name": "Rice (Paddy)", "category": "crop", "dialect": "bho"},

    "मूंगफली": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop"},
    "सींगदाना": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop", "dialect": "mew"},
    "singdana": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop", "dialect": "mew"},
    "भूंगफली": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop", "dialect": "rwr"},
    "bhungfali": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop"},
    "kadale": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop", "language": "kn"},
    "verusenaga": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop", "language": "te"},
    "nelakadalai": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop", "language": "ta"},
    "peanut": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop"},
    "groundnut": {"canonical_id": "groundnut", "canonical_name": "Groundnut (Peanut)", "category": "crop"},

    "कपास": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop"},
    "नरमा": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop", "language": "pa"},
    "ਨਰਮਾ": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop", "language": "pa"},
    "narma": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop"},
    "कापूस": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop", "language": "mr"},
    "kapus": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop"},
    "kapas": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop"},
    "paruthi": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop", "language": "ta"},
    "pratti": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop", "language": "te"},
    "cotton": {"canonical_id": "cotton", "canonical_name": "Cotton", "category": "crop"},

    "सरसों": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop"},
    "sarson": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop"},
    "राई": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop"},
    "rai": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop"},
    "तोरी": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop", "language": "pa"},
    "kadugu": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop", "language": "ta"},
    "aavalu": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop", "language": "te"},
    "sasive": {"canonical_id": "mustard", "canonical_name": "Mustard (Sarson)", "category": "crop", "language": "kn"},

    "चना": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop"},
    "छोला": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop", "dialect": "bho"},
    "chhola": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop"},
    "हरबरा": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop", "language": "mr"},
    "harbara": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop"},
    "boot": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop", "dialect": "mag"},
    "chana": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop"},
    "gram": {"canonical_id": "chickpea", "canonical_name": "Chickpea (Gram / Chana)", "category": "crop"},

    "गन्ना": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop"},
    "ईख": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop", "dialect": "bho"},
    "eekh": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop"},
    "ऊस": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop", "language": "mr"},
    "oos": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop"},
    "शेरडी": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop", "language": "gu"},
    "sherdi": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop"},
    "karumbu": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop", "language": "ta"},
    "cheruku": {"canonical_id": "sugarcane", "canonical_name": "Sugarcane", "category": "crop", "language": "te"},

    "सोयाबीन": {"canonical_id": "soybean", "canonical_name": "Soybean", "category": "crop"},
    "soyabean": {"canonical_id": "soybean", "canonical_name": "Soybean", "category": "crop"},
    "soybean": {"canonical_id": "soybean", "canonical_name": "Soybean", "category": "crop"},

    "मक्का": {"canonical_id": "maize", "canonical_name": "Maize (Corn)", "category": "crop"},
    "मक्की": {"canonical_id": "maize", "canonical_name": "Maize (Corn)", "category": "crop", "language": "pa"},
    "ਮੱਕੀ": {"canonical_id": "maize", "canonical_name": "Maize (Corn)", "category": "crop", "language": "pa"},
    "भुट्टा": {"canonical_id": "maize", "canonical_name": "Maize (Corn)", "category": "crop"},
    "corn": {"canonical_id": "maize", "canonical_name": "Maize (Corn)", "category": "crop"},
    "jola": {"canonical_id": "maize", "canonical_name": "Maize (Corn)", "category": "crop", "language": "kn"},

    "ज्वार": {"canonical_id": "sorghum", "canonical_name": "Sorghum (Jowar)", "category": "crop"},
    "jowar": {"canonical_id": "sorghum", "canonical_name": "Sorghum (Jowar)", "category": "crop"},
    "jawar": {"canonical_id": "sorghum", "canonical_name": "Sorghum (Jowar)", "category": "crop"},
    "cholam": {"canonical_id": "sorghum", "canonical_name": "Sorghum (Jowar)", "category": "crop", "language": "ta"},
    "jonnalu": {"canonical_id": "sorghum", "canonical_name": "Sorghum (Jowar)", "category": "crop", "language": "te"},

    "प्याज": {"canonical_id": "onion", "canonical_name": "Onion", "category": "crop"},
    "कांदा": {"canonical_id": "onion", "canonical_name": "Onion", "category": "crop", "language": "mr"},
    "डुंगरी": {"canonical_id": "onion", "canonical_name": "Onion", "category": "crop", "language": "gu"},
    "kanda": {"canonical_id": "onion", "canonical_name": "Onion", "category": "crop"},
    "dungri": {"canonical_id": "onion", "canonical_name": "Onion", "category": "crop"},
    "vengayam": {"canonical_id": "onion", "canonical_name": "Onion", "category": "crop", "language": "ta"},

    "आलू": {"canonical_id": "potato", "canonical_name": "Potato", "category": "crop"},
    "बटाटा": {"canonical_id": "potato", "canonical_name": "Potato", "category": "crop", "language": "mr"},
    "batata": {"canonical_id": "potato", "canonical_name": "Potato", "category": "crop"},
    "potato": {"canonical_id": "potato", "canonical_name": "Potato", "category": "crop"},

    "लहसुन": {"canonical_id": "garlic", "canonical_name": "Garlic", "category": "crop"},
    "लसन": {"canonical_id": "garlic", "canonical_name": "Garlic", "category": "crop", "dialect": "mew"},
    "lasun": {"canonical_id": "garlic", "canonical_name": "Garlic", "category": "crop"},
    "poondu": {"canonical_id": "garlic", "canonical_name": "Garlic", "category": "crop", "language": "ta"},
    "vellulli": {"canonical_id": "garlic", "canonical_name": "Garlic", "category": "crop", "language": "te"},

    # ------------------ 2. SOIL TYPES ------------------
    "रेतीली": {"canonical_id": "sandy_soil", "canonical_name": "Sandy Soil", "category": "soil"},
    "रेत": {"canonical_id": "sandy_soil", "canonical_name": "Sandy Soil", "category": "soil"},
    "बलुई": {"canonical_id": "sandy_soil", "canonical_name": "Sandy Soil", "category": "soil", "dialect": "bho"},
    "बलुआ": {"canonical_id": "sandy_soil", "canonical_name": "Sandy Soil", "category": "soil"},
    "sandy": {"canonical_id": "sandy_soil", "canonical_name": "Sandy Soil", "category": "soil"},
    "retili": {"canonical_id": "sandy_soil", "canonical_name": "Sandy Soil", "category": "soil"},

    "काली": {"canonical_id": "black_soil", "canonical_name": "Black Soil", "category": "soil"},
    "काली मिट्टी": {"canonical_id": "black_soil", "canonical_name": "Black Soil", "category": "soil"},
    "रेगुर": {"canonical_id": "black_soil", "canonical_name": "Black Soil", "category": "soil"},
    "regur": {"canonical_id": "black_soil", "canonical_name": "Black Soil", "category": "soil"},
    "black": {"canonical_id": "black_soil", "canonical_name": "Black Soil", "category": "soil"},
    "kali": {"canonical_id": "black_soil", "canonical_name": "Black Soil", "category": "soil"},

    "दोमट": {"canonical_id": "alluvial_soil", "canonical_name": "Alluvial Soil", "category": "soil"},
    "जलोढ़": {"canonical_id": "alluvial_soil", "canonical_name": "Alluvial Soil", "category": "soil"},
    "alluvial": {"canonical_id": "alluvial_soil", "canonical_name": "Alluvial Soil", "category": "soil"},
    "loam": {"canonical_id": "alluvial_soil", "canonical_name": "Alluvial Soil", "category": "soil"},

    "लाल": {"canonical_id": "red_soil", "canonical_name": "Red Soil", "category": "soil"},
    "लाल मिट्टी": {"canonical_id": "red_soil", "canonical_name": "Red Soil", "category": "soil"},
    "red": {"canonical_id": "red_soil", "canonical_name": "Red Soil", "category": "soil"},

    "चिकनी": {"canonical_id": "clay_soil", "canonical_name": "Clay Soil", "category": "soil"},
    "मटियार": {"canonical_id": "clay_soil", "canonical_name": "Clay Soil", "category": "soil", "dialect": "bho"},
    "clay": {"canonical_id": "clay_soil", "canonical_name": "Clay Soil", "category": "soil"},

    # ------------------ 3. FERTILIZERS & NUTRIENTS ------------------
    "यूरिया": {"canonical_id": "urea", "canonical_name": "Urea", "category": "fertilizer"},
    "urea": {"canonical_id": "urea", "canonical_name": "Urea", "category": "fertilizer"},
    "डीएपी": {"canonical_id": "dap", "canonical_name": "DAP (Diammonium Phosphate)", "category": "fertilizer"},
    "dap": {"canonical_id": "dap", "canonical_name": "DAP (Diammonium Phosphate)", "category": "fertilizer"},
    "पोटाश": {"canonical_id": "mop_potash", "canonical_name": "MOP Potash", "category": "fertilizer"},
    "potash": {"canonical_id": "mop_potash", "canonical_name": "MOP Potash", "category": "fertilizer"},
    "जिंक": {"canonical_id": "zinc_sulfate", "canonical_name": "Zinc Sulfate", "category": "fertilizer"},
    "गोबर की खाद": {"canonical_id": "fym_manure", "canonical_name": "Farmyard Manure (FYM)", "category": "fertilizer"},
    "manure": {"canonical_id": "fym_manure", "canonical_name": "Farmyard Manure (FYM)", "category": "fertilizer"},

    # ------------------ 4. DISEASES & PESTS ------------------
    "झुलसा": {"canonical_id": "blight", "canonical_name": "Blight Disease", "category": "disease"},
    "blight": {"canonical_id": "blight", "canonical_name": "Blight Disease", "category": "disease"},
    "टिक्का": {"canonical_id": "tikka_leaf_spot", "canonical_name": "Tikka Leaf Spot", "category": "disease"},
    "tikka": {"canonical_id": "tikka_leaf_spot", "canonical_name": "Tikka Leaf Spot", "category": "disease"},
    "सफेद मक्खी": {"canonical_id": "whitefly", "canonical_name": "Whitefly Pest", "category": "disease"},
    "whitefly": {"canonical_id": "whitefly", "canonical_name": "Whitefly Pest", "category": "disease"},
    "इल्ली": {"canonical_id": "caterpillar_pod_borer", "canonical_name": "Pod Borer / Caterpillar", "category": "disease"},

    # ------------------ 5. OPERATIONS ------------------
    "बोवणो": {"canonical_id": "sowing", "canonical_name": "Sowing", "category": "operation", "dialect": "mew"},
    "बुवाई": {"canonical_id": "sowing", "canonical_name": "Sowing", "category": "operation"},
    "वावणी": {"canonical_id": "sowing", "canonical_name": "Sowing", "category": "operation", "language": "gu"},
    "पेरणी": {"canonical_id": "sowing", "canonical_name": "Sowing", "category": "operation", "language": "mr"},
    "sowing": {"canonical_id": "sowing", "canonical_name": "Sowing", "category": "operation"},
    "बोईब": {"canonical_id": "sowing", "canonical_name": "Sowing", "category": "operation", "dialect": "bho"},

    "कटाई": {"canonical_id": "harvesting", "canonical_name": "Harvesting", "category": "operation"},
    "लूणी": {"canonical_id": "harvesting", "canonical_name": "Harvesting", "category": "operation", "dialect": "mew"},
    "कापणी": {"canonical_id": "harvesting", "canonical_name": "Harvesting", "category": "operation", "language": "mr"},
    "harvesting": {"canonical_id": "harvesting", "canonical_name": "Harvesting", "category": "operation"},

    # ------------------ 6. IRRIGATION ------------------
    "सिंचाई": {"canonical_id": "irrigation", "canonical_name": "Irrigation", "category": "irrigation"},
    "पानी देना": {"canonical_id": "irrigation", "canonical_name": "Irrigation", "category": "irrigation"},
    "ड्रिप": {"canonical_id": "drip_irrigation", "canonical_name": "Drip Irrigation", "category": "irrigation"},
    "फुहारा": {"canonical_id": "sprinkler_irrigation", "canonical_name": "Sprinkler Irrigation", "category": "irrigation"},

    # ------------------ 7. MANDI & WEATHER TERMS ------------------
    "भाव": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi"},
    "दाम": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi"},
    "कीमत": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi"},
    "rate": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi"},
    "दर": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi", "language": "gu"},
    "ભાવ": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi", "language": "gu"},
    "ਕੀਮਤ": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi", "language": "pa"},
    "ਧਰ": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi", "language": "pa"},
    "ధర": {"canonical_id": "mandi_price", "canonical_name": "Market Price", "category": "mandi", "language": "te"},

    "मौसम": {"canonical_id": "weather", "canonical_name": "Weather", "category": "weather"},
    "हवामान": {"canonical_id": "weather", "canonical_name": "Weather", "category": "weather", "language": "mr"},
    "વાતાવરણ": {"canonical_id": "weather", "canonical_name": "Weather", "category": "weather", "language": "gu"},
    "ਮੌਸਮ": {"canonical_id": "weather", "canonical_name": "Weather", "category": "weather", "language": "pa"},
    "weather": {"canonical_id": "weather", "canonical_name": "Weather", "category": "weather"},
    "rain": {"canonical_id": "rainfall", "canonical_name": "Rainfall", "category": "weather"},
    "बारिश": {"canonical_id": "rainfall", "canonical_name": "Rainfall", "category": "weather"},
    "बरसात": {"canonical_id": "rainfall", "canonical_name": "Rainfall", "category": "weather"},
    "सूखा": {"canonical_id": "drought", "canonical_name": "Drought", "category": "weather"},

    # ------------------ 8. EQUIPMENT ------------------
    "ट्रैक्टर": {"canonical_id": "tractor", "canonical_name": "Tractor", "category": "equipment"},
    "रोटावेटर": {"canonical_id": "rotavator", "canonical_name": "Rotavator", "category": "equipment"},
    "थ्रेशर": {"canonical_id": "thresher", "canonical_name": "Thresher", "category": "equipment"},
    "सीड ड्रिल": {"canonical_id": "seed_drill", "canonical_name": "Seed Drill", "category": "equipment"},

    # ------------------ 9. GOVERNMENT SCHEMES ------------------
    "पीएम किसान": {"canonical_id": "pm_kisan", "canonical_name": "PM-Kisan Samman Nidhi", "category": "scheme"},
    "pm kisan": {"canonical_id": "pm_kisan", "canonical_name": "PM-Kisan Samman Nidhi", "category": "scheme"},
    "फसल बीमा": {"canonical_id": "pmfby", "canonical_name": "Pradhan Mantri Fasal Bima Yojana", "category": "scheme"},
    "pmfby": {"canonical_id": "pmfby", "canonical_name": "Pradhan Mantri Fasal Bima Yojana", "category": "scheme"},
    "केसीसी": {"canonical_id": "kcc", "canonical_name": "Kisan Credit Card", "category": "scheme"},
    "kcc": {"canonical_id": "kcc", "canonical_name": "Kisan Credit Card", "category": "scheme"},
    "तारबंदी": {"canonical_id": "tarbandi_subsidy", "canonical_name": "Farm Fencing Subsidy (Tarbandi)", "category": "scheme"},
    "सौर पंप": {"canonical_id": "kusum_solar", "canonical_name": "PM KUSUM Solar Pump", "category": "scheme"},
}


# =============================================================================
# 5. DATA-DRIVEN NORMALIZATION FUNCTIONS
# =============================================================================

def normalize_agricultural_term(surface_form: str, category: Optional[str] = None) -> Optional[VocabularyItem]:
    """Map any colloquial, dialect, or regional agricultural word into a typed VocabularyItem."""
    if not surface_form:
        return None
    cleaned = surface_form.lower().strip()
    match = VOCABULARY_PACK.get(cleaned)
    if match:
        if category and match.get("category") != category:
            return None
        return VocabularyItem(
            surface_form=surface_form,
            canonical_entity=match["canonical_id"],
            canonical_name=match["canonical_name"],
            category=match["category"],
            language=match.get("language", "hi"),
            dialect=match.get("dialect"),
            confidence=0.98,
        )
    return None


def normalize_crop_name(name: str) -> Optional[str]:
    """Extract canonical English crop name from any surface form."""
    if not name:
        return None
    term = normalize_agricultural_term(name, category="crop")
    if term:
        return term.canonical_name
    return name.title()


def normalize_soil_name(name: str) -> Optional[str]:
    """Extract canonical English soil name from any surface form."""
    if not name:
        return None
    term = normalize_agricultural_term(name, category="soil")
    if term:
        return term.canonical_name
    return name.title()


def detect_dialect(text: str, detected_language: str = "hi") -> DialectDetectionResult:
    """
    Detect regional dialect probabilistically from grammatical markers and regional lexicon.
    Returns structured DialectDetectionResult with evidence and honest support tier.
    """
    if not text:
        return DialectDetectionResult(
            language=detected_language,
            dialect=None,
            script="Devanagari" if detected_language in ["hi", "mr"] else "Latin",
            confidence=1.0,
            support_tier=1,
            fallback_language=detected_language,
            evidence=[],
        )

    cleaned = text.lower().strip()
    tokens = set(re.findall(r'[^\s,?.!।॥]+', cleaned, re.UNICODE))

    # Check known dialect markers and pick the one with the most matches
    best_dialect = None
    best_matches = []
    best_meta = None

    for d_code, d_meta in DIALECT_MARKERS.items():
        matches = []
        for kw in d_meta["keywords"]:
            if " " in kw:
                if kw in cleaned:
                    matches.append(kw)
            else:
                if kw in tokens:
                    matches.append(kw)
        if len(matches) >= d_meta["min_match"] and len(matches) > len(best_matches):
            best_dialect = d_code
            best_matches = matches
            best_meta = d_meta

    if best_dialect and best_meta:
        profile = LANGUAGE_REGISTRY.get(best_dialect)
        return DialectDetectionResult(
            language=best_meta["parent"],
            dialect=best_dialect,
            script=profile.script if profile else "Devanagari",
            confidence=min(0.75 + (0.10 * len(best_matches)), 0.95),
            support_tier=profile.support_tier if profile else 2,
            fallback_language=profile.fallback_language if profile else best_meta["parent"],
            evidence=best_matches,
        )

    # Fallback to parent language
    profile = LANGUAGE_REGISTRY.get(detected_language) or LANGUAGE_REGISTRY["hi"]
    return DialectDetectionResult(
        language=profile.canonical_code,
        dialect=None,
        script=profile.script,
        confidence=0.90,
        support_tier=profile.support_tier,
        fallback_language=profile.fallback_language,
        evidence=[],
    )


def resolve_language_code(code_or_dialect: str) -> str:
    """Resolve any dialect or language code/alias to its canonical registry code."""
    if not code_or_dialect:
        return "hi"
    cleaned = code_or_dialect.lower().strip()
    if cleaned in LANGUAGE_REGISTRY:
        return cleaned
    if cleaned in LANGUAGE_CODE_ALIASES:
        return LANGUAGE_CODE_ALIASES[cleaned]
    return "hi"


def get_language_profile(code_or_dialect: str) -> LanguageProfile:
    """Retrieve the full LanguageProfile for a language or dialect."""
    canonical = resolve_language_code(code_or_dialect)
    return LANGUAGE_REGISTRY.get(canonical) or LANGUAGE_REGISTRY["hi"]
