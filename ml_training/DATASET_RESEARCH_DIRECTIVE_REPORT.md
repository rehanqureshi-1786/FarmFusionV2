# FarmFusion Crop Model V2 — Final Real-Data Research & Readiness Directive Report

**Date**: August 23, 2026  
**Auditor**: Antigravity AI Engineering Team  
**Evaluation Standard**: Ground-Truth Agricultural Integrity, Anti-Fabrication & Scientific Defensibility Mandate

---

## 1. Executive Summary & Final Verdict

```
################################################################################
🛑 FINAL VERDICT: NOT_READY_FOR_TRAINING
################################################################################
```

### Executive Summary:
A comprehensive investigation was conducted across national Indian agricultural research repositories, ICAR institutes, All India Coordinated Research Projects (AICRP-LTFE, AICRP-STCR), state agricultural universities (SAUs), government statistical portals (UPAg, SHC, DES), and open academic data repositories (Zenodo, Dryad, Harvard Dataverse, Mendeley Data, KRISHI).

**Key Finding**: No publicly downloadable dataset currently exists in India that provides an authentic, field-level micro-pairing of:
1. Laboratory measured Soil $N, P, K, pH$ ($0–15\text{ cm}$ plow layer)
2. Georeferenced plot location / district
3. Observed seasonal weather (temperature, relative humidity, cumulative seasonal precipitation)
4. Ground-truth crop choice / yield grown on that **exact same plot**.

Merging district-level Soil Health Card averages with district-level UPAg crop statistics creates pseudo-observations where 5–15 distinct crops receive the exact same input features. In strict adherence to our anti-fabrication directive:
* **No synthetic or pseudo-joined model will be trained.**
* **The Google Colab training gate remains locked.**
* **Production continues using verified Mode A (ML OCR verification with explicit distribution notices) and Mode B (Environmental Suitability Engine).**

---

## 2. Dataset Readiness & ML Validation Table

| Dataset | Real Measurements? | Plot-Linked Crop? | Climate Join Feasible? | Units Verified? | Spatial Validity | Temporal Validity | Valid for Multiclass Crop Choice ML? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Soil Health Card (SHC) Scheme** | ✅ Yes (Lab tested) | ❌ No (Holding crop unlinked in public exports) | ⚠️ Conditional | ✅ $N, P_2O_5, K_2O$ ($kg/ha$), $pH$ | District / Block aggregates | Multi-year cycles (2015–2026) | ❌ **NO** (Lacks paired crop label per sample) |
| **UPAg / DES APY Statistics** | ✅ Yes (Official harvest) | ⚠️ District total (Not plot-level) | ⚠️ District centroid matching | ✅ Area ($ha$), Prod ($t$), Yield ($kg/ha$) | District administrative level | Annual & Seasonal (1997–2024) | ❌ **NO** (Lacks soil chemical parameters) |
| **ICRISAT District Level Database (DLD)** | ✅ Yes (Agricultural census) | ⚠️ District total | ✅ Monthly / Annual precipitation | ⚠️ Fertilizer *consumption* ($t$), NOT soil test values | 571 districts | Annual (1966–2016) | ❌ **NO** (Historical; lacks soil nutrient status) |
| **ICAR-AICRP LTFE (Long-Term Fertilizer Experiments)** | ✅ Yes (Lab tested, $0–15\text{ cm}$) | ✅ Yes (Fixed experimental plots) | ✅ Station weather records | ✅ Available $N, P_2O_5, K_2O, pH$ | 18 Research Station locations | Continuous (1970–Present) | ❌ **NO** (Only 2 fixed crops per site in rotation, e.g. Rice-Wheat; cannot train a 20+ crop choice classifier) |
| **ICAR-AICRP STCR (Soil Test Crop Response)** | ✅ Yes (Field trials) | ⚠️ Site-specific trial plots | ⚠️ Zonal trials | ✅ Targeted yield equations ($FN=aT-bSN$) | Agro-Ecological Zones | Published trial bulletins | ❌ **NO** (Published as algebraic equations, non-tabular) |
| **IMD Gridded Meteorological Data** | ✅ Yes (Observed rain-gauge) | N/A (Climate only) | ✅ Spatial grid overlay | ✅ Daily precipitation ($mm$), $T_{max}, T_{min}$ ($^\circ C$) | $0.25^\circ \times 0.25^\circ$ / $1.0^\circ \times 1.0^\circ$ | Daily (1901–Present) | ⚠️ **CLIMATE LAYER ONLY** (Requires paired crop/soil layer) |
| **Open-Meteo ERA5-Land Reanalysis** | ✅ Yes (Copernicus reanalysis) | N/A (Climate only) | ✅ Coordinate-based lookup | ✅ Hourly/Daily $mm, ^\circ C, \%$ | $0.1^\circ \times 0.1^\circ$ (~$9\text{ km}$) | Daily (1950–Present) | ✅ **ACTIVE PRODUCTION BASELINE** |
| **Kaggle Crop Recommendation Dataset** | ❌ NO (Synthetic) | ❌ NO (No plot link) | ❌ NO ($20–300\text{ mm}$ misaligned) | ❌ NO (Unverified) | ❌ None | ❌ None | ❌ **REJECTED (OLD_BASELINE ONLY)** |

---

## 3. Deep-Dive Audit of Candidate Datasets

### A. ICAR-AICRP on Long-Term Fertilizer Experiments (LTFE)
* **Official Owner**: ICAR - Indian Institute of Soil Science (IISS), Bhopal.
* **Portal / Reference**: [aicrp.icar.gov.in/ltfe](https://aicrp.icar.gov.in/ltfe/)
* **Scientific Scope**: Established in 1970 across 18 centers (e.g. Pantnagar, Ludhiana, Jabalpur, Coimbatore, Barrackpore) covering major soil orders (Inceptisols, Vertisols, Alfisols, Mollisols).
* **Observation Structure**: Permanent layout plots receiving graded doses of $N, P, K$, farmyard manure (FYM), and control treatments.
* **Why it cannot train Model V2**:
  1. Each center evaluates **only one fixed 2-crop rotation sequence** (e.g., Rice-Wheat at Pantnagar; Soybean-Wheat at Jabalpur; Maize-Wheat at Ludhiana; Finger Millet-Maize at Coimbatore).
  2. The research objective is measuring **yield decline and soil nutrient depletion under continuous fertilization**, not predicting which crop a farmer should sow among competing options.
  3. Total crop diversity across all 18 centers is limited to $<8$ crops, each confined to a single geographic station.

### B. ICAR-AICRP on Soil Test Crop Response (STCR)
* **Official Owner**: ICAR - Indian Institute of Soil Science (IISS), Bhopal.
* **Scientific Scope**: Multi-locational calibration trials establishing targeted yield equations:
  $$FN = a \cdot T - b \cdot SN$$
  $$FP_2O_5 = c \cdot T - d \cdot SP$$
  $$FK_2O = e \cdot T - f \cdot SK$$
  *Where $T$ is target yield ($q/ha$), $SN, SP, SK$ are initial soil test values ($kg/ha$), and $a,b,c,d,e,f$ are crop/soil constants.*
* **Why it cannot train Model V2**: STCR outputs mathematical fertilizer prescription formulas for predetermined crops, not tabular classification datasets for crop selection.

### C. Soil Health Card (SHC) & UPAg Spatial Join Disqualification
* **SHC Reality**: Public exports provide district-level summaries (percentages of samples Low/Medium/High or mean N/P/K values).
* **UPAg Reality**: District-level aggregate statistics of total hectares sown and metric tonnes harvested.
* **Scientific Disqualification**: Merging these two datasets assigns the identical soil feature vector to every crop cultivated in that district. A machine learning model trained on such data learns arbitrary noise rather than genuine soil-crop agronomic affinities.

---

## 4. Feature Semantics & Chemical Unit Verification

| Feature | Standard Unit | Measurement Methodology | Indian Agricultural Semantics |
| :--- | :--- | :--- | :--- |
| **Nitrogen ($N$)** | $kg/ha$ | Alkaline Permanganate method (Subbiah & Asija, 1956) | Readily mineralizable / available Nitrogen. |
| **Phosphorus ($P$)** | $kg/ha$ | Olsen's $NaHCO_3$ ($pH > 6.5$) or Bray No. 1 ($pH \le 6.5$) | Reported as **Available $P_2O_5$ equivalent** in Soil Health Cards ($P = P_2O_5 \times 0.436$). |
| **Potassium ($K$)** | $kg/ha$ | Neutral normal $NH_4OAc$ extraction (Flame Photometry) | Reported as **Available $K_2O$ equivalent** in Soil Health Cards ($K = K_2O \times 0.830$). |
| **Soil Reaction ($pH$)** | Dimensionless ($0.0–14.0$) | $1:2.5$ or $1:2$ soil-water suspension | Direct potentiometric measurement. |
| **Soil Type** | Categorical | Farmer UI Selection | `"Sandy Soil"`, `"Black Soil"`, `"Red Soil"`, `"Alluvial Soil"`. **Never converted to synthetic N/P/K.** |
| **Rainfall** | $mm$ | Cumulative seasonal sum across growth cycle | **Kharif**: June 1 – October 31; **Rabi**: November 1 – March 31; **Zaid**: March 1 – May 31. Sourced from ERA5-Land reanalysis. |

---

## 5. Dual Model Strategy Definition

To maintain total transparency, FarmFusion separates its predictive and advisory systems into two distinct paradigms:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FARMFUSION MODEL STRATEGY                             │
├──────────────────────────────────────┬──────────────────────────────────────┤
│ TARGET A: Crop Choice (Empirical ML) │ TARGET B: Agronomic Suitability (KB) │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ • Predicts what crop was actually    │ • Evaluates physiological/climatic   │
│   sown based on plot ground-truth.   │   suitability of candidate crops.    │
│ • Requires authentic micro-dataset   │ • Driven by ICAR/FAO rules in        │
│   linking holding soil to harvest.   │   `crop_agronomic_rules.json`.       │
│ • STATUS: HALTED (Pre-Training Gate) │ • STATUS: ACTIVE IN PRODUCTION       │
│   until micro-data is acquired.      │   (Mode B: Environmental Engine).    │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 6. Recommended Future FarmFusion Field Data Collection Protocol

Because no public dataset currently meets the micro-level pairing criteria, FarmFusion establishes an official field-data collection protocol to gather authentic ground truth over time.

### A. Proposed Field Observation Data Schema
```csv
farm_id,plot_id,latitude,longitude,district,state,soil_sample_date,soil_sample_depth_cm,nitrogen_kg_ha,phosphorus_p2o5_kg_ha,potassium_k2o_kg_ha,ph,soil_type,crop_sown,crop_variety,sowing_date,harvest_date,actual_yield_q_ha,irrigation_type,kharif_rainfall_mm,rabi_rainfall_mm,mean_temp_c,mean_humidity_pct,lab_name,lab_certificate_id,farmer_confirmed
```

### B. Field Sampling & Quality Protocol:
1. **Soil Sampling Standard**:
   * Collect composite core samples from $0–15\text{ cm}$ plow depth across $8–10$ zigzag sub-spots per plot.
   * Air-dry, grind to pass through a $2\text{ mm}$ sieve, and analyze at an ICAR-accredited or NABL-certified Soil Testing Laboratory (STL).
   * Record exact laboratory certificate ID and testing methodology.
2. **Crop & Phenology Tracking**:
   * Record exact crop species, cultivar/variety, sowing date, and harvest date.
   * Verify harvest yield in quintals per hectare ($q/ha$).
3. **Automated Climate Assimilation**:
   * Upon recording plot GPS coordinates and sowing/harvest dates, automatically query Open-Meteo ERA5-Land reanalysis for daily precipitation, $T_{max}$, $T_{min}$, and relative humidity across the exact crop-growing window.
4. **Sampling Target for Model V2 Activation**:
   * **Minimum Sample Size**: $\ge 5,000$ verified plot-level records.
   * **Geographic Coverage**: Minimum 10 Indian states across 6 major Agro-Ecological Zones (Arid Western, Semi-Arid Peninsular, Northern Alluvial Plains, Coastal Humid, Central Plateau, Eastern Humid).
   * **Crop Distribution**: Minimum 15 crop classes with $\ge 250$ independent farm observations per class.

---

## 7. Model Training & Export Plan (Upon Micro-Data Availability)

When the FarmFusion field data collection reaches the $\ge 5,000$ sample feasibility threshold:
1. **Notebook Execution**: Run `ml_training/notebooks/FarmFusion_Crop_Model_V2.ipynb` in Google Colab.
2. **Multi-Model Benchmark**: Train XGBoost, LightGBM, CatBoost, and Random Forest using spatial holdouts (by State/AEZ).
3. **Probability Calibration**: Calibrate using Isotonic Regression; compute multi-class Expected Calibration Error (ECE) and Brier scores.
4. **OOD Distribution Bounds**: Extract $P_1$ and $P_{99}$ empirical bounds for $N, P, K, pH, \text{Temp}, \text{Humidity}, \text{Rainfall}$.
5. **Artifact Export**: Export `crop_model_v2.joblib`, `crop_label_encoder_v2.joblib`, `crop_model_v2_calibrator.joblib`, and `crop_model_v2_metadata.json` into `backend/app/ml_models/`.

---

## 8. Summary of Current Production Status

* **FastAPI Backend**: Fully operational on verified Mode A (ML OCR verification with explicit distribution notices) and Mode B (Environmental Suitability Engine).
* **Android Frontend**: Modern, neo-brutalist UI supporting 4 farmer-selectable soil types (`Sandy Soil`, `Black Soil`, `Red Soil`, `Alluvial Soil`), Soil Health Card OCR scanning, and transparent data provenance badges.
* **Test Suite**: 18/18 pytest tests passing with 100% green status.
