# FarmFusion — Mandi Guided Action UX & Multi-Turn Voice Integration Report

**Date**: August 31, 2026  
**Status**: Production-Ready / Fully Tested & Verified  
**Scope**: Android `MandiPricesScreen.kt`, LangGraph Voice Orchestrator, Multi-turn Context Memory, and Mandi Intelligence Service  

---

## 1. Overview & Problem Solved

Previously, tapping quick action chips on the Mandi Prices screen triggered network requests with hardcoded assumptions or showed empty dialogs.

This upgrade transforms the **FOUR core Mandi actions** into proactive, guided input flows:
1. **[ 📍 Best Nearby ]**
2. **[ ⚖️ Compare ]**
3. **[ 📈 Sell / Wait ]**
4. **[ 🔔 Set Alert ]**

No action opens into an ambiguous or blank state. The interface actively guides the farmer through required parameters (crop selection, mandi choices, alert thresholds), executes strict input validation, and renders structured, deterministic results.

---

## 2. Guided UX Flows

### 1. Best Nearby Flow
- **Trigger**: Farmer taps `[ 📍 Best Nearby ]`.
- **Guided Step**: "Which crop do you want to check? / फसल चुनें:" with popular crop chips (`Wheat`, `Mustard`, `Groundnut`, `Gram`, `Cotton`, `Soybean`, `Maize`, `Onion`, `Tomato`, `Garlic`).
- **Processing**: Fetches real nearby mandis using the farmer's location.
- **Display**:
  - **⭐ Best Practical Option**: Shows multi-criteria score (combining price, distance, and freshness) and reason (e.g. *"उच्च दर्ज भाव (₹2,580/Q) + बहुत कम दूरी (8.4 km)"*).
  - **🏆 Highest Recorded Price**: Highlights the regional peak price and distance.
  - **Nearby Alternatives**: Lists alternative markets with data freshness status (`FRESH`, `RECENT`, `STALE`).

### 2. Compare Flow
- **Trigger**: Farmer taps `[ ⚖️ Compare ]`.
- **Guided Steps**:
  - **Step 1**: Select Crop (quick chips or search).
  - **Step 2**: First Mandi (e.g. `Udaipur`).
  - **Step 3**: Second Mandi (e.g. `Jaipur`).
- **Validation**:
  - Requires crop selection.
  - Requires both mandis.
  - Rejects comparing a market with itself (`Market A != Market B`).
- **Display**: Side-by-side modal cards, absolute ₹ difference, percentage difference, and natural Hindi/English commentary.

### 3. Sell vs Wait Advisory Flow
- **Trigger**: Farmer taps `[ 📈 Sell vs Wait ]`.
- **Guided Steps**:
  - **Step 1**: Select Crop.
  - **Step 2**: Select Mandi.
- **Validation**: Ensures crop and mandi are specified before calling the Prophet + LightGBM advisory engine.
- **Display**:
  - Current observed price & arrival date.
  - 7-Day projected forecast & expected percentage change.
  - Advisory Signal Badge (`POSSIBLE_UPSIDE`, `FAVORABLE_TO_SELL`, `STABLE`, `INSUFFICIENT_EVIDENCE`).
  - Safe, non-fabricated advisory text with financial disclaimer.

### 4. Set Alert Flow
- **Trigger**: Farmer taps `[ 🔔 Set Alert ]`.
- **Guided Steps**:
  - **Step 1**: Select Crop.
  - **Step 2**: Select Mandi (optional, defaults to all mandis).
  - **Step 3**: Choose condition (`Rises Above` or `Drops Below`).
  - **Step 4**: Enter target threshold (e.g. `2600`).
- **Validation**: Enforces positive numeric threshold and non-empty crop.
- **Display**: Active alert confirmation banner: *"Alert set for Wheat — Udaipur when price goes above ₹2600/Q!"*

---

## 3. Multi-Turn Voice Assistant Behavior

The LangGraph Orchestrator now supports proactive clarification and multi-turn slot filling for Mandi voice queries:

| Turn | Farmer Utterance | Assistant Action / Response |
|---|---|---|
| **Turn 1** | *"Compare मंडी भाव"* | Identifies `compare_mandi` intent; detects missing crop; asks: *"किस फसल का भाव compare करना है?"* |
| **Turn 2** | *"गेहूं"* | Fills `commodity = "Wheat"`; detects missing mandis; asks: *"कौन-कौन सी दो मंडियों की तुलना करनी है?"* |
| **Turn 3** | *"उदयपुर और जयपुर"* | Fills `market_a = "Udaipur"`, `market_b = "Jaipur"`; executes comparison tool and speaks result. |
| **Alert Turn 1** | *"गेहूं के लिए alert लगाओ"* | Identifies `price_alert` intent; detects missing target price; asks: *"Wheat के लिए किस भाव पर अलर्ट सेट करना है (जैसे ₹2600)?"* |
| **Alert Turn 2** | *"2600 से ऊपर"* | Fills `target_price = 2600.0`, `direction = "ABOVE"`; creates alert. |

---

## 4. Verification & Test Results

### 1. Backend Pytest Suite
- **File**: [`backend/tests/test_mandi_intelligence.py`](file:///home/rdj/FarmFusionFinal/backend/tests/test_mandi_intelligence.py)
- **Result**: **`13 / 13 PASSED (100%)`**
- **Coverage Highlights**:
  - Geodesic Haversine calculations & coordinate lookup
  - Freshness score classification (`FRESH`, `RECENT`, `STALE`)
  - Practical ranking vs Highest price distinction
  - Mandi comparison arithmetic & summaries
  - Price alert creation & user query
  - Sell-now vs wait advisory matrix
  - Multi-turn voice comparison clarification
  - Multi-turn voice alert clarification

### 2. Android Kotlin Build & Tests
- **Command**: `./gradlew :app:compileDebugKotlin :app:testDebugUnitTest`
- **Result**: **`BUILD SUCCESSFUL`** with zero compilation errors and zero warnings.
