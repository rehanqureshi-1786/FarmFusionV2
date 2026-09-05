# FarmFusion Mandi Data Provenance Document

**Document Version**: 2.0  
**Effective Date**: September 4, 2026  
**Pipeline**: Longitudinal Agmarknet Historical Ingestion  
**Repository Location**: `backend/data/mandi_training_timeseries.csv`  

---

## 1. Authoritative Data Sources

FarmFusion ingests historical agricultural price records exclusively from authoritative Indian government sources:

| Source Identifier | Government Authority | Origin URL / Portal | Primary Time Span Covered | Total Ingested Records |
|---|---|---|---|---|
| **Agmarknet Pan-India Bulletin** | Directorate of Marketing & Inspection (DMI), Ministry of Agriculture & Farmers Welfare, Govt of India | `https://agmarknet.gov.in` / `data.gov.in` (Agmarknet Daily Market Bulletin) | Jan 2023 – Dec 2025 | 456,298 raw rows |
| **Agmarknet Madhya Pradesh Cotton Series** | Madhya Pradesh State Agricultural Marketing Board (Mandi Board) via Agmarknet | `https://agmarknet.gov.in` (APMC Sendhwa, Khetia, Kukshi, Badwaha) | Jan 2020 – Dec 2022 | 8,818 raw rows |
| **Agmarknet Maharashtra Onion Series** | Maharashtra State Agricultural Marketing Board (MSAMB) via Agmarknet | `https://agmarknet.gov.in` (APMC Nashik / Lasalgaon) | Jul 2024 – Sep 2025 | 435 raw rows |
| **Agmarknet Daily Snapshot** | Ministry of Agriculture & Farmers Welfare | `https://agmarknet.gov.in` (Daily pan-India arrival bulletin) | May 19, 2025 | 2,733 raw rows |

---

## 2. Ingestion & Transformation Pipeline

The ingestion pipeline is completely automated, reproducible, and contained in:  
`backend/scripts/ingest_mandi_history.py`

### Step-by-Step Transformations:

1. **Raw Storage**:
   Raw unmodified source files are preserved permanently in:  
   `backend/data/mandi_raw/`
   No raw file is ever edited or overwritten in place.

2. **Column Normalization**:
   Different Agmarknet portals export columns with differing headers and XML namespaces (e.g., `Modal_x0020_Price`, `Modal Price (Rs./Quintal)`, `Arrival_Date`, `Reported Date`).  
   The script maps all headers to a canonical target schema:
   - `commodity` (String, Title Case)
   - `variety` (String, Title Case)
   - `market` (String, Title Case)
   - `district` (String, Title Case, nullable)
   - `state` (String, Title Case, nullable)
   - `date` (ISO-8601 Date string: `YYYY-MM-DD`)
   - `min_price` (Float numeric)
   - `max_price` (Float numeric)
   - `modal_price` (Float numeric)
   - `arrivals` (Float numeric or null)
   - `source` (String tracking parent dataset)
   - `source_record_id` (Hexadecimal MD5 hash of raw record for deduplication and audit tracking)

3. **Date Normalization**:
   Dates are parsed across both Indian standard (`%d/%m/%Y`, `%d-%m-%Y`) and ISO (`%Y-%m-%d`, `%Y/%m/%d`) formats and converted strictly into ISO-8601 (`YYYY-MM-DD`). Records with unparseable dates are rejected.

4. **Numeric Sanitization**:
   - Currency symbols (`₹`, `Rs.`), commas, whitespace, and non-numeric characters are stripped.
   - Values are cast to `float64`.
   - Records with zero or negative `modal_price` are discarded.
   - If `min_price` > `max_price`, prices are swapped to preserve consistency.

5. **Deduplication**:
   Exact duplicate records across commodity, variety, market, date, and modal_price are eliminated. Out of 468,284 raw rows, 212,856 duplicate entries across multiple bulletin downloads were removed, yielding 255,428 unique, verifiable records.

6. **Target Dataset Output**:
   Saved to:
   - `backend/data/mandi_processed/mandi_historical_clean.csv`
   - `backend/data/mandi_training_timeseries.csv`

---

## 3. Excluded Data & Rejection Rules

- **Zero and Negative Prices**: Discarded.
- **Extreme Unrealistic Outliers**: Discarded where modal price exceeded 10x the commodity's historical interquartile range (IQR).
- **Synthetic / Generated Data**: In previous versions, missing dates were generated using `np.sin()` and Gaussian jitter. **All synthetic data generation has been permanently decommissioned.**

---

## 4. Known Limitations & Integrity Commitments

1. **Holiday Gaps**: Indian mandis do not trade on Sundays and gazetted public holidays. Time series are not strictly contiguous across calendar days; they are contiguous across trading sessions.
2. **Coverage Disparity**: Commodities such as Onion (817 dates), Cotton (813 dates), Potato (737 dates), Wheat (247 dates), and Tomato (155 dates) have deep multi-year coverage. Niche spices and minor pulses currently have single-date records.
3. **Threshold Enforcement**: FarmFusion enforces a hard minimum threshold of `MIN_OBSERVATIONS = 30` authentic dates for any commodity/mandi pair. If an APMC or crop has fewer than 30 dates, the model returns `INSUFFICIENT_HISTORY` rather than attempting a low-sample forecast.
