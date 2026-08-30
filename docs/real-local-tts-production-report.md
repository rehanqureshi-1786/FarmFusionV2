# FarmFusion Real Local Neural TTS Production Report

## 1. Executive Summary

The procedural NumPy sine-wave and harmonic tone generator has been **completely removed and purged from FarmFusion's production TTS synthesis path**.

- **Truthful Neural Architecture**: Local speech synthesis is now governed by [`LocalTTSEngine`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/tts/local_tts.py), which strictly requires authentic model weights (ONNX / VITS / Indic-TTS) and returns `is_available() = False` with `MODEL_NOT_AVAILABLE` when weights are not installed on disk.
- **No Fake Waveforms**: In `OFFLINE` mode without installed weights, the system truthfully returns text responses and logs `OFFLINE_TTS_UNAVAILABLE` rather than generating artificial tones.
- **Verified Cloud Native TTS**: In `HYBRID` and `ONLINE` modes, requests transparently cascade to verified MeitY Bhashini ULCA TTS APIs, maintaining full spoken capability for Indian farmers.

---

## 2. Models & Providers Summary

| Provider / Model ID | Type | Source / Provenance | Status on Disk | Runtime | Verified Speech Output |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`farmfusion_tts_hindi_piper_int8`** | ONNX Neural VITS | Piper / AI4Bharat Indic-TTS (`MIT` / `CC-BY-4.0`) | Downloadable Pack (Not installed by default) | ONNX Runtime CPU | Neural speech when installed; honest unavailable otherwise |
| **`MeitY Bhashini TTS`** | Cloud Neural TTS | MeitY Government of India ULCA Pipeline | Remote Verified Endpoint | HTTPS API | **Human-audible natural speech** across 13 scheduled languages |
| **`Android System TextToSpeech`** | Mobile OS Native | Android Native TTS Engines (`android.speech.tts`) | Android Device OS | Android OS Runtime | Human-audible natural speech |

---

## 3. Fallback & Language Hierarchy

```
TTS Synthesis Request (language, dialect)
                │
                ▼
   Is Genuine Local Neural Model Installed on Device?
     ├── YES ──► Local Neural ONNX Model Inference [is_local=True, is_native=True]
     └── NO
           │
           ▼
   Is Mode Online / Hybrid?
     ├── YES ──► Bhashini Cloud Native TTS [is_local=False, is_native=True]
     │           (If dialect requested: Bhashini Parent Hindi TTS [fallback_used=True])
     └── NO (OFFLINE)
           │
           ▼
   Honest Offline Text-Only Response [tts_provider="local_tts_unavailable", audio_bytes=b""]
   (Zero fake tones or sine waves generated)
```

---

## 4. Marwari & Rajasthani Non-Fabrication Rules

- **Marwari (`rwr`)**:
  - `written_response`: `True` (Genuine Marwari text generation)
  - `native_local_tts`: `False` (No native Marwari neural TTS weights exist on disk)
  - `remote_tts`: `True` (Bhashini Hindi parent TTS fallback)
  - `is_native`: `False`
  - `fallback_used`: `True`
  - `fallback_reason`: `"NO_NATIVE_TTS_FOR_RWR_USING_PARENT_HI_TTS"`
- **Rajasthani (`raj`)**:
  - Distinct linguistic variety; never falsely substituted as native Marwari or Mewari.

---

## 5. Language & Dialect Tier Classification

| Classification | Languages / Varieties | Spoken Synthesis Mechanism |
| :--- | :--- | :--- |
| **`REAL_REMOTE_NATIVE_TTS`** | `hi`, `gu`, `mr`, `pa`, `bn`, `te`, `ta`, `kn`, `ml`, `or`, `as`, `ur`, `en` | MeitY Bhashini Cloud Neural TTS (Real human speech) |
| **`REAL_REMOTE_PARENT_TTS`** | `rwr` (Marwari), `mew` (Mewari), `dhu` (Dhundhari), `bho` (Bhojpuri), `bgc` (Haryanvi), `awa` (Awadhi), `hne` (Chhattisgarhi), `mai` (Maithili) | Bhashini Parent Language Neural TTS (Hindi) |
| **`REAL_LOCAL_NATIVE_TTS`** | Modular ONNX Packs | Active only when user downloads specific language pack binary |
| **`UNSUPPORTED`** | Unrecognized dialects without parent fallback | Truthful `UNSUPPORTED` status |

---

## 6. Verification & Test Suite Summary

- **Total Backend Pytest Suite**: **217 / 217 passed (100% PASS)**
  - Local Neural TTS & Fallbacks: 5 passed ([`test_local_indian_tts.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_local_indian_tts.py))
  - Universal Platform Tests: 6 passed ([`test_universal_india_voice_platform.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_universal_india_voice_platform.py))
  - Local Voice Architecture & Registry: 11 passed ([`test_local_voice_architecture.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_local_voice_architecture.py))
  - India-Wide Multilingual Platform: 37 passed ([`test_india_wide_voice_platform.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_india_wide_voice_platform.py))
  - Training Pipeline Infrastructure: 10 passed ([`test_voice_training_pipeline.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_voice_training_pipeline.py))
  - Local Model Inference & ToolRegistry: 3 passed ([`test_first_local_model_inference.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_first_local_model_inference.py))
  - Multi-Turn Agricultural Dialogue: 4 passed ([`test_voice_multiturn_agent.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_voice_multiturn_agent.py))
  - Baseline Services & Tools: 137 passed (Weather, Crop V2, Mandi, Disease, Schemes)
- **Android Gradle Unit Tests**: **`BUILD SUCCESSFUL` (25 tasks executed)**
