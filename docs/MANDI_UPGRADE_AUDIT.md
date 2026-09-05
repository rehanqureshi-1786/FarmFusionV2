# Phase M — Mandi Market Intelligence Upgrade: Read-Only Audit & Migration Plan

> **Document:** `docs/MANDI_UPGRADE_AUDIT.md`  
> **Phase:** Phase 1 — Read-Only Audit  
> **Objective:** Comprehensive audit of the current Mandi Market Intelligence subsystem to prepare for replacing the synthetic 90-day time-series with authentic longitudinal Agmarknet data, establishing chronological model evaluation, and elevating the subsystem into a verified ML-Powered Mandi Agent.  
> **Status:** Phase 1 Complete (Read-Only). No code modified.  
> **Date:** September 4, 2026  

---

## 1. Current Architecture

The Mandi Market subsystem follows a structured, layered architecture spanning the Kotlin Android application, the FastAPI backend, mathematical services, ML forecasting, and the LangGraph Multilingual Supervisor.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          1. ANDROID CLIENT (KOTLIN)                         │
│  MandiPricesScreen.kt (Jetpack Compose)                                      │
│  ├── Current Prices LazyColumn & Category Filtering                         │
│  ├── Best Practical & Nearby Mandi Dialog                                   │
│  ├── Mandi Comparison Dialog                                                │
│  ├── Sell vs Wait Advisory Dialog                                           │
│  └── Set Price Alert Modal                                                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Retrofit HTTP / JSON (Port 8000)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       2. FASTAPI API ROUTING LAYER                          │
│  app/api/v1/market.py                                                       │
│  ├── GET  /prices              ──► MarketService.get_current_prices()       │
│  ├── GET  /best-nearby         ──► MandiIntelligenceService.get_best_nearby() │
│  ├── GET  /compare             ──► MandiIntelligenceService.compare_mandis()│
│  ├── GET  /advisory            ──► MandiIntelligenceService.get_advisory()  │
│  ├── GET  /forecast            ──► run_mandi_forecasting_pipeline()         │
│  ├── POST /alerts              ──► MandiIntelligenceService.create_alert()  │
│  └── GET  /commodities         ──► MarketService.get_all_commodities()      │
└──────────────────┬────────────────────────────────────────┬─────────────────┘
                   │                                        │
                   ▼                                        ▼
┌──────────────────────────────────────┐ ┌────────────────────────────────────┐
│   3. MANDI INTELLIGENCE SERVICE      │ │    4. ML FORECASTING WORKFLOW      │
│  app/services/mandi_intelligence.py  │ │  app/workflows/market_forecasting  │
│  ├── Geodesic Haversine Distance     │ │  └─► MandiPriceForecaster          │
│  ├── Practical Scoring Engine        │ │        (app/ml/market/forecaster)  │
│  ├── Mandi Difference & % Spread     │ │        ├── In-Memory 12h Cache     │
│  ├── Deterministic Advisory Matrix   │ │        ├── Synthetic Series Anchor │
│  └── Price Alert CRUD (PostgreSQL/DB)│ │        ├── Prophet (CmdStanPy)     │
└──────────────────────────────────────┘ │        ├── LightGBM Regressor      │
                                         │        └── 60/40 Ensemble Calc     │
                                         └────────────────────────────────────┘
                                                            ▲
┌───────────────────────────────────────────────────────────┴─────────────────┐
│               5. LANGGRAPH SUPERVISOR & VOICE ORCHESTRATION                 │
│  app/orchestrator/nodes/tool_router.py                                      │
│  ├── Maps "mandi"                 ──► market_price_tool                     │
│  ├── Maps "best_nearby_mandi"     ──► best_nearby_mandi_tool                │
│  ├── Maps "compare_mandi"         ──► mandi_comparison_tool                 │
│  └── Maps "sell_wait_advisory"    ──► mandi_advisory_tool                   │
│  app/orchestrator/nodes/synthesizer.py                                      │
│  └── LLM only narrates deterministic tool output (Safety Rule #2)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Current Data Source

### Dataset Metadata (`commodity_price.csv`)
* **Path:** `/home/rdj/FarmFusionFinal/commodity_price.csv`
* **File Size:** 188 KB (2,733 lines)
* **Header:** `State,District,Market,Commodity,Variety,Grade,Arrival_Date,Min_x0020_Price,Max_x0020_Price,Modal_x0020_Price`
* **Unique Commodities:** 145 (Top: Tomato 155, Onion 154, Potato 154, Brinjal 115, Bhindi 109, Green Chilli 103, Cucumbar 98, Banana 89, Bitter gourd 88)
* **Unique Mandis / APMCs:** 268 markets
* **Unique Districts:** 157 districts
* **Unique States:** 16 Indian states
* **Date Horizon:** **`19/05/2025`** (Single snapshot date).

### Ingestion Service (`app/services/market_service.py`)
* `MarketService.get_current_prices()` reads `commodity_price.csv` on-demand using standard Python `csv.DictReader`.
* Implements robust regional and multilingual aliases in `match_commodity_name()` covering 27 crops across Hindi, Gujarati, Marathi, Bengali, Telugu, and Punjabi.
* Includes a 10-crop fallback dictionary (`baseline_prices`) for Wheat, Mustard, Paddy, Soybean, Cotton, Onion, Potato, Tomato, Gram, and Maize when geographic filters yield zero matches.

---

## 3. Current Synthetic-Series Generation

### Exact Code Location
* **File:** `backend/app/ml/market/forecaster.py`
* **Functions:**
  * `MandiPriceForecaster._get_commodity_history(commodity, market)` (lines 113–145)
  * `MandiPriceForecaster._build_synthetic_history_if_needed(commodity, market, base_price)` (lines 87–111)

### Execution Trace & Trigger Condition
In `forecaster.py:126`:
```python
sub = df[mask].copy()
if sub["ds"].nunique() >= 15:
    # Real historical series aggregation
    daily = sub.groupby("ds")["modal_price"].mean().reset_index()
    ...
    return daily, current_p

# Triggered whenever historical date count < 15:
daily = self._build_synthetic_history_if_needed(commodity, market or "Regional Mandi", current_p)
return daily, current_p
```

Because `commodity_price.csv` contains only one arrival date (`19/05/2025`), `sub["ds"].nunique()` is **always 1**. Consequently, the branch `sub["ds"].nunique() >= 15` is **never taken**. The system unconditionally executes `_build_synthetic_history_if_needed(...)`.

### Exact Synthetic Mathematical Formula
```python
end_date = datetime.now()
dates = pd.date_range(end=end_date, periods=90, freq="D")
np.random.seed(abs(hash(commodity + market)) % (2**31))

trend = np.linspace(-base_price * 0.03, base_price * 0.04, 90)
weekly = 15.0 * np.sin(2 * np.pi * np.arange(90) / 7.0)
monthly = 25.0 * np.cos(2 * np.pi * np.arange(90) / 30.0)
noise = np.random.normal(0, base_price * 0.008, 90)

prices = base_price + trend + weekly + monthly + noise
prices = np.clip(prices, base_price * 0.7, base_price * 1.4)
```

### Why This Must Be Replaced:
1. **Scientific Honesty:** Prophet and LightGBM are fitting mathematical curves to artificial trigonometric waves and Gaussian noise rather than genuine market dynamics (arrival shocks, seasonal harvests, monsoon cycles, MSP announcements).
2. **Evaluative Invalidation:** Accuracy metrics (MAE, RMSE, MAPE) computed on synthetic history reflect how well models learn simple sine waves, not how well they predict real Indian agricultural market volatility.

---

## 4. Current Prophet Implementation

* **File:** `backend/app/ml/market/forecaster.py:147-169`
* **Method:** `_fit_predict_prophet(self, df_history: pd.DataFrame, days: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]`
* **Model Configuration:**
  ```python
  m = Prophet(
      yearly_seasonality=False,
      weekly_seasonality=True,
      daily_seasonality=False,
      changepoint_prior_scale=0.05,
      interval_width=0.95
  )
  ```
* **Fitting:** `m.fit(df_history[["ds", "y"]])`
  * Executes the underlying CmdStanPy C++ binary (`Chain [1] start processing` $\rightarrow$ `Chain [1] done processing`).
* **Prediction:**
  ```python
  future = m.make_future_dataframe(periods=days, freq="D", include_history=False)
  forecast = m.predict(future)
  ```
* **Output:** Extracts point estimate `yhat`, lower bound `yhat_lower`, and upper bound `yhat_upper`.

---

## 5. Current LightGBM Implementation

* **File:** `backend/app/ml/market/forecaster.py:170-230`
* **Method:** `_fit_predict_lightgbm(self, df_history: pd.DataFrame, days: int, base_price: float) -> np.ndarray`
* **Feature Engineering:**
  * Calendar features: `dayofweek`, `dayofyear`, $\sin(2\pi \cdot \text{dayofyear} / 365.25)$, $\cos(2\pi \cdot \text{dayofyear} / 365.25)$.
  * Autoregressive lag features: `lag_1`, `lag_2`, `lag_7`.
  * Rolling window feature: `rolling_mean_7`.
* **Regressor Hyperparameters:**
  ```python
  model = lgb.LGBMRegressor(
      n_estimators=30,
      learning_rate=0.08,
      num_leaves=15,
      min_child_samples=5,
      random_state=42,
      verbosity=-1
  )
  model.fit(X, y)
  ```
* **Multi-Step Rollout:** Iterative recursive forward simulation: for day $1 \dots N$, previous predicted outputs $\hat{y}_{t-1}$ are fed into `lag_1` and rolling means to predict $\hat{y}_t$.

---

## 6. Current Ensemble Implementation

* **File:** `backend/app/ml/market/forecaster.py:270`
* **Ensemble Weighting:**
  $$\hat{y}_{\text{ensemble}} = (0.60 \cdot \hat{y}_{\text{Prophet}}) + (0.40 \cdot \hat{y}_{\text{LightGBM}})$$
* **Uncertainty Interval Derivation:**
  * Lower bound: $\min(yhat\_lower_{\text{Prophet}}, \hat{y}_{\text{ensemble}} \cdot 0.95)$
  * Upper bound: $\max(yhat\_upper_{\text{Prophet}}, \hat{y}_{\text{ensemble}} \cdot 1.05)$
* **Trend Categorization:**
  * If % change from current price $> +1.2\% \rightarrow$ `"bullish"`
  * If % change from current price $< -1.2\% \rightarrow$ `"bearish"`
  * Otherwise $\rightarrow$ `"stable"`

---

## 7. Current Decision Engine

* **File:** `backend/app/services/mandi_intelligence.py:607-657` and `forecaster.py:298-315`
* **Deterministic Rules (100% Non-LLM):**
  * **Confidence Gate:** If $\text{confidence} < 0.60 \rightarrow$ `INSUFFICIENT_EVIDENCE`.
  * **Hold Signal:** If $\text{expected\_change} \ge +2.5\% \rightarrow$ `HOLD` / `POSSIBLE_UPSIDE`.
  * **Sell Signal:** If $\text{expected\_change} \le -2.5\% \rightarrow$ `SELL_NOW` / `FAVORABLE_TO_SELL`.
  * **Stable Signal:** If between $-2.5\%$ and $+2.5\% \rightarrow$ `STABLE`.
* **Multilingual Localization:** Dictionary mapping across Hindi, English, Gujarati, Marathi, Punjabi, Bengali.

---

## 8. Existing APIs

| Endpoint | Method | Request Parameters / Body | Response Schema | Purpose |
|---|---|---|---|---|
| `/api/v1/market/prices` | GET | `state`, `district`, `commodity`, `crop`, `market` | `MarketPriceListResponse` | Mandi prices list |
| `/api/v1/market/mandis` | GET | None | `List[dict]` | All unique mandis |
| `/api/v1/market/commodities` | GET | None | `List[str]` | All unique crops |
| `/api/v1/market/best-nearby` | GET | `commodity`, `latitude`, `longitude`, `district`, `limit` | `BestMandiResponse` | Geodesic + practical ranking |
| `/api/v1/market/compare` | GET | `commodity`, `market_a`, `market_b` | `MandiComparisonResponse` | ₹ diff & % spread |
| `/api/v1/market/advisory` | GET | `commodity`, `market`, `days`, `language` | `MandiAdvisoryResponse` | Sell vs Wait advisory |
| `/api/v1/market/forecast` | GET | `commodity`, `mandi`, `days` | `MandiForecastResult` | Prophet + LightGBM forecast |
| `/api/v1/market/forecast-explanation` | GET | `commodity`, `market` | `ForecastExplanationResponse` | Momentum & seasonal factors |
| `/api/v1/market/alerts` | POST | `PriceAlertCreate` | `PriceAlertResponse` | Store price alert condition |
| `/api/v1/market/alerts` | GET | `user_id` | `PriceAlertListResponse` | List user price alerts |

---

## 9. Existing Android Contract

### Kotlin Screen: `MandiPricesScreen.kt`
* **Price List Rendering:** Displays modal price, min/max price, observation date, market name, and source.
* **Filter Bar:** Category chips ("ALL CROPS", "GRAINS", "VEGETABLES", "PULSES", "FRUITS", "SPICES") + Search bar.
* **Guided Action Dialogs:**
  1. *Best Practical & Nearby Mandis:* Calls `api.getBestNearbyMandis(commodity)`. Displays highest recorded price mandi vs best practical mandi with geodesic KM.
  2. *Mandi Comparison:* Calls `api.compareMandis(commodity, marketA, marketB)`. Displays side-by-side cards with ₹ difference and % spread.
  3. *Sell vs Wait Advisory:* Calls `api.getMandiAdvisory(commodity, market, days)`. Displays signal badge (`HOLD`, `SELL_NOW`, `STABLE`), projected price, and localized native guidance.
  4. *Price Alert:* Calls `api.createPriceAlert(payload)`.

### Android Contract Stability Note
The REST contract between Android and FastAPI is clean and mature. **All existing endpoints, field names, and DTO structures must remain backward compatible** during the ML and data upgrade.

---

## 10. Existing Tests

### Current Test Inventory:
1. `backend/tests/test_real_mandi_forecaster.py` (7 tests)
   - Verifies CSV loading, Prophet fitting, LightGBM feature engineering, 60/40 ensemble weighting, deterministic actions, caching performance, and pipeline Pydantic schema validation.
2. `backend/tests/test_mandi_intelligence.py` (13 tests)
   - Verifies Haversine geodesic math, coordinate resolution, observation freshness scoring, practical scoring formula, best practical distinction, comparison math, alert storage/retrieval, advisory decision matrix, explanation signals, tool registry execution, and LangGraph multi-turn voice clarification.

**Test Pass Rate:** **20 / 20 passed (100%)** in 28.27 seconds.

---

## 11. Missing Capabilities & Identified Gaps

1. **Gap 1: Absence of Real Longitudinal Historical Series**  
   `commodity_price.csv` has only a single date (`19/05/2025`). The forecaster relies on a synthetic 90-day time-series generator.
2. **Gap 2: Lack of Chronological Train/Val/Test Split & Benchmarking**  
   Because the history is synthetically generated, models have not been evaluated on chronological real-world data against a Naive baseline (`tomorrow_price = today_price`) using MAE, RMSE, and MAPE.
3. **Gap 3: Proactive Alert Evaluation Daemon Missing**  
   Alerts are saved in `mandi_price_alerts`, but there is no background scheduled worker to compare current prices or forecast drops/rises against active triggers.
4. **Gap 4: Explicit Mandi Intelligence Agent Abstraction**  
   The current code lives in separate modules (`MandiIntelligenceService`, `MandiPriceForecaster`, `MarketService`). There is no unified `MandiIntelligenceAgent` that encapsulates all 7 domain tools under a single interface for both REST and LangGraph.
5. **Gap 5: No Clean "INSUFFICIENT_HISTORY" Signal**  
   When a commodity/mandi has sparse data, the system manufactures history rather than explicitly notifying the user/orchestrator of insufficient history.

---

## 12. Proposed Migration Plan (Phases 2 – 10)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MIGRATION ROADMAP OVERVIEW                            │
│                                                                             │
│  Phase 1: Read-Only Audit (COMPLETED)                                       │
│      └── Comprehensive audit document created (docs/MANDI_UPGRADE_AUDIT.md) │
│                                                                             │
│  Phase 2: Real Longitudinal Mandi Dataset Ingestion                         │
│      ├── Source authentic multi-date Agmarknet daily bulletin records       │
│      ├── Normalize schema: commodity, mandi, date, modal, min, max, arrivals│
│      └── Store in data/mandi_historical_longitudinal.csv / database         │
│                                                                             │
│  Phase 3: Data Quality & Cleaning Pipeline                                  │
│      ├── Duplicate detection, date continuity, price outlier filtering      │
│      └── Generate docs/MANDI_DATA_QUALITY_REPORT.md                         │
│                                                                             │
│  Phase 4 & 5: Chronological Model Training & Evaluation                     │
│      ├── Chronological Train (70%) / Validation (15%) / Test (15%)          │
│      ├── Eliminate synthetic series generator                              │
│      ├── Compute MAE, RMSE, MAPE for Prophet, LightGBM, Ensemble vs Naive   │
│      └── Generate docs/MANDI_FORECAST_EVALUATION.md                         │
│                                                                             │
│  Phase 6: Multi-Tool Mandi Intelligence Agent Architecture                  │
│      ├── Implement MandiIntelligenceAgent with 7 clean domain tools         │
│      └── Maintain 100% backward compatibility with existing REST endpoints │
│                                                                             │
│  Phase 7: Proactive Alert Monitoring Worker                                 │
│      └── Background evaluator checking active triggers against new data     │
│                                                                             │
│  Phase 8: LangGraph Multilingual Voice Integration                          │
│      └── Connect all 7 agent tools to LangGraph tool router & synthesizer   │
│                                                                             │
│  Phase 9 & 10: Regression Testing & Final Documentation                     │
│      ├── Verify Android DTO compatibility                                   │
│      ├── Expand test suite to >= 25 tests                                   │
│      └── Generate final upgrade report (docs/MANDI_UPGRADE_REPORT.md)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Audit Sign-Off

* **Audit Status:** **Phase 1 Completed**.
* **Safety & Integrity Confirmation:**
  * Zero code changes were made in Phase 1.
  * No existing files or endpoints were broken.
  * The synthetic generation locus has been precisely pinpointed to `app/ml/market/forecaster.py:87-145`.
* **Next Action:** Wait for user review and approval of this audit before beginning **Phase 2 (Real Longitudinal Data)**.
