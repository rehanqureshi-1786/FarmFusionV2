# FarmFusion Voice Agent Capability Map

This document establishes the comprehensive, verified capability map of all farmer-facing services, ML pipelines, and tools in FarmFusion.

---

## 1. Test Baseline (Stage 0 Verification)

- **Execution Command**: `backend/venv/bin/pytest backend/tests/ -v`
- **Python Version**: `Python 3.13.12`
- **Virtualenv Path**: `/home/rdj/FarmFusionFinal/backend/venv`
- **Test Suite Results**:
  - **Total Tests**: `64`
  - **Passed**: `64`
  - **Failed**: `0`
  - **Skipped**: `0`
  - **Status**: **100% HEALTHY BASELINE**

---

## 2. Comprehensive Capability Matrix

| Capability Name | Service / Module | Primary Function / Endpoint | Required Inputs | Optional Inputs | Output Structure | Deterministic? | Voice Invocable? | Informational vs Consequential | Confirmation Required? | Multilingual Today? | Data Provenance | Offline Capability | Failure Behavior | Integration Gaps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Weather & Rainfall** | `backend/app/services/weather_service.py`, `app/tools/weather_tool.py` | `WeatherService.get_current_weather`, `get_annual_rainfall`, `weather_tool` | `latitude`, `longitude` | `location_name` | `{temperature_c, humidity_percent, condition, annual_rainfall_mm}` | **Yes** (API) | **Yes** | Informational | None | Yes (synthesized) | Open-Meteo API + ERA5-Land Reanalysis | No (Live API) | Fallback cached weather or explicit UNAVAILABLE | Contextual extraction of village/district names from voice query |
| **Crop Recommendation (Mode A - Real Soil Report)** | `backend/app/services/crop_agent_v2/local_engine.py`, `app/services/ml_service.py` | `LocalCropEngine.recommend`, `CropMLService.predict_candidates` | `N`, `P`, `K`, `ph`, `latitude`, `longitude` | `soil_type`, `season`, `farm_size_acres` | `{top_crops: [{crop_name, confidence, model_prob, suitability_score, rank}], explanation}` | **Yes** (ML + Composite Ranking) | **Yes** | Informational / Advisory | None | Yes (multilingual ranking & TTS) | V2 XGBoost (57 classes, 57k dataset) + SQLite Regional Matrix | **Yes** (Runs fully local offline) | Fallback to V1 Crop Model (22 classes) | Voice slot-filling for all 4 lab parameters (N, P, K, pH) |
| **Crop Recommendation (Mode B - No Soil Report)** | `backend/app/services/no_soil_crop_service.py`, `app/services/environmental_suitability_service.py` | `NoSoilCropService.recommend`, `EnvironmentalSuitabilityService.evaluate` | `latitude`, `longitude` | `farmer_selected_soil_type`, `season`, `state`, `location_name` | `{recommendations: [{crop_name, suitability_level, suitability_score, factors, notes}], soil_parameters: {ph, N, P, K}}` | **Yes** (ICAR/FAO Agronomic Rules) | **Yes** | Informational / Advisory | None | Yes | ICAR/FAO agronomic rules + Open-Meteo + SoilGrids estimated pH (N/P/K strictly UNAVAILABLE) | Partial (Rules are offline; Weather is online) | Graceful degradation without pH or rainfall | Clear voice communication that N/P/K are unknown without lab test |
| **Crop Disease Diagnosis (Image)** | `backend/app/workflows/disease_workflow.py`, `app/services/disease_ml_service.py` | `run_disease_detection_workflow`, `DiseaseMLService.predict` | `image_bytes` | `crop_name`, `language` | `{disease_name, confidence, confidence_tier, symptoms, treatment_steps}` | **Yes** (Vision ML + Knowledge Base) | **No** (Image required) | Consequential / Advisory | None | Yes (multilingual advice) | EfficientNet-B3 (38 classes) + `disease_knowledge_base.json` | **Yes** (Local PyTorch weights) | Fallback to Unknown Disease advisory | Voice assistant must guide farmer to take/upload a leaf photo via app UI |
| **Crop Disease Knowledge (Text/Voice)** | `backend/app/services/disease_knowledge_service.py` | `DiseaseKnowledgeService.get_disease_info` | `crop_name` or `disease_name` | `language` | `{disease_id, disease_name, hindi_name, symptoms, organic_treatment, chemical_treatment, prevention}` | **Yes** (Structured JSON lookup) | **Yes** | Informational | None | Yes (Hindi + English) | `backend/app/data/disease_knowledge_base.json` | **Yes** (Offline JSON) | Return generic crop care advisory | Fuzzy crop/disease name matching in regional languages |
| **Mandi Market Prices & Forecasts** | `backend/app/workflows/market_forecasting.py`, `app/services/market_service.py` | `MarketService.get_mandi_prices`, `run_mandi_forecasting_pipeline` | `commodity` | `mandi`, `state`, `days` | `{commodity, mandi, current_price, modal_price, daily_forecasts: [{date, predicted_price, trend}]}` | **Yes** (Prophet + LightGBM) | **Yes** | Informational | None | Yes | Government Mandi APIs + ML Forecast Models | Partial (Offline ML model) | Return static historical modal prices | Voice entity extractor mapping colloquial crop names to mandi standards |
| **Government Schemes (RAG)** | `backend/app/rag/retriever.py`, `app/data/agriculture/farmfusion_agriculture.db` | `search_schemes`, `agriculture_repo.get_schemes_for_crop` | `query` or `crop_name` | `state`, `farmer_category` | `{schemes: [{scheme_name, benefit, eligibility, application_process, official_link}]}` | **Yes** (RAG / DB Query) | **Yes** | Informational | None | Yes | Government Portals + Vector DB + SQLite KB | **Yes** (SQLite KB offline) | Fallback to national flagship schemes (PM-Kisan, PMFBY) | Scheme eligibility filtering based on farmer profile state/land |
| **Soil & Topsoil Grids** | `backend/app/services/soil_service.py` | `SoilService.get_soil_nutrients` | `latitude`, `longitude` | None | `{ph, sand, clay, silt, texture_class, depth: "0-5cm", npk_available: false}` | **Yes** (ISRIC SoilGrids API) | **Yes** | Informational | None | Yes | ISRIC SoilGrids v2.0 REST API (N/P/K explicitly marked UNAVAILABLE) | No (Online API) | Return `soil_data_available: false` gracefully | Voice synthesizer explaining pH estimate vs lab soil test requirement |
| **Crop Care & Agronomic Advice** | `backend/app/data/agriculture/seed_agriculture_db.py`, `app/services/lifecycle_service.py` | `agriculture_repo.get_crop_details`, `LifecycleService` | `crop_name` | `stage`, `season` | `{crop_name, water_requirement, fertilizer_schedule, pest_management, harvesting_tip}` | **Yes** (Database Query) | **Yes** | Informational | None | Yes | ICAR Handbook of Agriculture + SQLite KB | **Yes** (Offline SQLite DB) | Fallback to standard crop profile | Map voice question to specific crop stage (sowing, vegetative, harvest) |
| **Farmer Profile & Context** | `backend/app/services/user_service.py` | `UserService.get_farmer_profile` | `user_id` or session | None | `{farmer_name, state, district, primary_crops, soil_type, land_size_acres}` | **Yes** (Database Query) | **Yes** (Context provider) | Informational | None | Yes | PostgreSQL / SQLite User Store | **Yes** | Fallback to session/prompt context | Auto-inject profile context into active voice session |
| **In-App Screen Navigation** | `backend/app/api/v1/voice.py`, Kotlin `ALLOWED_DESTINATIONS` | `VoiceService.handle_navigation` | `destination` | None | `{navigation_action: "navigate", target_screen: "crop_recommendation"}` | **Yes** (Deterministic enum) | **Yes** | Consequential (UI navigation) | Yes (Validated against Kotlin whitelist) | Yes | Hardcoded Kotlin Navigation Router | **Yes** | Reject unknown screen navigation safely | Maintain strict whitelist compliance with Android app |
| **Automated Purchasing / Payment** | **UNAVAILABLE** | None | N/A | N/A | N/A | N/A | **No** | Consequential (Financial) | Mandatory | N/A | N/A | N/A | Agent must state: *"FarmFusion does not process payments or purchases directly; please visit your nearest agri-store."* | Capability does not exist in backend |
| **Autonomous Scheme Application Submission** | **UNAVAILABLE** | None | N/A | N/A | N/A | N/A | **No** | Consequential (Govt Form Submission) | Mandatory | N/A | N/A | N/A | Agent must state: *"I can provide eligibility criteria and links, but applications must be submitted on the official government portal."* | Capability does not exist in backend |
| **Automated Farmer-to-Farmer Messaging** | **UNAVAILABLE** | None | N/A | N/A | N/A | N/A | **No** | Consequential | Mandatory | N/A | N/A | N/A | Agent must clarify messaging is not supported | Capability does not exist in backend |
| **Scheduled Reminders / Push Daemon** | **UNAVAILABLE** | None | N/A | N/A | N/A | N/A | **No** | Consequential | Mandatory | N/A | N/A | N/A | Agent must state reminders/alarms cannot be scheduled via voice | No standing background scheduler/celery daemon |

---

## 3. Language & Dialect Support Verification

| Tier | Language / Dialect | Code | ASR Support | TTS Support | NLU / Intent Support | Provenance / Provider |
|---|---|---|---|---|---|---|
| **Tier 1 (Full Pipeline)** | Hindi | `hi` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | English (Indian) | `en` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Marathi | `mr` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Gujarati | `gu` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Punjabi | `pa` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Bengali | `bn` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Telugu | `te` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Tamil | `ta` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Kannada | `kn` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Malayalam | `ml` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Odia | `or` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 1 (Full Pipeline)** | Assamese | `as` | **Yes** | **Yes** | **Yes** | Bhashini API / AI4Bharat |
| **Tier 2 (Dialect / Approximation)** | Mewari / Marwari (Rajasthani) | `hi-rajasthani` | **Yes (via Hindi ASR approximation)** | **Yes (Hindi TTS with regional vocabulary)** | **Yes (Groq NLU)** | Mapped to Hindi pipeline per `.agents/AGENTS.md` Tier 3 rule |
| **Tier 2 (Dialect / Approximation)** | Bhojpuri / Awadhi / Maithili | `hi-bhojpuri` | **Yes (via Hindi ASR approximation)** | **Yes (Hindi TTS)** | **Yes (Groq NLU)** | Mapped to Hindi pipeline per `.agents/AGENTS.md` Tier 3 rule |

---

## 4. Key Architectural Decisions for Voice Agent Upgrade

1. **Deterministic Agent Core**:
   - The agent controller is pure Python deterministic code in `backend/app/orchestrator/`.
   - LLM (Gemma 3 12B / Groq) is used strictly for intent classification, slot extraction, disambiguation, and dialect-tailored synthesis.
   - LLM is NEVER used to compute or fabricate weather, mandi prices, crop rankings, or disease diagnoses.

2. **Tool Registry Pattern**:
   - All capabilities above are wrapped in typed `ToolDefinition` contracts in `backend/app/tools/registry.py`.
   - Every tool execution returns: `{status, data, provenance: {source, timestamp, confidence, estimated_vs_measured}}`.

3. **Multi-Turn Session State**:
   - Maintains active intent, filled slots, missing slots, last recommendations, and context (location, soil, crops).
   - Supports contextual follow-ups ("पहली वाली क्यों?", "अगर बारिश कम हो?", "आज इसका मंडी भाव?").
