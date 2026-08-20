# FarmFusion Workspace Rules

## Developer Identity & Global Constraints

- **Developer Profile**: B.Tech AI/ML student (3rd year) building FarmFusion — a multilingual AI agricultural copilot for Indian farmers. Working across Python (FastAPI backend) and Kotlin (Android frontend).
- **Frontend Framework**: Never suggest migrating the Kotlin Android frontend to any other framework.
- **Models & Tools**: Always prefer free, open-source, or self-hostable models and tools.
- **Backend Async**: Prefer async Python (asyncio, SQLAlchemy async, aiohttp) everywhere in the backend.
- **Validation**: All new FastAPI code must use Pydantic v2 for schemas.
- **Database**: Never use SQLite anywhere. The project uses PostgreSQL with pgvector.
- **Migrations**: Always use Alembic for database migrations. Never write raw ALTER TABLE statements.
- **Dependencies**: Do not add unnecessary dependencies. Justify every new package before installing it.
- **Simplicity**: When in doubt, write a plain Python function before reaching for a framework abstraction.
- **Data Integrity**: Never invent data. Weather comes from APIs. Prices come from ML models. Schemes come from RAG.

---

## FarmFusion Core Architecture Rules

### Project Layout

The backend lives in `backend/`. The Kotlin Android app lives in `frontend/app/`.
The full architecture reference document is `farmfusion-architecture.md` in the repo root. Read the relevant section of this document before making any structural or technology decision.

### Agent vs Tool vs Workflow — Critical Distinction

- The ONLY true LangGraph agent is the **Main Multilingual Orchestrator** in `backend/app/orchestrator/`. It is stateful, multi-step, and goal-directed.
- Everything else is a **tool** (single-call, deterministic function) or a **workflow** (fixed-step pipeline). Do NOT create new LangGraph graphs for sub-tasks unless explicitly asked.
- Weather = tool. Mandi price lookup = tool. Navigation = tool. RAG search = tool.
- Disease detection = workflow (fixed pipeline: image → ML → RAG → LLM).
- Crop recommendation = workflow (fixed pipeline: features → ML → RAG → LLM).
- Crop monitoring = lightweight workflow with episodic memory.

### Folder Structure to Follow

```
backend/
├── app/
│   ├── api/           ← FastAPI routers only, no business logic here
│   ├── core/          ← database.py, security.py, logging.py, exceptions.py
│   ├── models/        ← SQLAlchemy 2.x ORM models
│   ├── schemas/       ← Pydantic v2 request/response models
│   ├── orchestrator/  ← LangGraph graph, state, nodes, prompts
│   ├── tools/         ← Single-call tool functions
│   ├── workflows/     ← Fixed-step ML+RAG+LLM pipelines
│   ├── ml/            ← ML model inference (disease/, crop/, market/)
│   ├── rag/           ← Embedder, retriever, reranker, pipeline, ingestion
│   ├── voice/         ← ASR, TTS, language detection, VAD
│   └── services/      ← weather_service, mandi_service, notification_service
├── migrations/        ← Alembic migration files only
├── scripts/           ← One-off scripts: scraping, training, ingestion
└── tests/             ← pytest tests
```

### Technology Stack (Non-Negotiable)

| Component | Technology |
|---|---|
| LLM (primary) | Gemma 3 12B via OpenRouter (`google/gemma-3-12b-it`) |
| LLM (fallback) | Qwen2.5-7B-Instruct via OpenRouter |
| ASR (primary) | Bhashini API (`bhashini.gov.in`) |
| ASR (fallback) | IndicWhisper (AI4Bharat, self-hosted) |
| TTS (primary) | Bhashini API |
| TTS (fallback) | AI4Bharat Indic-TTS (self-hosted) |
| Embeddings | BGE-M3 (`BAAI/bge-m3`, 1024-dimensional) |
| Vector search | pgvector in PostgreSQL (HNSW index) |
| Disease model | EfficientNet-B3, fine-tuned on PlantVillage + PlantDoc |
| Crop recommendation | XGBoost or LightGBM — NOT an LLM |
| Price forecasting | Prophet + LightGBM ensemble — NOT an LLM |
| Agent framework | LangGraph (orchestrator only) |
| Database | PostgreSQL + SQLAlchemy 2.x async + Alembic |
| Cache / sessions | Redis (Upstash free tier for MVP) |
| Observability | Langfuse (free tier, open-source) |
| Auth | Firebase Auth (existing, keep) |

### Safety Rules — Never Violate These

1. The LLM must NEVER generate or estimate weather numbers. It only formats data returned by the Open-Meteo API into natural language.
2. The LLM must NEVER predict mandi prices. Only the Prophet+LightGBM ML model produces price forecasts. The LLM only narrates the model's output.
3. Every disease diagnosis must include a `confidence_tier` field: `high` (>=0.75), `medium` (0.45-0.74), `low` (0.30-0.44), `unclear` (<0.30). The LLM response must communicate this tier to the farmer.
4. Government scheme eligibility must come from the structured DB + RAG only. The LLM must never add, invent, or extrapolate eligibility criteria.
5. Kotlin navigation actions must always be validated against the hardcoded `ALLOWED_DESTINATIONS` set in the Kotlin app before `navController.navigate()`.
6. If intent classification confidence < 0.6, the orchestrator must ask a clarifying question instead of routing to a tool.

### Voice and Privacy Rules

- Raw audio bytes are NEVER written to disk or stored in the database. Delete from memory immediately after transcription completes.
- Transcriptions are stored only if the farmer record has `consent_voice_storage = TRUE`.
- Language detection runs before or immediately after ASR; always stored in `OrchestratorState`.

### Code Style Rules

- All FastAPI endpoints must be `async def`.
- Use structlog for all logging. Never use `print()` in any backend file.
- Every new endpoint must have matching Pydantic v2 schemas in `app/schemas/`.
- Every database model is a SQLAlchemy 2.x mapped class in `app/models/`.
- Every tool function must have a docstring: purpose, inputs, outputs, side effects, errors.
- Write pytest tests for every new ML pipeline, tool, workflow, and API endpoint.
- Use `httpx.AsyncClient` + `pytest-asyncio` for API tests.

---

## FarmFusion Multilingual & Voice Rules

### Language Support Tiers

- **Tier 1 — Full pipeline (IndicWhisper + Bhashini TTS)**: Hindi, English, Bengali, Gujarati, Marathi, Punjabi, Tamil, Telugu, Kannada, Malayalam.
- **Tier 2 — Partial support (IndicWhisper with caveats, Whisper large-v3 fallback)**: Odia, Assamese, Maithili, Santali.
- **Tier 3 — Low-resource (Hindi ASR as approximation, log the limitation)**: Mewari, Marwari, Bhojpuri, Awadhi, Haryanvi, Rajasthani varieties.
  *Note*: Mewari is NOT Hindi. Do not treat them as equivalent. Log a warning whenever Tier 3 language handling is used.

### Code-Switching

- Do NOT split a code-switched utterance into separate language chunks.
- Pass the full mixed-language transcription to the LLM with this injected instruction: *"The farmer may mix Hindi and English or a regional language. Understand the full intent regardless of language mixing."*
- Respond in the farmer's dominant language. If unclear, default to Hindi.
- TTS always uses the dominant language's voice.

### OrchestratorState Language Fields

Every orchestrator state must carry:
- `detected_language: str` (BCP-47 code e.g. `"hi"`, `"en"`, `"gu"`)
- `detected_dialect: str | None` (e.g. `"mewari"`, `"marwari"`, `None`)
- `language_confidence: float` (0.0 to 1.0)

If `language_confidence < 0.6`, log a warning and default to Hindi for response. Do not ask the farmer to repeat themselves just for language identification.

### Bhashini API Integration

- Auth endpoint: `https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline`
- Always check the `detected_language` field in Bhashini ASR responses.
- Map detected language to Bhashini voice codes for TTS.
- Cache TTS audio for repeated short phrases (error messages, greetings) in Redis with key pattern: `tts:{language}:{hash_of_text}` (TTL: 24 hours).
- On Bhashini API failure, fall back to AI4Bharat Indic-TTS immediately. Log the failure with structlog. Do not surface the error to the farmer.

### LLM Prompting for Multilingual Responses

Always include in the LLM system prompt when generating farmer-facing responses:
> *"Respond in {detected_language}. Use simple vocabulary suitable for a rural Indian farmer with limited formal education. Avoid technical jargon. Keep voice responses to 2-3 sentences unless the farmer asked for detail."*

Never respond in English if the farmer spoke Hindi or another Indian language, unless the farmer explicitly requests English.

Adjust response length by farmer preference:
- `short`: 1-2 sentences
- `medium`: 2-3 sentences (default)
- `detailed`: up to 5 sentences with specific steps

### Voice Activity Detection (VAD)

- Use energy-threshold VAD for MVP; Silero VAD for V2.
- Minimum speech duration before sending to ASR: 0.5 seconds.
- Silence timeout to end utterance: 1.5 seconds.
- Maximum audio buffer before forced send: 30 seconds.
