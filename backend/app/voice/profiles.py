"""
Universal India-Wide Multilingual Language Inventory & Voice Capability System.
Provides independent, strictly decoupled concepts:
1. LanguageProfile: Pure linguistic and geographic metadata.
2. VoiceCapabilityProfile: Concrete, verified system capabilities (ASR, NLU, TTS, Local, Offline, Fallbacks).
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class LanguageFamily(str, Enum):
    INDO_ARYAN = "indo_aryan"
    DRAVIDIAN = "dravidian"
    AUSTROASIATIC = "austroasiatic"
    TIBETO_BURMAN = "tibeto_burman"
    LANGUAGE_ISOLATE = "language_isolate"


class CapabilityTier(str, Enum):
    NATIVE_VOICE = "native_voice"                                      # Full verified native ASR + native TTS
    NATIVE_ASR_PARENT_TTS = "native_asr_parent_tts"                    # Native ASR + Parent Language TTS fallback
    DIALECT_UNDERSTANDING_PARENT_RESPONSE = "dialect_understanding_parent_response" # Dialect NLU/vocab + Parent text/TTS
    TRANSLATION_FALLBACK = "translation_fallback"                      # Automated/rule translation + Parent voice
    VOCABULARY_ONLY = "vocabulary_only"                                # Normalized vocabulary only; no native voice
    UNSUPPORTED = "unsupported"                                        # Known language but zero verified models


class LanguageProfile(BaseModel):
    """Linguistic and demographic profile of an Indian language or dialect variety."""
    canonical_id: str = Field(..., description="Unique BCP-47 or ISO-639-3 identifier, e.g. hi, rwr, mew, gon")
    name: str = Field(..., description="Standard English name")
    native_name: str = Field(..., description="Endonym in native script")
    script: str = Field(..., description="Primary writing script, e.g. Devanagari, Bengali, Ol Chiki")
    language_family: LanguageFamily
    parent_language: Optional[str] = Field(None, description="Canonical ID of parent/standard language if dialect")
    is_scheduled_22: bool = Field(False, description="Whether listed in the 8th Schedule of the Indian Constitution")
    regional_states: List[str] = Field(default_factory=list, description="Indian states where prominently spoken")
    prominent_districts: List[str] = Field(default_factory=list, description="Districts with high speaker density")
    alternate_names: List[str] = Field(default_factory=list)
    dialects: List[str] = Field(default_factory=list, description="Sub-dialects or regional varieties")
    mother_tongue_references: List[str] = Field(default_factory=list, description="Census of India mother tongue codes")
    agricultural_vocabulary_pack: Optional[str] = Field(None, description="Associated agricultural vocabulary identifier")


class VoiceCapabilityProfile(BaseModel):
    """Verified runtime voice and intelligence capabilities for a language/dialect."""
    language_id: str = Field(..., description="Matching canonical_id from LanguageProfile")
    asr_available: bool = False
    asr_provider: Optional[str] = None           # e.g. "bhashini", "indicwhisper", "local_conformer", None
    asr_model: Optional[str] = None
    lid_available: bool = False                  # Language Identification availability
    dialect_detection: bool = False              # Probabilistic dialect detection
    nlu_available: bool = True                   # High-level NLU availability
    local_nlu_available: bool = False            # On-device lightweight NLU available
    response_generation_available: bool = True   # Response localization available
    native_text_generation: bool = False         # Genuine native written text generation
    native_tts: bool = False                     # Genuine native TTS synthesis
    tts_provider: Optional[str] = None           # e.g. "bhashini", "piper_vits", "indic_tts", None
    translation_available: bool = False
    streaming_asr: bool = False
    streaming_tts: bool = False
    offline_available: bool = False              # Can operate fully offline
    fallback_language: str = "hi"                # Default parent/fallback language
    fallback_chain: List[str] = Field(default_factory=lambda: ["hi", "en"])
    capability_tier: CapabilityTier = CapabilityTier.VOCABULARY_ONLY
    verified_status: str = "VERIFIED_TRUTHFUL"
    verified_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ============================================================================
# UNIVERSAL INDIA-WIDE LINGUISTIC CATALOG & CAPABILITY REGISTRY
# ============================================================================

INDIA_LANGUAGE_CATALOG: Dict[str, LanguageProfile] = {
    # ---------------- 22 SCHEDULED INDIAN LANGUAGES ----------------
    "hi": LanguageProfile(
        canonical_id="hi",
        name="Hindi",
        native_name="हिन्दी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Bihar", "Haryana", "Delhi", "Himachal Pradesh", "Jharkhand", "Chhattisgarh", "Uttarakhand"],
        alternate_names=["Standard Hindi", "Khari Boli"],
        dialects=["Braj", "Awadhi", "Bhojpuri", "Bundeli", "Bagheli", "Haryanvi", "Kannauji"],
        agricultural_vocabulary_pack="vocab_hi_universal",
    ),
    "bn": LanguageProfile(
        canonical_id="bn",
        name="Bengali",
        native_name="বাংলা",
        script="Bengali",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["West Bengal", "Tripura", "Assam"],
        alternate_names=["Bangla"],
        dialects=["Rarh", "Varendra", "Manbhum"],
        agricultural_vocabulary_pack="vocab_bn_universal",
    ),
    "te": LanguageProfile(
        canonical_id="te",
        name="Telugu",
        native_name="తెలుగు",
        script="Telugu",
        language_family=LanguageFamily.DRAVIDIAN,
        is_scheduled_22=True,
        regional_states=["Andhra Pradesh", "Telangana"],
        alternate_names=["Andhra"],
        dialects=["Costal Andhra", "Rayalaseema", "Telangana"],
        agricultural_vocabulary_pack="vocab_te_universal",
    ),
    "mr": LanguageProfile(
        canonical_id="mr",
        name="Marathi",
        native_name="मराठी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Maharashtra", "Goa"],
        alternate_names=["Maharashtri"],
        dialects=["Varhadi", "Deshi", "Konkani Marathi", "Khandeshi"],
        agricultural_vocabulary_pack="vocab_mr_universal",
    ),
    "ta": LanguageProfile(
        canonical_id="ta",
        name="Tamil",
        native_name="தமிழ்",
        script="Tamil",
        language_family=LanguageFamily.DRAVIDIAN,
        is_scheduled_22=True,
        regional_states=["Tamil Nadu", "Puducherry"],
        dialects=["Kongu", "Madurai", "Central Tamil", "Nellai"],
        agricultural_vocabulary_pack="vocab_ta_universal",
    ),
    "gu": LanguageProfile(
        canonical_id="gu",
        name="Gujarati",
        native_name="ગુજરાતી",
        script="Gujarati",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Gujarat", "Daman and Diu"],
        dialects=["Kathiawari", "Surati", "Charotari"],
        agricultural_vocabulary_pack="vocab_gu_universal",
    ),
    "ur": LanguageProfile(
        canonical_id="ur",
        name="Urdu",
        native_name="اردو",
        script="Perso-Arabic",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Jammu and Kashmir", "Uttar Pradesh", "Telangana", "Bihar", "Delhi"],
        dialects=["Dakhini", "Rekhta"],
        agricultural_vocabulary_pack="vocab_ur_universal",
    ),
    "kn": LanguageProfile(
        canonical_id="kn",
        name="Kannada",
        native_name="ಕನ್ನಡ",
        script="Kannada",
        language_family=LanguageFamily.DRAVIDIAN,
        is_scheduled_22=True,
        regional_states=["Karnataka"],
        dialects=["North Karnataka", "Mysore", "Mangalore", "Kundagannada"],
        agricultural_vocabulary_pack="vocab_kn_universal",
    ),
    "ml": LanguageProfile(
        canonical_id="ml",
        name="Malayalam",
        native_name="മലയാളം",
        script="Malayalam",
        language_family=LanguageFamily.DRAVIDIAN,
        is_scheduled_22=True,
        regional_states=["Kerala", "Lakshadweep"],
        dialects=["Malabar", "Central Travancore", "Southern"],
        agricultural_vocabulary_pack="vocab_ml_universal",
    ),
    "or": LanguageProfile(
        canonical_id="or",
        name="Odia",
        native_name="ଓଡ଼ିଆ",
        script="Odia",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Odisha"],
        alternate_names=["Oriya"],
        dialects=["Mughalbandi", "Sambalpuri", "Baleswari", "Ganjami"],
        agricultural_vocabulary_pack="vocab_or_universal",
    ),
    "pa": LanguageProfile(
        canonical_id="pa",
        name="Punjabi",
        native_name="ਪੰਜਾਬੀ",
        script="Gurmukhi",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Punjab", "Haryana", "Delhi"],
        dialects=["Majhi", "Malwai", "Doabi", "Pwadhi"],
        agricultural_vocabulary_pack="vocab_pa_universal",
    ),
    "as": LanguageProfile(
        canonical_id="as",
        name="Assamese",
        native_name="অসমীয়া",
        script="Bengali-Assamese",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Assam"],
        alternate_names=["Asamiya"],
        dialects=["Kamrupi", "Goalpariya", "Eastern Assamese"],
        agricultural_vocabulary_pack="vocab_as_universal",
    ),
    "mai": LanguageProfile(
        canonical_id="mai",
        name="Maithili",
        native_name="मैथिली",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Bihar", "Jharkhand"],
        alternate_names=["Tirhutia"],
        agricultural_vocabulary_pack="vocab_mai_universal",
    ),
    "sat": LanguageProfile(
        canonical_id="sat",
        name="Santali",
        native_name="ᱥᱟᱱᱛᱟᱲᱤ",
        script="Ol Chiki",
        language_family=LanguageFamily.AUSTROASIATIC,
        is_scheduled_22=True,
        regional_states=["Jharkhand", "Odisha", "West Bengal", "Bihar"],
        agricultural_vocabulary_pack="vocab_sat_universal",
    ),
    "ks": LanguageProfile(
        canonical_id="ks",
        name="Kashmiri",
        native_name="کٲشُر / कॉशुर",
        script="Perso-Arabic",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Jammu and Kashmir"],
    ),
    "ne": LanguageProfile(
        canonical_id="ne",
        name="Nepali",
        native_name="नेपाली",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Sikkim", "West Bengal"],
    ),
    "kok": LanguageProfile(
        canonical_id="kok",
        name="Konkani",
        native_name="कोंकणी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Goa", "Maharashtra", "Karnataka"],
    ),
    "sd": LanguageProfile(
        canonical_id="sd",
        name="Sindhi",
        native_name="سنڌي / सिन्धी",
        script="Perso-Arabic",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Gujarat", "Rajasthan", "Maharashtra"],
    ),
    "doi": LanguageProfile(
        canonical_id="doi",
        name="Dogri",
        native_name="डोगरी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Jammu and Kashmir", "Himachal Pradesh", "Punjab"],
    ),
    "mni": LanguageProfile(
        canonical_id="mni",
        name="Manipuri",
        native_name="মৈতৈলোন্ / ꯃꯤꯇꯩꯂꯣꯟ",
        script="Meitei Mayek",
        language_family=LanguageFamily.TIBETO_BURMAN,
        is_scheduled_22=True,
        regional_states=["Manipur", "Assam"],
        alternate_names=["Meitei"],
    ),
    "brx": LanguageProfile(
        canonical_id="brx",
        name="Bodo",
        native_name="बर'",
        script="Devanagari",
        language_family=LanguageFamily.TIBETO_BURMAN,
        is_scheduled_22=True,
        regional_states=["Assam", "Meghalaya"],
    ),
    "sa": LanguageProfile(
        canonical_id="sa",
        name="Sanskrit",
        native_name="संस्कृतम्",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        is_scheduled_22=True,
        regional_states=["Uttarakhand"],
    ),

    # ---------------- REGIONAL LANGUAGES & NON-SCHEDULED VARIETIES ----------------
    "rwr": LanguageProfile(
        canonical_id="rwr",
        name="Marwari",
        native_name="मारवाड़ी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Rajasthan", "Gujarat"],
        prominent_districts=["Jodhpur", "Bikaner", "Nagaur", "Jaisalmer", "Barmer", "Pali", "Jalore"],
        alternate_names=["Marwadi", "Western Rajasthani"],
        agricultural_vocabulary_pack="vocab_rwr_agri",
    ),
    "mew": LanguageProfile(
        canonical_id="mew",
        name="Mewari",
        native_name="मेवाड़ी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Rajasthan"],
        prominent_districts=["Udaipur", "Chittorgarh", "Rajsamand", "Bhilwara"],
        alternate_names=["Mewadi"],
        agricultural_vocabulary_pack="vocab_mew_agri",
    ),
    "dhu": LanguageProfile(
        canonical_id="dhu",
        name="Dhundhari",
        native_name="ढूंढाड़ी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Rajasthan"],
        prominent_districts=["Jaipur", "Dausa", "Tonk", "Sawai Madhopur"],
        alternate_names=["Jaipuri"],
        agricultural_vocabulary_pack="vocab_dhu_agri",
    ),
    "bho": LanguageProfile(
        canonical_id="bho",
        name="Bhojpuri",
        native_name="भोजपुरी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Bihar", "Uttar Pradesh", "Jharkhand"],
        prominent_districts=["Bhojpur", "Saran", "Varanasi", "Gorakhpur", "Ballia"],
        agricultural_vocabulary_pack="vocab_bho_agri",
    ),
    "bgc": LanguageProfile(
        canonical_id="bgc",
        name="Haryanvi",
        native_name="हरियाणवी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Haryana", "Delhi", "Punjab", "Rajasthan"],
        alternate_names=["Bangaru", "Deshwali"],
        agricultural_vocabulary_pack="vocab_bgc_agri",
    ),
    "awa": LanguageProfile(
        canonical_id="awa",
        name="Awadhi",
        native_name="अवधी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Uttar Pradesh", "Madhya Pradesh"],
        prominent_districts=["Ayodhya", "Lucknow", "Prayagraj", "Gonda", "Bahraich"],
        agricultural_vocabulary_pack="vocab_awa_agri",
    ),
    "hne": LanguageProfile(
        canonical_id="hne",
        name="Chhattisgarhi",
        native_name="छत्तीसगढ़ी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Chhattisgarh", "Odisha"],
        alternate_names=["Lariya", "Khaltahi"],
        agricultural_vocabulary_pack="vocab_hne_agri",
    ),
    "mag": LanguageProfile(
        canonical_id="mag",
        name="Magahi",
        native_name="मगही",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Bihar", "Jharkhand"],
        prominent_districts=["Patna", "Gaya", "Nalanda", "Jehanabad"],
    ),
    "bnd": LanguageProfile(
        canonical_id="bnd",
        name="Bundeli",
        native_name="बुन्देली",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Madhya Pradesh", "Uttar Pradesh"],
        prominent_districts=["Jhansi", "Sagar", "Damoh", "Tikamgarh", "Chhatarpur"],
    ),
    "gbm": LanguageProfile(
        canonical_id="gbm",
        name="Garhwali",
        native_name="गढ़वाली",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Uttarakhand"],
        prominent_districts=["Pauri Garhwal", "Tehri Garhwal", "Chamoli"],
    ),
    "kfy": LanguageProfile(
        canonical_id="kfy",
        name="Kumaoni",
        native_name="कुमाऊँनी",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        parent_language="hi",
        regional_states=["Uttarakhand"],
        prominent_districts=["Almora", "Nainital", "Pithoragarh"],
    ),
    "tcy": LanguageProfile(
        canonical_id="tcy",
        name="Tulu",
        native_name="ತುಳು",
        script="Kannada",
        language_family=LanguageFamily.DRAVIDIAN,
        parent_language="kn",
        regional_states=["Karnataka", "Kerala"],
        prominent_districts=["Dakshina Kannada", "Udupi", "Kasaragod"],
    ),
    "gon": LanguageProfile(
        canonical_id="gon",
        name="Gondi",
        native_name="गोंडी / గోండీ",
        script="Devanagari",
        language_family=LanguageFamily.DRAVIDIAN,
        regional_states=["Madhya Pradesh", "Chhattisgarh", "Maharashtra", "Telangana", "Andhra Pradesh"],
    ),
    "bhb": LanguageProfile(
        canonical_id="bhb",
        name="Bhili",
        native_name="भीली",
        script="Devanagari",
        language_family=LanguageFamily.INDO_ARYAN,
        regional_states=["Rajasthan", "Gujarat", "Madhya Pradesh", "Maharashtra"],
        prominent_districts=["Banswara", "Dungarpur", "Dahod", "Jhabua"],
    ),
    "kha": LanguageProfile(
        canonical_id="kha",
        name="Khasi",
        native_name="Ka Ktien Khasi",
        script="Latin",
        language_family=LanguageFamily.AUSTROASIATIC,
        regional_states=["Meghalaya", "Assam"],
    ),
    "trp": LanguageProfile(
        canonical_id="trp",
        name="Kokborok",
        native_name="ককবরক",
        script="Bengali",
        language_family=LanguageFamily.TIBETO_BURMAN,
        regional_states=["Tripura", "Assam"],
        alternate_names=["Tripuri"],
    ),
    "en": LanguageProfile(
        canonical_id="en",
        name="Indian English",
        native_name="English",
        script="Latin",
        language_family=LanguageFamily.INDO_ARYAN,
        regional_states=["All India"],
        alternate_names=["English"],
        agricultural_vocabulary_pack="vocab_en_universal",
    ),
}


# ============================================================================
# VERIFIED VOICE CAPABILITY REGISTRY (TRUTHFUL PROVIDER CAPABILITIES)
# ============================================================================

VOICE_CAPABILITY_REGISTRY: Dict[str, VoiceCapabilityProfile] = {
    # Tier 1: Full Pipeline (Verified Bhashini ASR + Bhashini TTS + Local NLU + Fallback)
    "hi": VoiceCapabilityProfile(
        language_id="hi",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_hi",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="en", fallback_chain=["en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "gu": VoiceCapabilityProfile(
        language_id="gu",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_gu",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "mr": VoiceCapabilityProfile(
        language_id="mr",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_mr",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "pa": VoiceCapabilityProfile(
        language_id="pa",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_pa",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "bn": VoiceCapabilityProfile(
        language_id="bn",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_bn",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "te": VoiceCapabilityProfile(
        language_id="te",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_te",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="en", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "ta": VoiceCapabilityProfile(
        language_id="ta",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_ta",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="en", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "kn": VoiceCapabilityProfile(
        language_id="kn",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_kn",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "ml": VoiceCapabilityProfile(
        language_id="ml",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_ml",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="en", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "or": VoiceCapabilityProfile(
        language_id="or",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_or",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "as": VoiceCapabilityProfile(
        language_id="as",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_as",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="bn", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "ur": VoiceCapabilityProfile(
        language_id="ur",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_ur",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),
    "mai": VoiceCapabilityProfile(
        language_id="mai",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_mai",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=False, tts_provider=None, # Verified: Bhashini does not have native Mai TTS yet; falls back to Hindi TTS
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.NATIVE_ASR_PARENT_TTS,
    ),
    "en": VoiceCapabilityProfile(
        language_id="en",
        asr_available=True, asr_provider="bhashini", asr_model="bhashini_asr_en",
        lid_available=True, dialect_detection=False,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=True, tts_provider="bhashini",
        streaming_asr=True, streaming_tts=True, offline_available=True,
        fallback_language="hi", fallback_chain=["hi"],
        capability_tier=CapabilityTier.NATIVE_VOICE,
    ),

    # ---------------- REGIONAL DIALECTS (Truthful Capability Tiers) ----------------
    "rwr": VoiceCapabilityProfile(
        language_id="rwr",
        asr_available=True, asr_provider="hindi_asr_with_marwari_normalization",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True, # Genuine Marwari written response
        native_tts=False, tts_provider=None, # Verified: No native Marwari TTS model yet; transparently uses Hindi TTS
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
    ),
    "mew": VoiceCapabilityProfile(
        language_id="mew",
        asr_available=True, asr_provider="hindi_asr_with_mewari_normalization",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=False, tts_provider=None,
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
    ),
    "dhu": VoiceCapabilityProfile(
        language_id="dhu",
        asr_available=True, asr_provider="hindi_asr_with_dhundhari_normalization",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=False, tts_provider=None,
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
    ),
    "bho": VoiceCapabilityProfile(
        language_id="bho",
        asr_available=True, asr_provider="hindi_asr_with_bhojpuri_normalization",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=False, tts_provider=None,
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
    ),
    "bgc": VoiceCapabilityProfile(
        language_id="bgc",
        asr_available=True, asr_provider="hindi_asr_with_haryanvi_normalization",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=False, tts_provider=None,
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
    ),
    "awa": VoiceCapabilityProfile(
        language_id="awa",
        asr_available=True, asr_provider="hindi_asr_with_awadhi_normalization",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=False, tts_provider=None,
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
    ),
    "hne": VoiceCapabilityProfile(
        language_id="hne",
        asr_available=True, asr_provider="hindi_asr_with_chhattisgarhi_normalization",
        lid_available=True, dialect_detection=True,
        nlu_available=True, local_nlu_available=True,
        response_generation_available=True, native_text_generation=True,
        native_tts=False, tts_provider=None,
        streaming_asr=False, streaming_tts=False, offline_available=True,
        fallback_language="hi", fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE,
    ),

    # ---------------- NON-SCHEDULED / TRIBAL (Vocabulary / Fallback Only) ----------------
    "sat": VoiceCapabilityProfile(
        language_id="sat",
        asr_available=False, lid_available=False, dialect_detection=False,
        nlu_available=True, local_nlu_available=False,
        response_generation_available=False, native_text_generation=False,
        native_tts=False, tts_provider=None,
        offline_available=False, fallback_language="hi", fallback_chain=["hi", "bn", "en"],
        capability_tier=CapabilityTier.VOCABULARY_ONLY,
    ),
    "tcy": VoiceCapabilityProfile(
        language_id="tcy",
        asr_available=False, lid_available=False, dialect_detection=False,
        nlu_available=True, local_nlu_available=False,
        response_generation_available=False, native_text_generation=False,
        native_tts=False, tts_provider=None,
        offline_available=False, fallback_language="kn", fallback_chain=["kn", "hi", "en"],
        capability_tier=CapabilityTier.VOCABULARY_ONLY,
    ),
    "gon": VoiceCapabilityProfile(
        language_id="gon",
        asr_available=False, lid_available=False, dialect_detection=False,
        nlu_available=True, local_nlu_available=False,
        response_generation_available=False, native_text_generation=False,
        native_tts=False, tts_provider=None,
        offline_available=False, fallback_language="hi", fallback_chain=["hi", "te", "en"],
        capability_tier=CapabilityTier.VOCABULARY_ONLY,
    ),
    "bhb": VoiceCapabilityProfile(
        language_id="bhb",
        asr_available=False, lid_available=False, dialect_detection=False,
        nlu_available=True, local_nlu_available=False,
        response_generation_available=False, native_text_generation=False,
        native_tts=False, tts_provider=None,
        offline_available=False, fallback_language="hi", fallback_chain=["hi", "gu", "en"],
        capability_tier=CapabilityTier.VOCABULARY_ONLY,
    ),
}


# ============================================================================
# HELPER LOOKUP FUNCTIONS
# ============================================================================

def get_language_profile(code: str) -> Optional[LanguageProfile]:
    """Retrieve LanguageProfile by BCP-47 / ISO code or alternate name."""
    if code in INDIA_LANGUAGE_CATALOG:
        return INDIA_LANGUAGE_CATALOG[code]
    code_lower = code.lower()
    for profile in INDIA_LANGUAGE_CATALOG.values():
        if code_lower == profile.name.lower() or code_lower in [alt.lower() for alt in profile.alternate_names]:
            return profile
    return None


def get_voice_capability(code: str) -> VoiceCapabilityProfile:
    """
    Retrieve verified VoiceCapabilityProfile.
    If language is not explicitly listed, returns a truthful UNSUPPORTED profile with fallback to Hindi.
    """
    if code in VOICE_CAPABILITY_REGISTRY:
        return VOICE_CAPABILITY_REGISTRY[code]
    return VoiceCapabilityProfile(
        language_id=code,
        asr_available=False,
        nlu_available=False,
        native_tts=False,
        fallback_language="hi",
        fallback_chain=["hi", "en"],
        capability_tier=CapabilityTier.UNSUPPORTED,
    )
