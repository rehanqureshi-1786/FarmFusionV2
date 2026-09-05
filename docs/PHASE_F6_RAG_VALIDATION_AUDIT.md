# Phase F6: Grounded RAG + Validation/Safety + LLM Response Synthesis — Technical Audit

**Date**: 2026-09-04  
**Auditor**: Antigravity AI Engineering  
**Scope**: Read-Only Architecture Audit of RAG Ingestion & Retrieval, Vector Store, LLM Providers, LangGraph Orchestration Nodes, Validation & Safety Gates, and Response Synthesis  
**Status**: Step 1 Complete (Read-Only Audit) — Awaiting User Review before Implementation  

---

## 1. Current RAG Runtime Path

### 1.1 Embedder Service (`app/rag/embedder.py`)
- **Implementation**: `RealAgriculturalEmbedder` (aliased as `BGEM3Embedder`).
- **Primary Model**: Configured via `settings.embedding_model_name` (defaults to `"sentence-transformers/all-MiniLM-L6-v2"` in active `.env`, or `"BAAI/bge-m3"`).
- **Vector Dimension**: Normalizes embeddings to a fixed 1024-dimensional vector (padded with zeros if using 384-dim MiniLM to maintain compatibility with pgvector's `Vector(1024)` column).
- **Execution**: Runs locally in-process with PyTorch and `SentenceTransformer.encode(normalize_embeddings=True)`.

### 1.2 Storage & Vector Search (`app/models/rag.py` & PostgreSQL)
- **Table**: `document_chunks` in PostgreSQL with `pgvector` extension.
- **Index**: HNSW index on `embedding` using cosine distance (`<=>`).
- **Active Data State**:
  - Total Chunks: **174 verified document chunks** currently indexed and active in PostgreSQL.
  - Document Types:
    - `disease_guide`: 49 pathology protocols from ICAR-NCIPM.
    - `regional_guide`: 89 agro-ecological regional suitability matrices.
    - `crop_guide`: 32 ICAR crop cultivation and agronomy packages of practice.
    - `scheme`: 4 national welfare schemes (PM-KISAN, PMFBY, KCC, Soil Health Card).

### 1.3 Knowledge Retriever (`app/rag/retriever.py`)
- **Class**: `KnowledgeRetriever`.
- **Search Method**: Cosine distance query via SQLAlchemy `DocumentChunk.embedding.cosine_distance(query_vector).label("distance")`.
- **Score Formulation**: `similarity = round(max(0.0, 1.0 - dist_val), 4)`.
- **Filtering**: Supports SQL-level `doc_type` filtering and in-memory `crop` filtering against `metadata_json`.

### 1.4 Current Access Points
- REST Endpoints: `/api/v1/knowledge/search` and `/api/v1/knowledge/context`.
- Tool Registry: Registered as `rag_knowledge_tool` in `app/tools/registry.py`.

---

## 2. Embedding & Retrieval Implementation Details

| Property | Current Status | Notes |
|---|---|---|
| **Model In-Memory** | `SentenceTransformer` | Lazy-loaded on first embedding call; cached on instance. |
| **Padded Geometry** | 384-dim ➔ 1024-dim | MiniLM embeddings are padded to 1024-dim to fit pgvector schema. |
| **Search Metric** | Cosine Distance | `DocumentChunk.embedding <=> query_vector`. |
| **Output Type** | Untyped `List[Dict[str, Any]]` | Returns dictionaries with keys `id, title, doc_type, content, source_url, similarity, distance, metadata`. |
| **Quality Gate** | **Missing** | Does not enforce a minimum similarity cutoff before passing chunks to callers. |
| **Reranker** | **Missing** | No secondary cross-encoder reranker currently active. |

---

## 3. Which Agents Currently Use RAG

1. **Disease Detection Agent / Workflow**:
   - In Phase F5, `planner.py` added a dynamic mapping `rag_1.static_inputs["query"] = "disease_1.disease_name"` when `CapabilityType.RAG_KNOWLEDGE` was requested alongside `DISEASE_DETECTION`.
   - However, RAG is not automatically triggered if the farmer's query didn't explicitly request treatment info.
2. **Disaster Risk Agent / Workflow**:
   - In Phase F5, `planner.py` added dynamic mapping `rag_1.static_inputs["query"] = "disaster_1.active_hazards"`.
3. **Crop Recommendation Agent**:
   - Currently runs pure XGBoost V2 inference. Does not automatically fetch ICAR agronomy packages of practices for the recommended top crop.
4. **Mandi Price & Forecasting Agent**:
   - Pure statistical Prophet + LightGBM timeseries forecasting. Does not consult RAG for MSP, market regulations, or post-harvest storage advisory.
5. **Government Schemes & Agricultural Knowledge**:
   - Explicitly mapped to `rag_knowledge_tool` / `government_scheme_tool`.

---

## 4. Current Synthesizer Implementation (`app/orchestrator/nodes/synthesizer.py`)

- **Lines of Code**: 544 lines.
- **Methodology**: **100% hardcoded `if-elif` string interpolation templates**.
- **Input Read**: Reads exclusively from `state.get("tool_output")` (a single legacy dictionary) and `state.get("intent")`.
- **Deficiencies**:
  - Does not inspect `state["tool_results"]` (where F5 stores multiple tool outputs from concurrent DAG stages).
  - Cannot synthesize cross-tool insights (e.g. combining Weather forecast + Mandi sell/hold recommendation + RAG crop storage guidance).
  - Incapable of fluid natural language explanation while preserving technical accuracy.
  - Generates plain string `state["final_response"]`; lacks structured citations, warnings, or provenance metadata.

---

## 5. Current LLM Provider & Configuration

- **Provider Abstraction**: [`app/core/llm/`](file:///home/rdj/FarmFusionFinal/backend/app/core/llm/) with `LLMProvider`, `GroqLLMProvider`, and `get_llm_provider()`.
- **Target Primary Models**:
  - Primary: `google/gemma-3-12b-it` (via OpenRouter).
  - Fallback: `qwen/qwen-2.5-7b-instruct` (via OpenRouter).
  - Cloud Fast Provider: `llama-3.3-70b-versatile` (via Groq Cloud).
- **Current Runtime Status**:
  - In `app/orchestrator/semantic_extractor.py`, cloud LLM APIs are invoked when API keys are available, with an automatic, 100% verified deterministic agricultural fallback when keys are placeholders.
  - The response synthesizer does **not** call any LLM provider at all.

---

## 6. Current Validation & Safety Mechanisms

### What Exists Today (Phases F2–F5)
1. **Photo Gate**: Zero ML models executed if leaf image is missing for crop disease (`ActionType.NAVIGATE` to camera).
2. **Location Gate**: Physical farming advisory requests without coordinates/district trigger `ActionType.REQUEST_INPUT`.
3. **Intent Confidence Gate**: Clarification query triggered if intent confidence < 0.60.
4. **DAG Execution Safety**: Upstream blocking failures mark downstream dependents as `SKIPPED` without crashing.
5. **Model Invariance**: Disease, Crop, Mandi, and Disaster numbers originate strictly from specialist ML engines.

### What is Missing (Pre-Synthesis Validation)
1. **Post-Tool Validation Node**: No LangGraph node checks whether tool results are valid, non-contradictory, and complete before handing them to synthesis.
2. **Numerical Immutability Guard**: No mechanism compiles an immutable fact set of verified numerical values (prices, temperatures, rain mm, confidence scores) to prevent LLM numerical distortion.
3. **RAG Grounding Verification**: No validation confirms that retrieved RAG chunks actually match the query domain or meet quality thresholds.
4. **Cross-Tool Consistency Check**: No validator checks for contradictions between related tools (e.g., Weather predicting heavy rain while Smart Irrigation advises immediate watering).

---

## 7. Exact Gaps Identified

| ID | Architectural Gap | Description |
|---|---|---|
| **G1** | **No RAG Grounding Node in LangGraph** | `graph.py` transitions directly from `plan_executor` to `response_synthesizer`. RAG is treated purely as a tool inside the plan, rather than a dedicated grounding layer. |
| **G2** | **No Conditional RAG Decision Logic** | No deterministic rules determine when RAG should be automatically invoked post-tool execution (e.g. disease diagnosis requiring ICAR treatments). |
| **G3** | **No Retrieval Quality Gate** | If similarity score is weak (e.g. < 0.50), the system lacks a threshold cutoff to explicitly state lack of authoritative evidence. |
| **G4** | **No Validation/Safety Node** | LangGraph lacks a `validation_node` to verify tool outputs, units, timestamps, and model provenance. |
| **G5** | **No Numerical Fact Set Extraction** | LLM could potentially hallucinate or round numbers without a deterministic fact-checking guard. |
| **G6** | **Rigid Template Synthesizer** | Handcoded string templates in `synthesizer.py` fail on multi-tool DAG outputs. |
| **G7** | **No Structured Action/Response Envelope** | Output is a simple string instead of a typed response containing `response_text`, `action`, `citations`, `confidence`, and `warnings`. |
| **G8** | **No Hallucination Re-check Loop** | No post-synthesis verification detects hallucinated numbers or altered crop names with a retry loop. |

---

## 8. Proposed Phase F6 Architecture & Implementation Plan

### 8.1 Updated LangGraph Pipeline
```
[START]
   ↓
intent_classification
   ↓
planner
   ↓
plan_executor
   ↓
[route_after_executor] ──(RAG not needed)─────────────┐
   ↓ (RAG required)                                   │
rag_grounding (Automatic query construction & gating) │
   ↓                                                  │
validation (Numerical immutability & cross-tool check) ◄┘
   ↓
response_synthesis (Grounded LLM synthesis + fact verification)
   ↓
[END]
```

### 8.2 Deliverable Components to Build in Subsequent F6 Steps
1. **`app/schemas/rag.py` & `app/schemas/validation.py`**: Strongly typed models for RAG chunks, quality gates, verified facts, and validation results.
2. **`app/orchestrator/nodes/rag_grounding.py`**: Automatic RAG query formulation from verified tool outputs (e.g. `Tomato Early Blight` ➔ ICAR treatment search), similarity score quality gating, and citation assembly.
3. **`app/orchestrator/nodes/validation.py`**: Validation node extracting verified numerical facts, validating units, checking cross-tool consistency, and evaluating confidence tiers.
4. **`app/orchestrator/nodes/synthesizer.py` (Overhaul)**: Grounded LLM response synthesis (Gemma 3 12B / Groq / deterministic fallback) that strictly respects the verified fact set and regional language directives.
5. **Numerical Immutability Validator**: Regex/token scanner ensuring all numbers in the synthesized text match the verified fact set.
6. **Typed Response Envelope**: Returning structured `ResponseEnvelope` with `response_text`, `action`, `citations`, `confidence`, and `warnings`.
7. **Comprehensive Tests (`tests/test_rag_grounding_validation.py`)**: Covering RAG gates, validation checks, numerical immutability, multilingual synthesis, and failure isolation.
