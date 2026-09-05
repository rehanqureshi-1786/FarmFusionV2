# Phase F4: Tool Contracts & Capability Normalization

## 1. Executive Summary & Boundaries

Phase F4 standardizes the typed contract boundary between the Phase F3 `SemanticFrame` and FarmFusion's specialist execution tools.

```
SemanticFrame
    ↓
required_capabilities: List[CapabilityType]
    ↓
Capability Registry (contracts.py)
    ↓
Deterministic Tool Mapping (map_capabilities_to_tools)
    ↓
Strict Pydantic Input Validation (WeatherInput, SmartIrrigationInput, etc.)
    ↓
Executable Specialist Tools (tool_registry.execute)
    ↓
Canonical ToolResult Envelope (Status, Data, Provenance, Message)
```

> [!IMPORTANT]
> Phase F4 strictly normalizes and standardizes tool interfaces and contracts. It **does NOT** implement autonomous multi-step planning, dependency resolution DAGs, or parallel execution. Multi-tool scheduling and execution begins in **Phase F5 (Task Planner)**.

---

## 2. Canonical Capability Vocabulary

The unified vocabulary is defined in `CapabilityType` ([`app.schemas.semantic_frame`](file:///home/rdj/FarmFusionFinal/backend/app/schemas/semantic_frame.py)) and re-exported in [`app.tools.contracts`](file:///home/rdj/FarmFusionFinal/backend/app/tools/contracts.py):

| Canonical Capability | Tool Name | Specialist Engine / Backend Service |
|---|---|---|
| `WEATHER` | `weather_tool` | Open-Meteo Physical NWP API |
| `SMART_IRRIGATION` | `smart_irrigation_tool` | Open-Meteo Root-Zone Moisture + Agronomic Rules |
| `DISASTER_RISK` | `disaster_risk_tool` | DisasterPredictorAI 4-Model Ensemble |
| `CROP_RECOMMENDATION` | `crop_recommendation_tool` | XGBoost V2 / ICAR Agronomic Rules |
| `DISEASE_DETECTION` | `disease_detection_tool` | EfficientNet-B3 38-Class + Photo Gatekeeper |
| `CURRENT_PRICE` / `MANDI_CURRENT_PRICE` | `mandi_current_price_tool` | Agmarknet Longitudinal Mandi Records |
| `MANDI_HISTORY` | `mandi_history_tool` | Agmarknet Price Trend Engine |
| `MANDI_FORECAST` | `mandi_forecast_tool` | Prophet + LightGBM Ensemble Forecaster |
| `MANDI_COMPARISON` | `mandi_comparison_tool` | Agmarknet Market Differential Engine |
| `MANDI_DECISION` | `mandi_decision_tool` | Deterministic Sell-vs-Hold Engine |
| `RAG_KNOWLEDGE` | `rag_knowledge_tool` | pgvector HNSW Index + BGE-M3 Embeddings |
| `GOVERNMENT_SCHEME` | `government_scheme_tool` | Verified Scheme Registry + Guidelines |
| `ANIMAL_DETECTION` / `ANIMAL_ALERT` | `animal_detection_tool` | ESP32 IoT Perimeter Hardware Telemetry |
| `NAVIGATION` | `navigation_tool` | Hardcoded Kotlin Android Navigation Whitelist |
| `CALLING` | `calling_tool` | KisanCallingService (Vobiz Telephony) |

---

## 3. Tool Mapping Contract (`map_capabilities_to_tools`)

Deterministic mapping from `SemanticFrame.required_capabilities` to registered tool names:

```python
map_capabilities_to_tools(["WEATHER", "SMART_IRRIGATION"])
# => ["weather_tool", "smart_irrigation_tool"]

map_capabilities_to_tools(["DISEASE_DETECTION", "RAG_KNOWLEDGE"])
# => ["disease_detection_tool", "rag_knowledge_tool"]

map_capabilities_to_tools(["CURRENT_PRICE", "MANDI_COMPARISON", "MANDI_FORECAST", "MANDI_DECISION"])
# => ["mandi_current_price_tool", "mandi_comparison_tool", "mandi_forecast_tool", "mandi_decision_tool"]
```

---

## 4. Standard Tool Envelope: `ToolResult` & `ProvenanceMetadata`

Every tool execution emits a structured Pydantic `ToolResult`:

```json
{
  "status": "success",
  "capability": "MANDI_FORECAST",
  "tool_name": "mandi_forecast_tool",
  "data": { ... },
  "confidence": 0.92,
  "provenance": {
    "source": "Agmarknet Historical Data + Prophet/LightGBM Forecaster",
    "timestamp": "2026-09-04T16:53:26.545579+00:00",
    "model": "Prophet + LightGBM Ensemble",
    "model_version": "v2.0",
    "confidence": 0.92,
    "estimated": true,
    "estimated_vs_measured": "estimated",
    "location": "Jaipur Mandi"
  },
  "message": "7-day price forecast for Wheat in Jaipur Mandi: trend is UPWARD.",
  "warnings": [],
  "localized_message": {
    "hi": "गेहूं के भाव में अगले 7 दिनों में बढ़त का अनुमान है।",
    "en": "7-day price forecast for Wheat in Jaipur Mandi: trend is UPWARD."
  }
}
```

### Supported Status Codes (`ToolStatus`)
- `SUCCESS`: Tool completed successfully with authentic data.
- `INVALID_INPUT`: Inputs failed schema validation or range limits.
- `MISSING_INPUT`: Required slot was missing from input payload.
- `REQUIRES_PHOTO`: Sensory photo input required (triggers navigation to camera scan).
- `INSUFFICIENT_DATA`: Mandatory historical records or sensor observations missing.
- `UNAVAILABLE`: Service or backend dependency temporarily unreachable.
- `TIMEOUT`: Execution exceeded timeout threshold.
- `SAFETY_BLOCKED`: Action blocked by safety gating rules.
- `NETWORK_ERROR`: Physical network or HTTP connection failure.
- `NOT_FOUND`: Target entity (mandi, crop, scheme) not found.
- `UNSUPPORTED_CAPABILITY`: Action intentionally not automated (direct purchase, official form filing).
- `ERROR`: Unhandled internal exception.

---

## 5. Specialist Tool Contracts

### 5.1 Smart Irrigation Tool (`smart_irrigation_tool`)
- **Capability**: `SMART_IRRIGATION`
- **Underlying Logic**: Reuses `WeatherService` and Open-Meteo physical volumetric root-zone moisture (0-1cm, 3-9cm, 9-27cm) with deterministic agronomic rules.
- **Input Contract**: `SmartIrrigationInput` (`latitude: float`, `longitude: float`, `crop: Optional[str]`, `language: str = "hi"`)
- **Output Contract**: `SmartIrrigationOutput` (`status`, `irrigation_need_score`, `action`, `advice`, `next_irrigation_window`, `root_zone_moisture_percent`, `watering_hours_recommended`)

### 5.2 Disease Detection Tool (`disease_detection_tool`)
- **Capability**: `DISEASE_DETECTION`
- **Underlying Logic**: `EfficientNet-B3` 38-class leaf disease classifier.
- **Photo Gate Enforcement**:
  - If `image_bytes` or `image_path` is present: executes inference, verifies plant via `PlantGatekeeperService`, applies safety confidence tiers (`high`, `medium`, `low`, `unclear`).
  - If image is missing: **Never guesses disease**. Returns `ToolStatus.REQUIRES_PHOTO` with typed action:
    ```json
    {
      "action": "NAVIGATE",
      "destination": "DISEASE_SCAN",
      "android_route": "crop_disease",
      "required_input": "LEAF_IMAGE"
    }
    ```

### 5.3 Calling Tool (`calling_tool`)
- **Capability**: `CALLING`
- **Underlying Logic**: Delegates to `KisanCallingService` via official Vobiz API (`app/calling_agent/service.py`).
- **Input Contract**: `CallingInput` (`phone: str`, `farmer_name: str`, `call_type: str`, `crop_name: Optional[str]`, `mandi_name: Optional[str]`, etc.)
- **Validation**: Strict E.164 phone formatting (`+91XXXXXXXXXX`), 5-minute spam cooldown check.

### 5.4 Navigation Tool (`navigation_tool`)
- **Capability**: `NAVIGATION`
- **Strict Whitelist**:
  - `DISEASE_SCAN` → `crop_disease`
  - `MANDI` → `mandi_rates`
  - `WEATHER` → `weather_detail`
  - `CROP_RECOMMENDATION` → `crop_recommendation`
  - `FINANCIAL_SERVICES` → `financial_schemes`
  - `DASHBOARD` → `dashboard`
- **Output Contract**: `NavigationOutput` (`action: "NAVIGATE"`, `destination`, `android_route`, `required_input`, `message`). Arbitrary route strings from LLM are strictly rejected with `INVALID_INPUT`.

### 5.5 Mandi Suite Tools
- `mandi_current_price_tool`: Agmarknet modal, min, and max price for crop/market.
- `mandi_history_tool`: Longitudinal records and computed price trend over 1-365 days.
- `mandi_forecast_tool`: Prophet + LightGBM ensemble forecast with confidence scores.
- `mandi_comparison_tool`: Exact price spread, difference, and higher-yielding market between two mandis.
- `mandi_decision_tool`: Sell-now vs hold decision with projected percentage return.
