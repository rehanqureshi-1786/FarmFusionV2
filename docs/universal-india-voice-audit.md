# FarmFusion Universal India-Wide Multilingual Voice Agent — Architecture Audit

## 1. Executive Summary & Baseline

- **Repository Root**: `/home/rdj/FarmFusionFinal`
- **Initial Verified Pytest Baseline**: **206 / 206 tests passed (100%)**
- **Initial Android Unit Test Baseline**: `BUILD SUCCESSFUL` (25 tasks executed)
- **Primary Objective**: Establish FarmFusion as a **Universal India-Wide Multilingual Voice Agent** supporting scheduled languages, non-scheduled regional languages, dialects, and rural agricultural varieties with a **trainable, local-first, hybrid architecture**.

---

## 2. Component Inventory & Audit

### 2.1 Language & Dialect Infrastructure (`backend/app/voice/languages.py`)
- **Current Language Registry**: Contains 38 entries spanning 14 primary scheduled languages and 24 regional varieties/dialects.
- **Dialect Recognition**: Probabilistic keyword & marker matching (`DIALECT_MARKERS`) for Marwari (`rwr`), Mewari (`mew`), Dhundhari (`dhu`), Bhojpuri (`bho`), Haryanvi (`bgc`), Awadhi (`awa`), and Chhattisgarhi (`hne`).
- **Agricultural Vocabulary Catalog**: 185 canonical agricultural terms across crops, soils, diseases, fertilizers, and operations.

### 2.2 Cloud Voice Providers (`backend/app/voice/bhashini.py`)
- **ASR Pipeline**: Bhashini ULCA Pipeline API across 14 Tier-1 and Tier-2 Indian languages.
- **TTS Pipeline**: Bhashini TTS with MD5 audio caching in Redis and automatic parent-language fallback for non-native dialects.
- **Fallbacks**: Transparent fallback reporting with `native_tts=False` and `fallback_used=True`.

### 2.3 Local Voice Stack (`backend/app/voice/local/`)
- **Hardware Profile**: [`capabilities.py`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/capabilities.py) classifying devices into `LOW_END` ($\le$ 2GB RAM), `MID_RANGE` (3–6GB RAM), and `HIGH_END` ($\ge$ 8GB RAM).
- **Model Registry**: [`model_registry.py`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/model_registry.py) guaranteeing zero-fabrication (`is_model_installed()` only true if binary exists and is verified).
- **Language Packs**: [`package_manager.py`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/package_manager.py) managing 15 modular packs.
- **Runtime Router**: [`runtime.py`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/runtime.py) supporting `OFFLINE`, `HYBRID`, and `ONLINE` modes.
- **Local NLU**: [`agri_nlu_multilingual_v1`](file:///home/rdj/FarmFusionFinal/backend/app/voice/local/models/agri_nlu_multilingual_v1/model.joblib) (350.34 KB) trained on verified `GODL-India` agricultural data.

### 2.4 LangGraph Orchestrator & ToolRegistry
- **Single Orchestrator**: One central stateful graph in [`backend/app/orchestrator/graph.py`](file:///home/rdj/FarmFusionFinal/backend/app/orchestrator/graph.py).
- **Single ToolRegistry**: Deterministic tool execution for weather, crop recommendation (V2 ML model), mandi price forecasting, disease photo triage, government schemes, and Android navigation.

### 2.5 Android Jetpack Compose Frontend
- **VoiceAssistantScreen**: [`frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/VoiceAssistantScreen.kt`](file:///home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/ui/screens/VoiceAssistantScreen.kt)
- **ViewModel**: [`frontend/app/src/main/java/com/example/farmfusionapp/viewmodel/VoiceAssistantViewModel.kt`](file:///home/rdj/FarmFusionFinal/frontend/app/src/main/java/com/example/farmfusionapp/viewmodel/VoiceAssistantViewModel.kt)
- **Navigation Safety**: Hardcoded `ALLOWED_DESTINATIONS` preventing arbitrary route execution.

---

## 3. Key Findings & Areas for Universal India Architecture

1. **Separation of LanguageProfile vs VoiceCapabilityProfile**: Currently, language metadata and provider capabilities are bundled in `languages.py`. We need explicit independent definitions:
   - `LanguageProfile`: Linguistic facts (name, script, parent language, family, regions, dialects).
   - `VoiceCapabilityProfile`: Exact verified system capabilities (local ASR/TTS, Bhashini ASR/TTS, streaming, offline status, fallback chain).
2. **Confidence Cascade**: Deepen the multi-tier confidence evaluation:
   - Local Fast-Path NLU $\to$ Multilingual/Cloud NLU $\to$ LLM Fallback $\to$ Clarification Question.
3. **Comprehensive India-Wide Catalog**: Expand catalog representation to all 22 Scheduled Languages and non-scheduled/tribal/rural varieties (Santali, Bodo, Dogri, Konkani, Kashmiri, Manipuri, Nepali, Gondi, Bhili, Tulu, Garhwali, Kumaoni, etc.) while explicitly marking capability tiers.
4. **Structured Canonical Semantic Schema**: Enforce a strict language-agnostic intent and entity representation across all tools.
