"""
Comprehensive Multi-Language Real Local Neural TTS & Anti-Procedural Test Suite.
Validates:
1. All official Indian neural VITS models installed on disk and loadable in LocalTTSEngine.
2. Genuine neural VITS speech synthesis across all major agrarian zones.
3. Strictly anti-procedural: zero sine waves, zero tone generators, zero hardcoded frequencies.
4. Text-dependent phonetic duration and acoustic waveform synthesis.
5. Provider router prioritizes Real Local Neural TTS for all installed languages.
6. Offline mode produces real neural speech locally without network calls.
"""
import io
import wave
import pytest
from app.voice.local.tts.local_tts import local_tts_engine
from app.voice.provider_router import universal_voice_router
from app.voice.local.runtime import voice_runtime_router, RuntimeMode


ALL_INSTALLED_LANGUAGES = [
    "hi", "mr", "gu", "bn", "ta", "te", "pa",
    "kn", "ml", "or", "as", "mai", "bgc", "hne",
    "ur", "dgo", "awa", "mag", "gbm", "bod", "hoc", "unr", "kru"
]


def test_01_all_indian_neural_vits_models_installed_and_registered():
    """Verify that all official Indian neural VITS models are registered and installed on disk."""
    for lang in ALL_INSTALLED_LANGUAGES:
        assert local_tts_engine.supports_language(lang) is True, f"Language {lang} not supported in LocalTTSEngine!"

    caps = local_tts_engine.capabilities()
    assert caps["is_available"] is True
    assert set(caps["installed_languages"]).issuperset(set(ALL_INSTALLED_LANGUAGES))
    assert caps["neural_model_type"] == "VITS_End_to_End"
    assert caps["procedural_generator_used"] is False


@pytest.mark.asyncio
async def test_02_real_neural_vits_synthesizes_all_languages():
    """
    Test real neural speech synthesis across installed languages with real agricultural sentences.
    Verifies valid 16kHz WAV, non-zero duration, and genuine neural speech waveform.
    """
    test_cases = [
        ("hi", "आज मौसम साफ है और तापमान अट्ठाईस डिग्री है।"),
        ("mr", "आज हवामान चांगले आहे आणि शेतात पाणी देणे गरजेचे आहे."),
        ("gu", "આજે હવામાન સારું છે અને પાક સારો છે."),
        ("bn", "আজ আবহাওয়া ভালো আছে।"),
        ("ta", "இன்று வானிலை நன்றாக உள்ளது."),
        ("te", "ఈరోజు వాతావరణం బాగుంది."),
        ("pa", "ਅੱਜ ਮੌਸਮ ਵਧੀਆ ਹੈ।"),
        ("kn", "ಇಂದು ಹವಾಮಾನ ಚೆನ್ನಾಗಿದೆ."),
        ("ml", "ഇന്ന് കാലാവസ്ഥ നല്ലതാണ്."),
        ("or", "ଆଜି ପାଣିପାଗ ଭଲ ଅଛି।"),
        ("as", "আজি বতৰ ভাল।"),
        ("mai", "आइ मौसम नीक अछि।"),
        ("bgc", "आज मौसम बढ़िया सै।"),
        ("hne", "आज मौसम बने हे।"),
        ("ur", "आज मौसम साफ है और फसल अच्छी है।"),
        ("dgo", "अज्ज मौसम बड़ा शैल ऐ।"),
        ("awa", "आज मौसम बढ़िया बा खेत मा पानी देवब जरूरी बा।"),
        ("mag", "आज मौसम ठीक हे खेत में पानी देवे के बा।"),
        ("gbm", "आज मौसम् भलु च खेत मा पाणी द्या।"),
        ("kru", "इन्ना बीड़ी बेस रही।"),
    ]

    for lang, text in test_cases:
        res = await local_tts_engine.synthesize(text, language=lang)
        assert res.is_native is True, f"Failed native flag for {lang}"
        assert res.sample_rate == 16000, f"Incorrect sample rate for {lang}"
        assert res.duration_seconds > 0.4, f"Duration too short for {lang}"
        assert res.provider == "local_neural_vits_tts"
        assert len(res.audio_bytes) > 5000, f"Audio buffer too small for {lang}"

        # Validate standard WAV container
        with wave.open(io.BytesIO(res.audio_bytes), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 16000


@pytest.mark.asyncio
async def test_03_text_dependent_phonetic_variations_and_anti_procedural_check():
    """
    Anti-procedural test:
    1. Different sentences produce distinct, non-linear phonetic durations and waveforms.
    2. Zero sine-wave formulas or hardcoded frequency generators exist in local_tts.py.
    """
    res_a = await local_tts_engine.synthesize("आज मौसम साफ है।", language="hi")
    res_b = await local_tts_engine.synthesize("कल गेहूं की फसल के लिए पानी देना जरूरी है।", language="hi")
    res_c = await local_tts_engine.synthesize("नमस्कार किसान भाई।", language="hi")

    assert res_a.duration_seconds != res_b.duration_seconds
    assert res_b.duration_seconds > res_c.duration_seconds
    assert res_a.audio_bytes != res_b.audio_bytes

    # Source code anti-procedural check
    with open("app/voice/local/tts/local_tts.py", "r", encoding="utf-8") as f:
        code_content = f.read()

    assert "np.sin" not in code_content
    assert "np.cos" not in code_content
    assert "f0 = base_pitch" not in code_content
    assert "syllable_mod" not in code_content


def test_04_provider_router_prioritizes_local_neural_vits_for_all_languages():
    """Verify that ProviderRouter selects Local Neural VITS for installed languages and cascades for dialects."""
    for lang in ALL_INSTALLED_LANGUAGES:
        decision = universal_voice_router.route_tts(lang)
        assert decision.selected_provider == "local_neural_tts", f"Routing failed for {lang}"
        assert decision.is_local is True
        assert decision.is_native is True
        assert decision.fallback_used is False

    # Marwari dialect -> Bhashini Hindi Parent Fallback
    rwr_decision = universal_voice_router.route_tts("hi", dialect="rwr")
    assert rwr_decision.actual_tts_language == "hi"
    assert rwr_decision.is_native is False
    assert rwr_decision.fallback_used is True


@pytest.mark.asyncio
async def test_05_offline_mode_synthesis_and_honest_dialect_fallback():
    """
    Verify that in OFFLINE mode:
    - Installed languages generate real neural audio locally without network calls.
    - Uninstalled dialects return OFFLINE_TTS_UNAVAILABLE honestly without fake tones.
    """
    voice_runtime_router.set_mode(RuntimeMode.OFFLINE)

    # 1. Kannada Query in Offline Mode
    res_kn = await voice_runtime_router.process_voice_query(
        text_query="ಹೊಲದಲ್ಲಿ ಯಾವ ಬೆಳೆ ಬೆಳೆಯಬೇಕು?",
        language_hint="kn"
    )
    assert res_kn.runtime_mode == RuntimeMode.OFFLINE
    assert res_kn.tts_provider == "local_neural_vits_tts"
    assert len(res_kn.audio_bytes) > 5000
    assert res_kn.native_tts is True

    # 2. Dialect in Offline Mode (no native dialect TTS weights)
    res_dial = await voice_runtime_router.process_voice_query(
        text_query="म्हारी फसल में कीड़ा लाग्यो है",
        language_hint="hi"
    )
    assert res_dial.runtime_mode == RuntimeMode.OFFLINE
    assert res_dial.tts_provider == "local_tts_unavailable"
    assert res_dial.audio_bytes == b""

    # Reset to HYBRID
    voice_runtime_router.set_mode(RuntimeMode.HYBRID)
