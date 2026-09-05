# Phase F6: Conditional RAG Grounding & Calibrated Quality Gating

## Executive Summary

Phase F6 introduces **Conditional RAG Grounding** into the central LangGraph orchestrator (`app/orchestrator/nodes/rag_grounding.py`). RAG is never used to compute or alter numerical agricultural truth (weather observations, crop probabilities, disease confidence scores, mandi price forecasts, or disaster risk metrics). Instead, it injects **authoritative agronomic package of practices**, ICAR crop cultivation guides, plant disease treatment protocols, and government scheme eligibility details into the synthesizer context.

---

## 1. Runtime Embedding & Vector Database Verification

Before activating production retrieval thresholds, the runtime embedding layer and vector store were verified against live PostgreSQL:

| Property | Active Runtime Specification |
| :--- | :--- |
| **Model Name** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Embedding Dimension** | 384 dimensions (padded with zeroes to 1024 dimensions) |
| **Loaded Model Class** | `sentence_transformers.SentenceTransformer` |
| **Vector DB Storage** | PostgreSQL 16 + `pgvector` with HNSW cosine index (`vector_cosine_ops`) |
| **Stored Chunks Compatibility** | 174 verified document chunks indexed (49 disease, 89 regional agro-climatic, 32 crop, 4 government scheme) |
| **Vector Parity** | 100% compatibility between query embedding generation and stored chunk vectors |

---

## 2. Calibrated Empirical Quality Gating

Blindly hardcoding an arbitrary threshold (such as `0.50` or `0.70`) results in either false rejections or hallucinated grounding. A 15-query empirical benchmark was run across all domains (`scratch/calibrate_rag_similarity.py`):

| Domain / Query Type | Representative Query | Empirical Similarity Range | Assigned Quality Tier |
| :--- | :--- | :--- | :--- |
| **Plant Pathology** | Tomato Early Blight treatment control | `0.5871 – 0.6360` | `HIGH_EVIDENCE` |
| **Crop Agronomy** | Wheat cultivation package of practices | `0.5757 – 0.6067` | `HIGH_EVIDENCE` |
| **Government Schemes** | PM Kisan eligibility criteria | `0.6196 – 0.6911` | `HIGH_EVIDENCE` |
| **Disaster Mitigation** | Flood risk drainage precautions | `0.4574 – 0.4829` | `HIGH_EVIDENCE` |
| **Low-Resource / Broad** | Neem oil spray concentration | `0.3200 – 0.4490` | `LOW_EVIDENCE` |
| **Out-of-Domain / Unsupported** | Cricket score / stock trading | `0.0850 – 0.2265` | `NO_EVIDENCE` |

### Established Production Thresholds:
- **`HIGH_EVIDENCE` (Similarity >= 0.45)**: Authoritative ICAR / ministerial guidelines confirmed. Direct grounding enabled.
- **`LOW_EVIDENCE` (0.30 <= Similarity < 0.45)**: Partial relevance. Synthesizer instructed to maintain cautious uncertainty.
- **`NO_EVIDENCE` (Similarity < 0.30)**: Grounding suppressed. The synthesizer will not claim authoritative backing.

---

## 3. Conditional Activation Rules

RAG grounding is evaluated deterministically in `should_trigger_rag_grounding`:

1. **Automatic Trigger**:
   - `DISEASE_DETECTION`: Always ground with biological, cultural, and chemical management protocols if disease is identified.
   - `CROP_RECOMMENDATION`: Ground with ICAR cultivation guidelines and optimal agronomy for the top recommended crop.
   - `DISASTER_RISK`: Ground with NDMA / ICAR preparedness, field drainage, and crop protection measures.
   - `GOVERNMENT_SCHEME`: Ground with official portal eligibility, documentation, and benefit structures.
   - `AGRICULTURAL_KNOWLEDGE`: Direct semantic search on farming practices.
2. **Deterministic Bypass**:
   - Pure UI Navigation (`NAVIGATE`)
   - Direct Clarification Questions (`CLARIFY`)
   - Missing Prerequisite Requests (`REQUEST_INPUT`)

---

## 4. Authoritative Query Formulation

RAG queries are derived **strictly from confirmed specialist tool results** (`construct_verified_rag_query`), never from speculative LLM text:

- *Tool Result*: `{"disease_name": "Tomato Early Blight", "crop": "Tomato"}`
  *Formulated Query*: `"Tomato Tomato Early Blight treatment management control measures"`
  *Filter*: `doc_type="disease_guide"`, `crop="tomato"`
- *Tool Result*: `{"top_crop": "Pearl Millet (Bajra)"}`
  *Formulated Query*: `"Pearl Millet (Bajra) cultivation agronomy package of practices optimal temperature soil"`
  *Filter*: `doc_type="crop_guide"`, `crop="pearl millet (bajra)"`

---

## 5. Attributable Chunk Citations

Every retrieved chunk is converted into an immutable `RAGCitation` (`app/schemas/rag.py`):
```json
{
  "chunk_id": 42,
  "title": "Tomato - Early Blight Identification and Treatment Guide",
  "source_url": "https://icar.org.in/plant-protection-guidelines",
  "organization": "ICAR-NCIPM",
  "doc_type": "disease_guide",
  "similarity_score": 0.636
}
```
No fabricated titles, organizations, or reference URLs are permitted.
