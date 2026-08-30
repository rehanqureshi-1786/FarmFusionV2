"""
Comprehensive Test Suite for FarmFusion Universal India-Wide Multilingual Platform.
Validates:
1. Complete Indian Language Inventory vs Voice Capability decoupling
2. 22 Scheduled languages + Regional non-scheduled varieties
3. Canonical Semantic Mapping (crops, soils, operations)
4. Universal Provider Router (ASR and TTS transparent routing)
5. Multi-turn language switching & preference memory
6. Truthful capability tiers without capability fabrication
"""
import pytest
from app.voice.profiles import (
    INDIA_LANGUAGE_CATALOG,
    VOICE_CAPABILITY_REGISTRY,
    get_language_profile,
    get_voice_capability,
    CapabilityTier,
    LanguageFamily,
)
from app.voice.canonical import (
    map_to_canonical_crop,
    CanonicalCrop,
    CanonicalSemanticFrame,
    CanonicalIntent,
    CanonicalAgriculturalEntities,
)
from app.voice.provider_router import universal_voice_router
from app.orchestrator.graph import run_orchestrator_pipeline


def test_01_language_catalog_inventory_completeness():
    """Verify all 22 scheduled languages are indexed with authentic linguistic facts."""
    scheduled_codes = [
        "hi", "bn", "te", "mr", "ta", "gu", "ur", "kn", "ml", "or",
        "pa", "as", "mai", "sat", "ks", "ne", "kok", "sd", "doi", "mni", "brx", "sa"
    ]
    for code in scheduled_codes:
        profile = get_language_profile(code)
        assert profile is not None, f"Scheduled language '{code}' missing from catalog"
        assert profile.is_scheduled_22 is True
        assert len(profile.native_name) > 0
        assert profile.language_family in [
            LanguageFamily.INDO_ARYAN,
            LanguageFamily.DRAVIDIAN,
            LanguageFamily.AUSTROASIATIC,
            LanguageFamily.TIBETO_BURMAN,
        ]


def test_02_regional_and_non_scheduled_varieties():
    """Verify regional varieties (Marwari, Mewari, Bhojpuri, Haryanvi, Gondi, Bhili, Tulu, etc.) exist in catalog."""
    varieties = ["rwr", "mew", "dhu", "bho", "bgc", "awa", "hne", "tcy", "gon", "bhb"]
    for code in varieties:
        profile = get_language_profile(code)
        assert profile is not None, f"Regional variety '{code}' missing from catalog"
        assert len(profile.regional_states) > 0


def test_03_capability_profile_truthful_tiers():
    """Verify that presence in catalog DOES NOT falsely imply native TTS/ASR."""
    # Hindi has native voice
    hi_cap = get_voice_capability("hi")
    assert hi_cap.capability_tier == CapabilityTier.NATIVE_VOICE
    assert hi_cap.native_tts is True

    # Marwari has genuine dialect understanding but transparently uses parent Hindi TTS
    rwr_cap = get_voice_capability("rwr")
    assert rwr_cap.capability_tier == CapabilityTier.DIALECT_UNDERSTANDING_PARENT_RESPONSE
    assert rwr_cap.native_tts is False
    assert rwr_cap.fallback_language == "hi"

    # Maithili has Bhashini ASR but uses parent Hindi TTS
    mai_cap = get_voice_capability("mai")
    assert mai_cap.capability_tier == CapabilityTier.NATIVE_ASR_PARENT_TTS
    assert mai_cap.native_tts is False

    # Gondi has vocabulary catalog only
    gon_cap = get_voice_capability("gon")
    assert gon_cap.capability_tier == CapabilityTier.VOCABULARY_ONLY
    assert gon_cap.native_tts is False
    assert gon_cap.asr_available is False

    # Unknown code returns unsupported
    un_cap = get_voice_capability("xyz_unknown")
    assert un_cap.capability_tier == CapabilityTier.UNSUPPORTED


def test_04_canonical_crop_surface_mapping():
    """Verify regional surface dialect words map to canonical crop enums."""
    # Pearl Millet variants
    assert map_to_canonical_crop("बाजरो") == CanonicalCrop.PEARL_MILLET
    assert map_to_canonical_crop("बाजरी") == CanonicalCrop.PEARL_MILLET
    assert map_to_canonical_crop("bajra") == CanonicalCrop.PEARL_MILLET
    assert map_to_canonical_crop("kambu") == CanonicalCrop.PEARL_MILLET

    # Wheat variants
    assert map_to_canonical_crop("गेहूं") == CanonicalCrop.WHEAT
    assert map_to_canonical_crop("कनक") == CanonicalCrop.WHEAT
    assert map_to_canonical_crop("godhumai") == CanonicalCrop.WHEAT

    # Groundnut variants
    assert map_to_canonical_crop("मूंगफली") == CanonicalCrop.GROUNDNUT
    assert map_to_canonical_crop("सींगदाना") == CanonicalCrop.GROUNDNUT
    assert map_to_canonical_crop("peanut") == CanonicalCrop.GROUNDNUT

    # Cotton variants
    assert map_to_canonical_crop("कापूस") == CanonicalCrop.COTTON
    assert map_to_canonical_crop("कपास") == CanonicalCrop.COTTON
    assert map_to_canonical_crop("paruthi") == CanonicalCrop.COTTON

    # Paddy variants
    assert map_to_canonical_crop("धान") == CanonicalCrop.PADDY
    assert map_to_canonical_crop("ਝੋਨਾ") == CanonicalCrop.PADDY


def test_05_provider_router_asr_and_tts_decisions():
    """Verify Universal Voice Provider Router routes with honest fallback metadata."""
    # Routing Tamil ASR -> Native Bhashini
    ta_asr = universal_voice_router.route_asr("ta")
    assert ta_asr.is_native is True
    assert ta_asr.selected_provider == "bhashini"

    # Routing Marwari ASR -> Parent with dialect normalization
    rwr_asr = universal_voice_router.route_asr("hi", dialect="rwr")
    assert rwr_asr.is_native is False
    assert rwr_asr.fallback_used is True

    # Routing Gujarati TTS -> Native
    gu_tts = universal_voice_router.route_tts("gu")
    assert gu_tts.is_native is True
    assert gu_tts.target_language == "gu"

    # Routing Mewari TTS -> Transparent fallback to parent Hindi TTS via Bhashini
    mew_tts = universal_voice_router.route_tts("hi", dialect="mew")
    assert mew_tts.is_native is False
    assert mew_tts.target_language in ["raj", "hi"]
    assert "PARENT" in mew_tts.fallback_reason or "FALLBACK" in mew_tts.fallback_reason or "HI" in mew_tts.fallback_reason


@pytest.mark.asyncio
async def test_06_multi_turn_language_switching_in_orchestrator():
    """
    Test dynamic language switching across turns:
    Turn 1: Hindi query
    Turn 2: Explicit switch: 'अब मरवाड़ी में बोल'
    Turn 3: Marwari interaction
    """
    session_id = "test_multilingual_switch_session"

    # Turn 1: Hindi
    res1 = await run_orchestrator_pipeline(
        user_input="आज मौसम कैसा रहेगा?",
        detected_language="hi",
        session_id=session_id
    )
    assert res1["intent"] == "weather"
    assert res1["detected_language"] == "hi"

    # Turn 2: Switch request
    res2 = await run_orchestrator_pipeline(
        user_input="मारवाड़ी में बोलो",
        detected_language="hi",
        session_id=session_id
    )
    assert res2["intent"] == "dialect_preference"
    assert res2["farmer_preferred_dialect"] == "rwr"

    # Turn 3: Interaction in Marwari
    res3 = await run_orchestrator_pipeline(
        user_input="म्हाने बाजरी रो भाव बताओ",
        detected_language="hi",
        detected_dialect="rwr",
        session_id=session_id
    )
    assert res3["intent"] == "mandi"
    assert res3["response_dialect"] == "rwr"
    assert res3["native_tts"] is False
    assert res3["fallback_used"] is True
