# FarmFusion — Architectural Specification & Ground Truth Document

## 1. System Overview
FarmFusion is a multilingual AI agricultural copilot for Indian farmers. It integrates voice interactions, crop disease detection, mandi price forecasting, crop recommendation, weather integration, and government scheme RAG into a unified assistant.

- **Backend**: Python (FastAPI), Async SQLAlchemy 2.x, PostgreSQL + pgvector, Alembic, Redis.
- **Frontend**: Native Android App in Kotlin.
- **Orchestrator**: LangGraph stateful orchestrator (`backend/app/orchestrator/`).

---

## 2. Architectural Classification

### Agents (1 total)
- **Main Multilingual Orchestrator** (`backend/app/orchestrator/`): The stateful, multi-step, goal-directed agent managing voice/text conversations, intent routing, state management, and fallback strategies.

### Tools (Single-call, deterministic async Python functions)
- `weather_tool`: Fetches live/forecast weather data from Open-Meteo API.
- `mandi_tool`: Fetches current prices and trends from Agmarknet / local mandi database.
- `navigation_tool`: Generates validated screen navigation commands for the Kotlin app.
- `rag_search_tool`: Performs similarity vector search over ingested PDF documents.
- `scheme_tool`: Queries government agricultural scheme eligibility guidelines.

### Workflows (Fixed-step ML + RAG + LLM pipelines)
- `disease_detection_workflow`: Image quality check → EfficientNet-B3 inference → confidence tier assignment → RAG retrieval → LLM explanation.
- `crop_recommendation_workflow`: Feature extraction → XGBoost/LightGBM model inference → RAG context enrichment → LLM synthesis.
- `crop_monitoring_workflow`: Periodic crop health analysis with episodic memory tracking.

---

## 3. Core Component Technology Matrix

| Component | Primary Tech | Fallback / Notes |
|---|---|---|
| **LLM Orchestration** | Gemma 3 12B (`google/gemma-3-12b-it`) via OpenRouter | Qwen2.5-7B-Instruct |
| **ASR (Speech-to-Text)** | Bhashini API (`bhashini.gov.in`) | IndicWhisper (AI4Bharat) |
| **TTS (Text-to-Speech)** | Bhashini API | AI4Bharat Indic-TTS |
| **Embeddings** | BGE-M3 (`BAAI/bge-m3`, 1024-dim) | pgvector HNSW index |
| **Disease Model** | Fine-tuned EfficientNet-B3 | PlantVillage + PlantDoc trained |
| **Crop Model** | XGBoost / LightGBM | Pure ML inference, no LLM guessing |
| **Price Forecasting** | Prophet + LightGBM Ensemble | Agmarknet historical dataset |
| **Database** | PostgreSQL async (SQLAlchemy 2.x) | Alembic migrations, pgvector |
| **Cache & Sessions** | Redis | Upstash / local Redis |
| **Observability** | Langfuse | Tracing intent & tool calls |

---

## 4. Multi-tier Language Policy

- **Tier 1 (Full Pipeline)**: Hindi (`hi`), English (`en`), Bengali (`bn`), Gujarati (`gu`), Marathi (`mr`), Punjabi (`pa`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Malayalam (`ml`).
- **Tier 2 (Partial Pipeline)**: Odia (`or`), Assamese (`as`), Maithili (`mai`), Santali (`sat`).
- **Tier 3 (Low-Resource)**: Mewari, Marwari, Bhojpuri, Awadhi, Haryanvi, Rajasthani varieties. (Log warning, default response handling).

---

## 5. Non-Negotiable Safety Policies

1. **Weather**: LLM never generates numbers. All weather numbers come from Open-Meteo API.
2. **Mandi Prices**: LLM never invents prices. All predictions come from Prophet + LightGBM models.
3. **Disease Diagnosis**: Must always output a `confidence_tier` (`high` >= 0.75, `medium` 0.45-0.74, `low` 0.30-0.44, `unclear` < 0.30).
4. **Schemes**: Eligibility criteria derived exclusively from DB/RAG documents.
5. **Kotlin Nav**: Navigation strings validated against `ALLOWED_DESTINATIONS` set.
