# India-Wide Voice Implementation Audit

## 1. Executive Summary & Baseline Metrics

- **Workspace Root**: `/home/rdj/FarmFusionFinal`
- **Execution Environment**: Python 3.13.12 / venv (`backend/venv`)
- **Baseline Test Execution**: `backend/venv/bin/pytest backend/tests/ -v`
- **Baseline Test Status**: **109 / 109 PASSED (100%)**
- **Core Principle**: Agricultural intelligence is deterministic and language-independent. The voice layer is an honest interface preserving zero data fabrication and strict audio privacy.

---

## 2. Current Provider & Voice Architecture Audit

### 2.1 ASR (Speech-to-Text) Providers
- **Primary**: MeitY Bhashini API (`getModelsPipeline` at `https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline`).
- **Secondary / Fallback**: AI4Bharat IndicWhisper (self-hostable) / Local Fallback.
- **Provider Status**: In standard development/test environments where `BHASHINI_API_KEY` or `BHASHINI_USER_ID` are not populated in `.env`, the provider reports honest availability or falls back to local canonical text processing without fabricating audio bytes or fake live transcripts.

### 2.2 TTS (Text-to-Speech) Providers
- **Primary**: MeitY Bhashini TTS API.
- **Secondary / Fallback**: AI4Bharat Indic-TTS / On-Device Android TTS (`hi_IN`, `mr_IN`, `pa_IN`, `te_IN`, `en_IN`).
- **Caching**: Redis key caching pattern `tts:{language}:{text_hash}` with 24-hour TTL.

### 2.3 Translation & NLU Providers
- **Canonical Normalization**: FarmFusion Data-Driven Agricultural Vocabulary Normalizer (mapping surface dialect forms $\to$ canonical English entity IDs).
- **Orchestrator**: LangGraph stateful multi-turn graph (`intent_classification_node`, `tool_router_node`, `response_synthesizer_node`).

---

## 3. Language & Dialect Tier Classification

| Tier | Definition | Examples | Handling Strategy |
|---|---|---|---|
| **Tier 1** | Full Native Voice (ASR + NLU + Response + TTS in same language) | Hindi (`hi`), English (`en`), Marathi (`mr`), Gujarati (`gu`), Punjabi (`pa`), Bengali (`bn`), Telugu (`te`), Tamil (`ta`), Kannada (`kn`), Malayalam (`ml`), Odia (`or`), Assamese (`as`), Urdu (`ur`), Maithili (`mai`) | Native ASR $\to$ Canonical NLU $\to$ Tool Execution $\to$ Native TTS |
| **Tier 2** | Native Understanding + Parent Language Fallback | Mewari (`mew`), Marwari (`rwr`), Dhundhari (`dhu`), Harauti (`har`), Shekhawati (`swv`), Wagdi (`wbr`), Bhojpuri (`bho`), Awadhi (`awa`), Magahi (`mag`), Chhattisgarhi (`hne`), Bundeli (`bns`), Haryanvi (`bgc`), Braj (`bra`), Garhwali (`gbm`), Kumaoni (`kfy`), Malwai (`mup`), Doabi (`doa`), Varhadi (`vah`), Kathiawari (`kat`), Tulu (`tcy`), Kodava (`kfa`), Konkani (`kok`) | Dialect detection + Dialect vocabulary mapping $\to$ Parent ASR/Language $\to$ Tool Execution $\to$ Parent Language TTS |
| **Tier 3** | Vocabulary & Dialect Normalization Only | Colloquial crop/soil/fertilizer/mandi slang across all states | Data-driven dictionary normalization to canonical IDs |
| **Tier 4** | Unsupported by Provider Infrastructure | Extremely rare unmapped tribal languages without written/acoustic models | Honest admission via `unsupported_capability_tool` |

---

## 4. Current Tool-Calling Architecture

The multilingual orchestrator interfaces directly with `backend/app/tools/registry.py`:
1. `weather_tool`: Open-Meteo live API / verified local historical fallback.
2. `crop_recommendation_tool`: XGBoost V2 Mode A (measured soil report) & Mode B (SoilGrids estimated pH + suitability matrix with explicit $N/P/K$ unavailable status).
3. `disease_info_tool`: ICAR disease knowledge base & photo request redirect.
4. `market_price_tool`: Agmarknet modal prices & Prophet+LightGBM forecasting.
5. `government_scheme_tool`: Structured schemes DB & RAG.
6. `soil_info_tool`: SoilGrids estimated properties & ICAR soil classification.
7. `crop_care_tool`: Agronomic crop calendar & management guidelines.
8. `navigation_tool`: Whitelisted Android in-app destinations (`market_prices`, `weather`, `crop_recommendation`, `disease_detection`, `government_schemes`, `home`, `back`).
9. `speech_control`: Voice pacing adjustment (`slow`, `normal`, `fast`).
10. `repeat_last`: Playback of the most recent response.
11. `unsupported_capability_tool`: Honest rejection of purchasing, financial transactions, or automated scheme submissions.

---

## 5. Required File Enhancements

1. [`backend/app/voice/languages.py`](file:///home/rdj/FarmFusionFinal/backend/app/voice/languages.py): Expand 10-category agricultural vocabulary catalog, probabilistic dialect scoring, and 4-tier model.
2. [`backend/app/voice/providers.py`](file:///home/rdj/FarmFusionFinal/backend/app/voice/providers.py): Expand decoupled provider discovery (`supports_asr`, `supports_tts`, `supports_translation`, `supports_language_detection`) and execution trace model (`ExecutionTrace`).
3. [`backend/app/orchestrator/nodes/intent_classification.py`](file:///home/rdj/FarmFusionFinal/backend/app/orchestrator/nodes/intent_classification.py): Canonical semantic representation output.
4. [`backend/app/orchestrator/nodes/synthesizer.py`](file:///home/rdj/FarmFusionFinal/backend/app/orchestrator/nodes/synthesizer.py): Dynamic TTS fallback ladder metadata.
5. [`backend/tests/test_india_wide_voice_platform.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_india_wide_voice_platform.py): 37 comprehensive integration scenarios.
