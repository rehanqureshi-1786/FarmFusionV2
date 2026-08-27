# FarmFusion Crop Model V2: Dataset Availability, Provenance & Feasibility Gate

## 1. Core Principles & Strict Data Taxonomy

To guarantee scientific defensibility and total data integrity, all information utilized across FarmFusion is categorized into 5 mutually exclusive data tiers. **A tier cannot be converted into another or disguised as laboratory ground truth.**

### The 5 Data Categories:
* **Category A: Directly Measured / Observed Data**
  * *Definition*: Primary empirical measurements gathered through physical laboratory analysis, field surveys, or hardware meteorological stations.
  * *Examples*: Laboratory Soil Health Card test entries (N, P, K, pH), Government crop harvesting statistics (APY reported by District Agricultural Officers), IMD physical rain-gauge readings.
* **Category B: Reanalysis & Modeled Environmental Data**
  * *Definition*: Numerical model assimilations combining satellite observations and physical atmospheric/soil models.
  * *Examples*: Copernicus ERA5-Land climate reanalysis ($0.1^\circ \times 0.1^\circ$), ISRIC SoilGrids ($250\text{ m}$ spatial depth modeling).
  * *Rule*: Reanalysis must **never** be cited as direct on-site laboratory measurements.
* **Category C: Derived & Engineered Features**
  * *Definition*: Deterministic mathematical aggregations or interactions computed from Category A or B inputs.
  * *Examples*: `NPK_sum = N + P + K`, `N_to_P_ratio = N / (P + 1e-6)`, `rainfall = sum(daily_precip[Kharif_start : Kharif_end])`.
* **Category D: Farmer-Provided Information**
  * *Definition*: Inputs supplied directly by the agricultural producer via application UI or verified OCR review.
  * *Examples*: `farmer_selected_soil_type` (`"Sandy Soil"`, `"Black Soil"`, `"Red Soil"`, `"Alluvial Soil"`), farm size (acres), confirmation/correction of scanned Soil Health Card values.
  * *Rule*: Farmer soil classification is an observational heuristic and must **never** be used to fabricate laboratory N/P/K numbers.
* **Category E: Agronomic Knowledge & Expert Rules**
  * *Definition*: Published agronomic literature, ICAR/FAO technical bulletins, and multi-criteria suitability thresholds.
  * *Examples*: Optimal temperature and rainfall bands in `crop_agronomic_rules.json`, ICAR-AICRP targeted yield equations.

---

## 2. Dataset Feasibility & Availability Audit Table

Every candidate real-world dataset was audited for availability, accessibility, licensing, geographic/temporal alignment, and real-world join capability. **No dataset is assumed to be usable without verification.**

| Dataset | Official Source & Organization | Access Method & Status | License / Terms | Geographic Resolution | Time Resolution | Required Fields for V2 | Available Fields | Join Key | Estimated Usable Rows | Usable for V2 Training? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Soil Health Card (SHC)** | DA&FW, Ministry of Agriculture & Farmers Welfare ([soilhealth.dac.gov.in](https://soilhealth.dac.gov.in/)) | Web Dashboard table export (CSV/XLSX) via portal or [Dataful.in](https://dataful.in) / [IndiaDataPortal](https://indiadataportal.com). **ACCESSIBLE (Manual Export)** | Government Open Data License - India (GODL-India) / NDSAP | District & Block level aggregates (Cycles I, II, III) | Multi-year cycles (2015–17, 2017–19, 2023–26) | $N, P, K, pH$ ($kg/ha$ & pH scale) | $N, P, K, pH, OC, EC, S, Zn, Fe, Cu, Mn, B$ | `(State, District)` | ~700 Indian agricultural districts | ⚠️ **CONDITIONAL**: Provides authentic soil nutrient distributions, but lacks linked crop labels and climate data. Requires valid spatial-temporal linkage. |
| **UPAg District APY** | Directorate of Economics and Statistics (DES), MoA&FW ([upag.gov.in](https://upag.gov.in/)) | Portal reports export or REST API (`data.upag.gov.in`). **ACCESSIBLE (Export / Registered API)** | Open Government Data (OGD) Platform India | District level across all States | Annual & Seasonal (Kharif, Rabi, Summer, 1997–2024) | Ground-truth crop grown, season, year | `State`, `District`, `Crop`, `Season`, `Year`, `Area`, `Production`, `Yield` | `(State, District, Year, Season)` | >200,000 crop-district-season instances | ⚠️ **CONDITIONAL**: Ground-truth crop labels, but contains no soil nutrient measurements or daily rainfall. |
| **ICRISAT District Level Database (DLD)** | ICRISAT & Tata-Cornell Institute ([data.icrisat.org/dld](http://data.icrisat.org/dld/)) | Direct bulk download (Excel spreadsheets). **ACCESSIBLE** | Open Access for Research (Attribution Required) | 571 districts across 20 States | Annual & Monthly (1966–2015/16) | Historic climate, crop areas, soil type | `Rainfall` (annual/monthly), `Tmax`, `Tmin`, `Crop_Area`, `Production`, `Fertilizer_Use` | `(State, District, Year)` | 571 districts $\times$ 50 years | ⚠️ **CONDITIONAL / HISTORICAL**: Dataset terminates in 2015–16. Lacks lab soil test values ($N, P, K$ are fertilizer *application totals*, not available soil nutrients). |
| **IMD Gridded Meteorological Data** | India Meteorological Department, MoES ([cdsp.imdpune.gov.in](https://cdsp.imdpune.gov.in/)) | NetCDF download / `imdlib` Python utility. **ACCESSIBLE (Registration Required)** | Free for Academic / Scientific Research | $0.25^\circ \times 0.25^\circ$ (Rainfall), $1.0^\circ \times 1.0^\circ$ (Temp) | Daily (1901–Present) | Daily precipitation, $T_{max}$, $T_{min}$ | Gridded daily precipitation ($mm$), $T_{max}$, $T_{min}$ | `(Latitude, Longitude, Date)` | Continuous nationwide grid | ⚠️ **CONDITIONAL**: Excellent for aggregating exact seasonal rainfall, but must be paired with district polygons. |
| **Open-Meteo ERA5-Land** | ECMWF / Open-Meteo ([open-meteo.com](https://open-meteo.com/)) | Live REST API & Historical archive. **ACCESSIBLE & ACTIVE** | CC-BY 4.0 | $0.1^\circ \times 0.1^\circ$ (~$9\text{ km}$) | Hourly & Daily (1950–Present) | Seasonal rainfall sum ($mm$), Temp, Humidity | `precipitation_sum`, `temperature_2m`, `relative_humidity_2m` | `(Latitude, Longitude, Date_Range)` | Global continuous archive | ✅ **ACCESSIBLE & INTEGRATED**: Production baseline for seasonal rainfall and real-time conditions. |
| **ICAR-AICRP STCR** | ICAR - Indian Institute of Soil Science, Bhopal | Technical bulletins & Annual Reports. **UNAVAILABLE FOR BULK DOWNLOAD** | Copyright ICAR (Academic citation) | Multilocational research trials | Annual trial bulletins | Fertilizer equations & targeted yields | Ready reckoner coefficients ($a, b, c, d, e, f$) | Agro-Ecological Zone / Soil Series | Tabular bulletin equations only | ❌ **UNAVAILABLE AS TABULAR ML DATASET**: Contains agronomic equations, not tabular training rows. |
| **Kaggle Crop Recommendation** | Public Kaggle dataset (`atharvaingle/crop-recommendation-dataset`) | Public Download. **ACCESSIBLE** | CC0 Public Domain | ❌ None (No spatial metadata) | ❌ None (No dates/seasons) | N, P, K, pH, temp, humidity, rainfall, crop | 8 synthetic columns | ❌ Cannot be joined | 2,200 synthetic rows | ❌ **UNUSABLE FOR V2 TRAINING (OLD_BASELINE ONLY)**: Synthetic origin, misaligned rainfall (20–300 mm), zero real provenance. |

---

## 3. Dataset Feasibility Gate: Verdict & Next Steps

### Critical Finding:
> [!IMPORTANT]
> **No single monolithic real dataset exists in the public domain that natively couples soil laboratory measurements (N, P, K, pH), crop harvest records, and seasonal climate observations at the individual farm level.**

### Scientific Multi-Source Fusion Requirements:
A valid real-data training matrix can only be constructed if:
1. **Soil Layer**: Real district-level median laboratory values ($N, P, K, pH$) are exported from the Soil Health Card portal cycles (2015–2019).
2. **Crop Ground-Truth Layer**: Corresponding district crop production records for major crops ($>1,000\text{ ha}$) are extracted from UPAg / DES across matching agricultural years.
3. **Climate Layer**: Exact cumulative seasonal rainfall (June–Oct for Kharif, Nov–March for Rabi) and mean temperature/humidity are computed from IMD / ERA5-Land for the district polygon centroid.
4. **Feasibility Threshold**: The merged dataset must contain at least **5 major crop classes** with $\ge 150$ verified district-season instances per class without any synthetic row generation.

### Stop Gate Policy:
**The Google Colab notebook (`FarmFusion_Crop_Model_V2.ipynb`) will refuse to train any ML model if the raw files fail to satisfy this feasibility threshold.** We do NOT promise a trained V2 model until authentic real data has successfully cleared this gate.
