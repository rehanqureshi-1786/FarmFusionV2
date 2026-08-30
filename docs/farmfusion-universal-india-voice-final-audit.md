# FarmFusion Universal India-Wide Multilingual Voice Agent — Final Architecture & Audit Report

## 1. Executive Summary

FarmFusion is now architected and verified as a **Universal India-Wide Multilingual Voice Agent** operating on a **Trainable + Local-First + Hybrid Architecture**. 

- **Single Agricultural Agent**: One unified LangGraph state machine and one typed `ToolRegistry` serving all languages and dialects.
- **Language as an Interface Layer**: Language is strictly an interaction interface; agricultural domain intelligence and deterministic ML pipelines are never duplicated per language.
- **Decoupled Architecture**: Linguistic classification (`LanguageProfile`) is decoupled from verified runtime execution (`VoiceCapabilityProfile`), guaranteeing zero-fabrication of provider or model capabilities.

---

## 2. Linguistic Inventory & Capability Matrix

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Total Linguistic Entries** | **38 entries** | Full index across 4 language families (Indo-Aryan, Dravidian, Austroasiatic, Tibeto-Burman) |
| **Scheduled Languages (8th Schedule)** | **22 languages** | Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Urdu, Kannada, Malayalam, Odia, Punjabi, Assamese, Maithili, Santali, Kashmiri, Nepali, Konkani, Sindhi, Dogri, Manipuri, Bodo, Sanskrit |
| **Regional & Non-Scheduled Varieties** | **16 varieties** | Marwari, Mewari, Dhundhari, Bhojpuri, Haryanvi, Awadhi, Chhattisgarhi, Magahi, Bundeli, Garhwali, Kumaoni, Tulu, Gondi, Bhili, Khasi, Kokborok |
| **Native Voice (ASR + TTS)** | **13 languages** | `hi`, `gu`, `mr`, `pa`, `bn`, `te`, `ta`, `kn`, `ml`, `or`, `as`, `ur`, `en` |
| **Native ASR + Parent TTS** | **1 language** | `mai` (Maithili ASR with transparent Hindi TTS fallback) |
| **Dialect Understanding + Parent TTS** | **7 dialects** | `rwr` (Marwari), `mew` (Mewari), `dhu` (Dhundhari), `bho` (Bhojpuri), `bgc` (Haryanvi), `awa` (Awadhi), `hne` (Chhattisgarhi) |
| **Vocabulary / Normalization Only** | **4 varieties** | `sat` (Santali), `tcy` (Tulu), `gon` (Gondi), `bhb` (Bhili) |
| **Unsupported / Unknown** | **Dynamic** | Truthfully returns `UNSUPPORTED` tier without inventing answers |

---

## 3. Local-First & Hybrid Provider Architecture

### 3.1 Local Voice Stack (`backend/app/voice/local/`)
- **Lightweight Local NLU**: [`agri_nlu_multilingual_v1`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/models/agri_nlu_multilingual_v1/model.joblib) (350.34 KB, $< 1.5$ ms CPU latency) trained on verified `GODL-India` data.
- **Hardware Tier Profiling**: Assesses device RAM/CPU into `LOW_END`, `MID_RANGE`, and `HIGH_END`.
- **Zero-Fabrication Registry**: [`LocalModelRegistry`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/model_registry.py) confirms physical binary existence before reporting availability.
- **Modular Language Packs**: 15 self-contained packages (`hi`, `gu`, `mr`, `pa`, `bn`, `ta`, `te`, `kn`, `ml`, `or`, `as`, `ur`, `mai`, `hi_rwr`, `hi_mew`).

### 3.2 Confidence Cascade
```
Farmer Utterance (Voice / Text)
       │
       ▼
Local Fast-Path NLU (LocalAgriculturalNLUEngine)
       │
  Confidence >= 0.65?
    ├── YES ──► Canonical Semantic Frame ──► ToolRegistry
    └── NO  ──► Multilingual / Cloud Cascade (IntentClassificationNode)
                     │
               Confidence >= 0.60?
                 ├── YES ──► Canonical Semantic Frame ──► ToolRegistry
                 └── NO  ──► Clarification Question (Safety Gate #6)
```

### 3.3 Provider Routing & Transparent Metadata
Universal Voice Provider Router dispatches requests with explicit audit tags:
- `selected_provider`: Local engine or Bhashini ULCA API.
- `native_tts`: `true` if authentic native voice model exists, `false` otherwise.
- `fallback_used`: `true` when parent language TTS fallback is active.
- `fallback_reason`: e.g. `"NO_NATIVE_TTS_FOR_RWR_TRANSPARENT_FALLBACK_TO_HI"`.

---

## 4. Safety & Zero-Fabrication Guarantees

1. **Deterministic Agriculture**: Weather is strictly fetched from Open-Meteo, market prices from the Prophet+LightGBM ensemble, and crop recommendations from XGBoost V2 / Mode B rule trees.
2. **No Numeric Hallucination**: N, P, K, pH, rainfall, temperature, and mandi prices are never generated or modified by LLM/NLP layers.
3. **Offline Mode Safety**: Offline execution returns `OFFLINE_NETWORK_REQUIRED` for cloud APIs without fabricating numbers.

---

## 5. Verification & Test Suite Summary

- **Total Backend Pytest Suite**: **212 / 212 passed (100% PASS)**
  - Local Model Inference & Safety: 3 tests
  - Local Voice REST API: 4 tests
  - Universal India-Wide Platform: 6 tests
  - India-Wide Voice Platform: 37 tests
  - Voice Training Infrastructure: 10 tests
  - Local Voice Architecture & Registry: 11 tests
  - Multi-Turn Agricultural Dialogue: 4 tests
  - Crop Recommendation ML V2: 100% preserved
- **Android Gradle Unit Tests & Compilation**: **`BUILD SUCCESSFUL` (25 actionable tasks executed)**
- **Real Physical Device Testing**: `REAL DEVICE VOICE TEST NOT AVAILABLE` (No active ADB USB connection detected at audit time; hardware status truthfully logged).
