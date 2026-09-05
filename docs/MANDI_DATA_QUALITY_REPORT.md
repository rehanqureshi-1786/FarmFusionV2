# FarmFusion Mandi Data Quality Report (Phase 2)

**Report Date**: September 4, 2026  
**Pipeline**: Longitudinal Agmarknet Mandi Price Ingestion  
**Processed Target Dataset**: `backend/data/mandi_training_timeseries.csv` (Mirror: `backend/data/mandi_processed/mandi_historical_clean.csv`)  
**Ingestion Script**: `backend/scripts/ingest_mandi_history.py`  

---

## 1. Executive Summary

This report provides a comprehensive data audit of the genuine longitudinal agricultural market price observations ingested into FarmFusion. All synthetic data generators, sine-wave price models, and Gaussian random jitter have been removed.

- **Total Raw Records Ingested**: 468,284  
- **Total Processed Clean Records**: 255,428  
- **Duplicate Records Removed**: 212,856  
- **Invalid / Zero / Non-Numeric Prices Filtered**: 0  
- **Earliest Authentic Date**: January 1, 2020 (`2020-01-01`)  
- **Latest Authentic Date**: December 5, 2025 (`2025-12-05`)  
- **Longitudinal Span**: 71 months (~5.9 years)  
- **Total Unique Observation Dates**: 1,655  
- **Total Unique Commodities**: 125  
- **Total Unique Mandis / Markets**: 1,663  
- **Total Unique Districts**: 416  
- **Total Unique States / UTs**: 31  

---

## 2. Ingestion & Filtering Funnel

| Step | Operation | Record Count | Delta |
|---|---|---|---|
| **Raw Source 1** | `agmarknet_pan_india_2023_2025.csv` | 456,298 | +456,298 |
| **Raw Source 2** | `cotton.csv` (MP Mandi Agmarknet 2020-2022) | 8,818 | +8,818 |
| **Raw Source 3** | `commodity_price.csv` (Baseline Snapshot) | 2,733 | +2,733 |
| **Raw Source 4** | `sample_agmarknet_onion_nashik.csv` (Nashik Mandi) | 435 | +435 |
| **Raw Input Total** | All combined raw sources | **468,284** | — |
| **Deduplication** | Exact duplicate key match (`commodity`, `variety`, `market`, `date`, `modal_price`) | 255,428 | -212,856 |
| **Price Filtering** | Removal of `modal_price <= 0`, `min > max`, or NaN dates/prices | 255,428 | 0 |
| **Final Processed** | Fully normalized longitudinal dataset | **255,428** | — |

---

## 3. Commodity Breakdown & History Depth

### Multi-Date Longitudinal Commodities (Eligible for ML Forecasting)

| Commodity | Clean Records | Unique Dates | Unique Markets | Date Span | Minimum History Rule ($\ge 30$) |
|---|---|---|---|---|---|
| **Onion** | 98,561 | **817** | 1,050 | 2023-01-07 to 2025-12-05 | **Eligible** (817 > 30) |
| **Cotton** | 8,375 | **813** | 39 | 2020-01-01 to 2025-05-19 | **Eligible** (813 > 30) |
| **Potato** | 109,374 | **737** | 986 | 2023-01-07 to 2025-12-05 | **Eligible** (737 > 30) |
| **Wheat** | 25,327 | **247** | 708 | 2023-01-07 to 2025-05-19 | **Eligible** (247 > 30) |
| **Tomato** | 9,127 | **155** | 687 | 2023-01-07 to 2025-05-19 | **Eligible** (155 > 30) |
| **Paddy (Dhan)** | 2,588 | **62** | 224 | 2025-01-05 to 2025-12-05 | **Eligible** (62 > 30) |

All 6 major national commodities comfortably satisfy the minimum 30-day requirement. Five of them exceed 90 genuine observation dates, satisfying the Phase 2 verification criterion ($\ge 1$ commodity with $\ge 90$ genuine dates).

### Commodities with Insufficient History (< 30 Observations)

119 commodities originated from the legacy single-date Agmarknet bulletin (`commodity_price.csv`, snapshot date `2025-05-19`), including:
- Mustard (16 records, 1 date)
- Soybean (6 records, 1 date)
- Gram / Chana (1 date)
- Apple, Apricot, Ajwan, Barley, Maize, etc. (1 date)

**Policy Decision**:
Any forecaster invocation for these 119 commodities (or for specific mandis lacking $\ge 30$ historical observations) returns:
```json
{
  "status": "INSUFFICIENT_HISTORY",
  "confidence_level": 0.0,
  "deterministic_action": {
    "action": "INSUFFICIENT_EVIDENCE"
  }
}
```
**FarmFusion strictly prohibits manufacturing artificial time series for crops with insufficient history.**

---

## 4. Commodity + Mandi Pair Analysis

| Threshold (Unique Dates) | Number of Commodity-Mandi Pairs | System Behavior |
|---|---|---|
| **$\ge 365$ dates (1+ Year)** | 14 pairs | Full multi-year seasonality modeling |
| **$\ge 180$ dates (6+ Months)** | 448 pairs | Robust multi-season forecasting |
| **$\ge 90$ dates (3+ Months)** | 1,121 pairs | Standard Prophet + LightGBM ensemble |
| **$\ge 60$ dates (2+ Months)** | 1,444 pairs | Meets Phase 2 verification criterion ($\ge 1$ pair with $\ge 60$ dates) |
| **$\ge 30$ dates (Minimum)** | 1,975 pairs | Minimum threshold for ML forecasting |
| **$< 30$ dates** | Remaining pairs | Returns `INSUFFICIENT_HISTORY` |

### Top 15 Commodity-Mandi Pairs by Historical Depth

| Rank | Commodity | Mandi / APMC | State | Unique Dates | Record Count |
|---|---|---|---|---|---|
| 1 | Cotton | Sendhwa | Madhya Pradesh | **535** | 535 |
| 2 | Cotton | Khetia | Madhya Pradesh | **533** | 533 |
| 3 | Cotton | Kukshi | Madhya Pradesh | **496** | 496 |
| 4 | Onion | Pratapgarh | Uttar Pradesh | **458** | 458 |
| 5 | Cotton | Badwaha | Madhya Pradesh | **435** | 435 |
| 6 | Onion | Nashik | Maharashtra | **435** | 435 |
| 7 | Potato | Durgapur | West Bengal | **427** | 427 |
| 8 | Cotton | Gandhwani | Madhya Pradesh | **406** | 406 |
| 9 | Cotton | Bhikangaon | Madhya Pradesh | **404** | 404 |
| 10 | Cotton | Saunsar | Madhya Pradesh | **402** | 402 |
| 11 | Potato | Pratapgarh | Uttar Pradesh | **396** | 396 |
| 12 | Cotton | Badwani | Madhya Pradesh | **392** | 392 |
| 13 | Cotton | Manawar | Madhya Pradesh | **392** | 392 |
| 14 | Cotton | Anjad | Madhya Pradesh | **389** | 389 |
| 15 | Potato | Alipurduar | West Bengal | **363** | 363 |

---

## 5. Missing Values & Field Completeness

| Target Field | Processed Non-Null Count | Null Count | % Complete | Handling Strategy |
|---|---|---|---|---|
| `commodity` | 255,428 | 0 | 100.0% | Normalized to Title Case |
| `variety` | 255,428 | 0 | 100.0% | Preserved ("Other" if unstated) |
| `market` | 255,428 | 0 | 100.0% | Normalized to Title Case |
| `date` | 255,428 | 0 | 100.0% | ISO-8601 `YYYY-MM-DD` |
| `modal_price` | 255,428 | 0 | 100.0% | Float numeric (₹/Quintal) |
| `min_price` | 255,428 | 0 | 100.0% | Float numeric (₹/Quintal) |
| `max_price` | 255,428 | 0 | 100.0% | Float numeric (₹/Quintal) |
| `district` | 194,457 | 60,971 | 76.1% | Left null when not in bulletin source; never invented |
| `state` | 194,272 | 61,156 | 76.0% | Left null when not in bulletin source; never invented |
| `arrivals` | 435 | 254,993 | 0.17% | Populated where recorded; never invented |
| `source` | 255,428 | 0 | 100.0% | Fully tracked |
| `source_record_id` | 255,428 | 0 | 100.0% | MD5 provenance hash |

---

## 6. Date Continuity and Mandi Operating Dynamics

Analysis of high-density markets (e.g. Nashik Onion, Sendhwa Cotton) shows realistic trading calendar behavior:
- Mandis operate Monday through Saturday and remain closed on Sundays and gazetted national holidays (e.g. Republic Day, Diwali).
- Lags and rolling averages in `LightGBM` operate on chronological sequential trading days (`ds`) rather than calendar day offsets, ensuring that non-trading holidays do not introduce synthetic null values.
