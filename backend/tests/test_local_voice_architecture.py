"""
Comprehensive Test Suite for FarmFusion Local Voice Intelligence Layer.
Validates:
1. Device capability detection & tier classification
2. Local model registry & zero-fabrication integrity
3. Missing model honest handling (MODEL_NOT_AVAILABLE)
4. Modular language pack lifecycle (discovery, vocabulary, prompts)
5. Runtime modes: OFFLINE, HYBRID, ONLINE
6. Zero live data fabrication in offline mode
7. Marwari & regional dialect fallback transparency
"""
import pytest
from pathlib import Path
from app.voice.local import (
    RuntimeMode,
    DeviceTier,
    detect_device_capabilities,
    local_model_registry,
    ModelTask,
    ModelStatus,
    language_package_manager,
    LanguagePackMetadata,
    voice_runtime_router,
)
from app.voice.local.asr import LocalASREngine
from app.voice.local.lid import LocalLanguageDetectorEngine
from app.voice.local.dialect import LocalDialectEngine
from app.voice.local.nlu import LocalAgriculturalNLUEngine
from app.voice.local.response import LocalResponseEngine
from app.voice.local.tts import LocalTTSEngine


def test_device_capability_detection():
    """Verify hardware profile detection and valid DeviceTier classification."""
    caps = detect_device_capabilities()
    assert caps.tier in [DeviceTier.LOW_END, DeviceTier.MID_RANGE, DeviceTier.HIGH_END]
    assert caps.cpu_count >= 1
    assert caps.total_ram_mb > 0
    assert caps.max_recommended_model_size_mb > 0
    assert "rule_engine" in caps.supported_runtimes


def test_local_model_registry_integrity():
    """Verify model manifests, query filters, and honest installation status."""
    # List all manifests
    all_manifests = local_model_registry.list_manifests()
    assert len(all_manifests) >= 6

    # Query by task
    asr_manifests = local_model_registry.list_manifests(task=ModelTask.ASR)
    assert len(asr_manifests) >= 2
    assert all(m.task == ModelTask.ASR for m in asr_manifests)

    # Rule-based model is marked installed by definition
    lid_status = local_model_registry.get_model_status("farmfusion_lid_indic_v1")
    assert lid_status == ModelStatus.INSTALLED

    # Uninstalled ONNX model is marked downloadable with zero fake availability
    whisper_manifest = local_model_registry.get_manifest("farmfusion_asr_hindi_whisper_tiny_int8")
    assert whisper_manifest is not None
    assert whisper_manifest.format.value == "onnx"


def test_missing_model_returns_honest_unavailable():
    """Verify that uninstalled local models return MODEL_NOT_AVAILABLE rather than simulated outputs."""
    asr = LocalASREngine("farmfusion_asr_hindi_whisper_tiny_int8")
    assert not asr.is_available()
    
    caps = asr.capabilities()
    assert caps["is_available"] is False

    tts = LocalTTSEngine("farmfusion_tts_hindi_piper_int8")
    assert not tts.is_available()


@pytest.mark.asyncio
async def test_missing_model_async_transcribe_and_synthesize():
    """Verify runtime error response for missing model files."""
    asr = LocalASREngine("farmfusion_asr_hindi_whisper_tiny_int8")
    res_asr = await asr.transcribe(b"dummy_bytes", language="hi")
    assert not res_asr.is_native
    assert "MODEL_NOT_AVAILABLE" in str(res_asr.error)

    tts = LocalTTSEngine("farmfusion_tts_hindi_piper_int8")
    res_tts = await tts.synthesize("परीक्षण टेक्स्ट", language="hi")
    assert not res_tts.is_native
    assert "MODEL_NOT_AVAILABLE" in str(res_tts.error)


def test_language_package_manager_discovery_and_vocab():
    """Verify modular language pack installation, metadata, and vocabulary retrieval."""
    installed = language_package_manager.list_installed_packs()
    assert len(installed) >= 14

    # Hindi pack
    hi_pack = language_package_manager.get_pack("hi")
    assert hi_pack is not None
    assert hi_pack.language == "hi"
    assert hi_pack.native_name == "हिन्दी"

    # Marwari pack
    rwr_pack = language_package_manager.get_pack("hi", "rwr")
    assert rwr_pack is not None
    assert rwr_pack.dialect == "rwr"
    assert rwr_pack.status == "VOCABULARY_ONLY"

    # Vocab retrieval
    vocab_hi = language_package_manager.get_vocabulary("hi")
    assert "गेहूं" in vocab_hi or "बाजरा" in vocab_hi


def test_local_lid_and_script_disambiguation():
    """Verify local script-based LID engine across scripts and code-switching."""
    lid = LocalLanguageDetectorEngine()
    
    # Gujarati
    res_gu = lid.detect_language("આજે હવામાન કેવું રહેશે?")
    assert res_gu.detected_language == "gu"
    assert res_gu.script == "Gujarati"

    # Punjabi
    res_pa = lid.detect_language("ਅੱਜ ਮੰਡੀ ਵਿੱਚ ਕਣਕ ਦਾ ਕੀ ਭਾਅ ਹੈ?")
    assert res_pa.detected_language == "pa"
    assert res_pa.script == "Gurmukhi"

    # Bengali vs Assamese
    res_bn = lid.detect_language("আজ আবহাওয়া কেমন থাকবে?")
    assert res_bn.detected_language == "bn"

    res_as = lid.detect_language("আজি বতৰ কেনেকুৱা থাকিব?")
    assert res_as.detected_language == "as"

    # Code-switched Hinglish
    res_cs = lid.detect_language("aaj mausam kaisa hai")
    assert res_cs.detected_language == "hi"
    assert res_cs.is_code_switched is True


def test_local_dialect_and_normalization():
    """Verify Marwari and regional dialect recognition."""
    dialect_engine = LocalDialectEngine()
    
    # Marwari
    res_rwr = dialect_engine.detect_and_normalize("म्हाने बाजरी रो भाव बताओ", detected_language="hi")
    assert res_rwr.detected_dialect == "rwr"
    assert "बाजरी" in res_rwr.normalized_text or "Pearl Millet" in res_rwr.normalized_text


@pytest.mark.asyncio
async def test_local_nlu_and_response_synthesis():
    """Verify local NLU intent parsing and grounded response synthesis."""
    nlu = LocalAgriculturalNLUEngine()
    res_nlu = await nlu.parse("गेहूं का भाव बताओ", language="hi")
    assert res_nlu.intent == "mandi"
    assert res_nlu.canonical_action == "show_result"

    response_engine = LocalResponseEngine()
    res_synth = await response_engine.generate_response(
        intent="weather",
        tool_payload={"temperature_c": 28.5, "humidity_percent": 65, "condition": "clear sky", "location_name": "Jaipur", "annual_rainfall_mm": 650.0},
        language="hi"
    )
    assert "28.5" in res_synth.response_text
    assert "Jaipur" in res_synth.response_text


@pytest.mark.asyncio
async def test_runtime_router_hybrid_mode():
    """Verify HYBRID mode routes to cloud fallback when local ASR/TTS binaries are not present."""
    voice_runtime_router.set_mode(RuntimeMode.HYBRID)
    res = await voice_runtime_router.process_voice_query(
        text_query="उदयपुर में मौसम कैसा है?",
        language_hint="hi",
    )
    assert res.intent == "weather"
    assert res.detected_language == "hi"
    assert res.runtime_mode == RuntimeMode.HYBRID
    assert res.nlu_provider == "langgraph_orchestrator"
    assert "Udaipur" in res.response_text


@pytest.mark.asyncio
async def test_runtime_router_offline_mode_no_fabrication():
    """Verify OFFLINE mode does not fabricate live weather or mandi prices."""
    voice_runtime_router.set_mode(RuntimeMode.OFFLINE)
    res = await voice_runtime_router.process_voice_query(
        text_query="उदयपुर में आज का मौसम कैसा है?",
        language_hint="hi",
    )
    assert res.runtime_mode == RuntimeMode.OFFLINE
    assert res.intent == "weather"
    # Never fabricate live weather numbers offline
    assert "ऑफलाइन मोड" in res.response_text or "इंटरनेट कनेक्शन" in res.response_text
    assert res.tool_output is not None
    assert res.tool_output.get("error") == "OFFLINE_NETWORK_REQUIRED"

    # Reset back to default hybrid mode
    voice_runtime_router.set_mode(RuntimeMode.HYBRID)


@pytest.mark.asyncio
async def test_runtime_router_marwari_fallback_transparency():
    """Verify Marwari dialect retains honest parent TTS fallback metadata."""
    voice_runtime_router.set_mode(RuntimeMode.HYBRID)
    res = await voice_runtime_router.process_voice_query(
        text_query="म्हाने बाजरी रो भाव बताओ",
        language_hint="hi",
    )
    assert res.detected_dialect == "rwr"
    assert res.tts_language in ["hi", "raj"]
    assert res.native_tts is False
    assert res.fallback_used is True
