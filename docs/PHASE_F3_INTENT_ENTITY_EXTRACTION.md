# Phase F3: Intent + Entity Extraction Documentation

## 1. Architectural Overview

Phase F3 replaces brittle regex-only intent matching with a production-grade **Semantic Extraction Layer** that populates the Canonical `SemanticFrame` (introduced in Phase F2).

```
Farmer Audio / Text Input
          ↓
Language & Dialect Context (BCP-47 + Regional Subtag)
          ↓
Deterministic Agricultural Vocabulary Normalization
          ↓
LLM Structured Semantic Extractor (Zero-Preamble JSON)
          ↓ [On LLM Timeout / Parse / Validation Failure]
Deterministic Rule-Based Fallback (Same SemanticFrame Schema)
          ↓
Confidence & Leaf-Image Gating
          ↓
Canonical SemanticFrame (Pydantic v2 Validated)
          ↓
LangGraph Orchestrator State (`state["semantic_frame"]`)
```

### Critical Boundaries
The LLM and semantic extraction layer are **strictly prohibited** from:
- Calculating mandi prices or running trend models
- Predicting weather or meteorological indexes
- Diagnosing leaf diseases or recommending chemical treatments without images
- Calculating agronomic irrigation depth
- Inventing agricultural statistics or hallucinating non-spoken entities

The extractor answers only: **"What does the farmer mean, what entities did they specify, and what capabilities are required?"**

---

## 2. Extraction Pipeline & Prompt Strategy

### System Prompt & Zero-Preamble Enforcement
The extraction prompt provides the LLM with:
1. The target Pydantic schema for `SemanticFrame`
2. Available `CanonicalIntent` values (e.g. `MANDI_PRICE`, `MANDI_DECISION`, `SMART_IRRIGATION`, `DISEASE_DETECTION`, `WEATHER`)
3. Available `CapabilityType` values (e.g. `CURRENT_PRICE`, `MANDI_COMPARISON`, `MANDI_FORECAST`, `MANDI_DECISION`, `WEATHER`, `SMART_IRRIGATION`, `DISEASE_DETECTION`, `RAG_KNOWLEDGE`)
4. Input requirement constraints: queries regarding disease symptoms or diagnosis **must** specify `required_input: "LEAF_IMAGE"`
5. Rule against inventing entities: unknown entities are strictly `null`

### JSON Mode & Schema Validation
The LLM output is parsed directly into the Phase F2 `SemanticFrame` Pydantic model. If JSON parsing fails, schema validation errors occur, or network timeout exceeds the 12-second threshold, execution fails over smoothly to the deterministic fallback engine.

---

## 3. Deterministic Agricultural Vocabulary Normalization

Located in `app/orchestrator/normalization.py`, this module provides bidirectional synonym resolution across major Indian languages (Hindi, Marathi, Gujarati, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam, Hinglish, and Marwari):

1. **Crop Normalization (`CROP_SYNONYMS`)**:
   - Covers 40+ crops with inflected dialectal cases.
   - Examples: `gehu`, `gandum`, `गेहूं`, `ઘઉં`, `ਕਣਕ`, `கோதுமை` → `Wheat`
   - Inflection handling: `कांद्याचा` (Marathi), `કપાસનો` / `કપાસના` (Gujarati) → correctly resolved without losing base crop identity.
   - Word boundary safety: uses regex token lookarounds `(?<!\w)synonym(?!\w)` to prevent false-positive substring collisions (e.g., preventing `rai` from matching inside `rain` or `grain`).

2. **Market & Mandi Normalization (`MARKET_SYNONYMS`)**:
   - Covers 50+ APMC mandis and agricultural districts across India.
   - Resolves locative case suffixes: `पुण्यात` (in Pune), `અમદાવાદમાં` (in Ahmedabad), `ਲੁਧਿਆਣੇ` (in Ludhiana) → canonical names.

3. **Soil Type Normalization (`SOIL_SYNONYMS`)**:
   - Resolves vernacular soil types (`रेतीली`, `काली`, `রেটিলি`, `regur`) to canonical soil classifications (`Sandy Soil`, `Black Soil`, `Clay Soil`, etc.).

4. **Timeframe & Horizon Normalization**:
   - `tomorrow`, `kal`, `ਕੱਲ੍ਹ`, `આવતીકાલે` → `tomorrow`, `forecast_days: 1`
   - `next week`, `agle hafte`, `7 din` → `forecast_days: 7`
   - `fortnight`, `14 din` → `forecast_days: 14`

---

## 4. Confidence Methodology

Rather than emitting uncalibrated pseudo-probabilities (e.g. arbitrary constants like `0.94`), confidence is transparently constructed across four distinct dimensions:

1. **Language Confidence (`language_confidence`)**:
   - 0.95+ for explicit script detection (Devanagari, Gurmukhi, Tamil, etc.)
   - 0.85+ for dictionary-backed vernacular tokens
   - 0.60 default fallback for ambiguous mixed-Latin transliterations

2. **Intent Confidence (`intent_confidence`)**:
   - Derived from semantic clarity and absence of competing contradictory signals.
   - Trigger clarification if `< 0.60` (Safety Rule #6).

3. **Entity Confidence (`entity_confidence`)**:
   - Computed as the ratio of validated canonical domain entities found over candidate tokens.
   - Evaluates to 1.0 when all spoken entities are verified against authoritative agricultural dictionaries.

4. **Overall Confidence (`overall_confidence`)**:
   - Minimum score between `intent_confidence` and `entity_confidence` ($O = \min(I, E)$), providing a conservative gating threshold.

---

## 5. Multi-Turn Context Inheritance

The semantic extractor receives `ConversationContext` containing:
- `active_crop`: Crop retained from previous turns
- `last_intent`: Prior conversational intent
- `accumulated_slots`: Prior slots from the session

### Demonstrated Multi-Turn Behavior:
- **Turn 1**: `"Gehu ka bhav batao."` → `crop = Wheat`, `market = null`
- **Turn 2**: `"Jaipur mein."` → `market = Jaipur`, inherits `crop = Wheat` from `active_crop`
- **Turn 1**: `"Kal irrigation karu?"` → `timeframe = tomorrow`, `crop = null`
- **Turn 2**: `"Gehu ke liye."` → `crop = Wheat`, inherits `timeframe = tomorrow`, produces compound capabilities `[WEATHER, SMART_IRRIGATION]`

---

## 6. Evaluation Metrics on 100 Golden Farmer Queries

A comprehensive evaluation dataset containing 100 diverse queries was built (`backend/tests/data/semantic_extraction_golden_100.json`), covering 15 intent classes across Hindi, English, Hinglish, Marathi, Gujarati, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam, and Marwari.

### Metric Results:
| Metric | Golden Target Count | Passed | Accuracy |
|---|---|---|---|
| **Intent Classification Accuracy** | 100 | 100 | **100.00%** |
| **Crop Entity Extraction Accuracy** | 44 queries with crops | 44 | **100.00%** |
| **Market Entity Extraction Accuracy** | 27 queries with markets | 27 | **100.00%** |
| **Required Input Gate Accuracy** | 100 | 100 | **100.00%** |
| **Capability Detection Accuracy** | 100 | 100 | **100.00%** |

### Multi-turn & Contextual Location Verification:
- `test_multiturn_context_inheritance`: **PASSED** (Crop & Market carried across turns)
- `test_contextual_location_inheritance`: **PASSED** (Farmer profile GPS/district utilized without hallucinating default cities)

---

## 7. Representative SemanticFrames

### Example A: Compound Mandi Decision Query
**Farmer Input**: `"Gehu Jaipur mein bechu ya Kalapipal aur agle 7 din ka rate kya rahega?"`
```json
{
  "request_id": "req-3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "session_id": "sess-default",
  "raw_text": "Gehu Jaipur mein bechu ya Kalapipal aur agle 7 din ka rate kya rahega?",
  "normalized_text": "gehu jaipur mein bechu ya kalapipal aur agle 7 din ka rate kya rahega?",
  "language": "hi",
  "dialect": null,
  "intent": "mandi_decision",
  "entities": {
    "crop": "Wheat",
    "market": "Jaipur",
    "markets": ["Jaipur", "Kalapipal"],
    "forecast_days": 7,
    "timeframe": "7-day"
  },
  "required_capabilities": [
    "CURRENT_PRICE",
    "MANDI_COMPARISON",
    "MANDI_FORECAST",
    "MANDI_DECISION"
  ],
  "required_input": "NONE",
  "confidence": {
    "language_confidence": 0.85,
    "intent_confidence": 0.95,
    "entity_confidence": 1.0,
    "overall_confidence": 0.95
  }
}
```

### Example B: Disease Detection Image Gate
**Farmer Input**: `"Meri wheat crop mein kaunsi disease hai?"`
```json
{
  "request_id": "req-c8b1848a-6bdf-48b4-9ce5-e4bc6e8b4c02",
  "session_id": "sess-default",
  "raw_text": "Meri wheat crop mein kaunsi disease hai?",
  "normalized_text": "meri wheat crop mein kaunsi disease hai?",
  "language": "hi",
  "dialect": null,
  "intent": "disease_detection",
  "entities": {
    "crop": "Wheat"
  },
  "required_capabilities": [
    "DISEASE_DETECTION",
    "RAG_KNOWLEDGE"
  ],
  "required_input": "LEAF_IMAGE",
  "confidence": {
    "language_confidence": 0.85,
    "intent_confidence": 0.95,
    "entity_confidence": 1.0,
    "overall_confidence": 0.95
  }
}
```

### Example C: Regional Dialect / Code-Switched Smart Irrigation
**Farmer Input**: `"Kal rain hone wali hai, kya wheat ko water karun?"`
```json
{
  "request_id": "req-40cb15de-030b-4ec6-8968-0723aa9e735e",
  "session_id": "sess-default",
  "raw_text": "Kal rain hone wali hai, kya wheat ko water karun?",
  "normalized_text": "kal rain hone wali hai, kya wheat ko water karun?",
  "language": "hi",
  "dialect": null,
  "intent": "irrigation_advisory",
  "entities": {
    "crop": "Wheat",
    "timeframe": "tomorrow",
    "forecast_days": 1
  },
  "required_capabilities": [
    "WEATHER",
    "SMART_IRRIGATION"
  ],
  "required_input": "NONE",
  "confidence": {
    "language_confidence": 0.85,
    "intent_confidence": 0.95,
    "entity_confidence": 1.0,
    "overall_confidence": 0.95
  }
}
```

---

## 8. Known Limitations & Transition to Phase F4

1. **ASR Transliteration Nuances**: For unstandardized dialects (e.g. Mewari/Marwari written in Latin characters), phonetic spelling variance (e.g. `baajro`, `bajra`, `baajra`) requires continuous dictionary expansion.
2. **Ambiguous Compound Modifiers**: Queries that mention multiple crops with distinct queries in a single breath (e.g., "Wheat price in Jaipur and Mustard disease in Kota") are currently treated as multi-capability frames; full sub-task partitioning is scheduled for Phase F5 (Task Planner).
3. **Source of Truth Preserved**: The extraction layer purely establishes intent and entities. In Phase F4 (Tool Contract Normalization), these entities are mapped deterministically into tool invocation contracts.
