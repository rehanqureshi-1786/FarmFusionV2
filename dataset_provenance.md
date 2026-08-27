# FarmFusion Dataset Provenance & Model Audit

This document audits the datasets, knowledge bases, and machine learning assets utilized in the FarmFusion Crop Recommendation subsystem.

---

## 1. Existing ML Model Dataset Audit

- **Asset**: `backend/app/ml_models/crop_recommendation.joblib`
- **Metadata**: `backend/app/ml_models/crop_model_metadata.json`
- **Source**: Kaggle Crop Recommendation Dataset (`atharvaingle/crop-recommendation-dataset`, 2,200 rows, 22 crop classes, 100 observations per class).
- **Target Variable**: Categorical Crop Label (`apple`, `banana`, `blackgram`, `chickpea`, `coconut`, `coffee`, `cotton`, `grapes`, `jute`, `kidneybeans`, `lentil`, `maize`, `mango`, `mothbeans`, `mungbean`, `muskmelon`, `orange`, `papaya`, `pigeonpeas`, `pomegranate`, `rice`, `watermelon`).

### Critical Audit Findings & Limitations

1. **Synthetic Nature of Kaggle Labels**:
   - The 22 classes have equal sample sizes ($N=100$) and almost zero intra-class overlap, resulting in artificially high cross-validation test accuracy ($99.5\%$).
   - The labels represent **synthetic agronomic suitability envelopes** rather than actual historical harvest or yield data from Indian field trials.
2. **Rainfall Semantics Mismatch**:
   - In the Kaggle dataset, the `rainfall` column spans $20.21\text{ mm}$ to $298.56\text{ mm}$ (mean $\approx 103.46\text{ mm}$), representing seasonal or short growing-cycle moisture rather than complete annual precipitation.
   - Real annual rainfall in India (e.g. Udaipur, Rajasthan 2025: $941.5\text{ mm}$) exceeds the maximum training value ($298.56\text{ mm}$).
   - **Protection Implemented**: The system preserves the real annual rainfall value ($941.5\text{ mm}$) without clipping, and sets `rainfall_outside_training_distribution = true` with a calibration disclaimer on the ML path.
3. **N/P/K Feature Dependency**:
   - The model feature importance assigns $36.3\%$ of total weight directly to $N, P, K$ ($N: 12.8\%, K: 13.3\%, P: 10.2\%$).
   - When $N, P, K$ are missing, the ML model **MUST NOT** be invoked with fabricated or estimated values. Mode B completely bypasses this model.

---

## 2. Agronomic Knowledge Base Provenance (Mode B)

- **File**: `backend/app/data/crop_agronomic_rules.json`
- **Authoritative Sources**:
  1. **ICAR** (Indian Council of Agricultural Research) — *Handbook of Agriculture*, 6th Edition.
  2. **FAO** (Food and Agriculture Organization of the United Nations) — *Crop Water Requirements & Irrigation Guidelines* (Irrigation and Drainage Paper 56 & 33).
  3. **Department of Agriculture & Farmers Welfare**, Ministry of Agriculture & Farmers Welfare, Government of India.
  4. **State Agricultural Universities (SAUs)**:
     - Maharana Pratap University of Agriculture and Technology (MPUAT), Udaipur (Arid & Semi-arid zone recommendations).
     - Punjab Agricultural University (PAU), Ludhiana (Alluvial & Rabi crops).
     - Tamil Nadu Agricultural University (TNAU) Agritech Portal.

### Verification of Agronomic Criteria

Every crop definition includes:
- **Optimal & Tolerable Temperature Ranges**: Verified germination and vegetative stage thermal thresholds ($^\circ\text{C}$).
- **Annual Rainfall Viability & Optimal Windows**: Verified precipitation requirement ($400 - 1800\text{ mm}$).
- **Soil Type Compatibility**: Mapped to India's 4 major agricultural soil orders:
  - *Vertisols* (`Black Soil`)
  - *Inceptisols / Entisols* (`Alluvial Soil`)
  - *Alfisols* (`Red Soil`)
  - *Aridisols* (`Sandy Soil`)
- **Soil pH Compatibility**: Optimal and tolerable pH bounds ($5.0 - 8.5$).
- **Cropping Season**: Primary sowing window (`Kharif`, `Rabi`, `Zaid`).

---

## 3. External API Provenance

### Open-Meteo Weather API
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Provider**: Open-Meteo GmbH (Open-source weather data derived from national meteorological agencies: DWD ICON, NOAA GFS).
- **Parameters**: Current temperature ($2\text{m}$), relative humidity ($2\text{m}$), weather code.
- **Latency / Resilience**: $5\text{s}$ timeout, structured fallback to `UNAVAILABLE` without fabricated defaults.

### Open-Meteo ERA5-Land Historical Reanalysis
- **Endpoint**: `https://archive-api.open-meteo.com/v1/archive`
- **Provider**: ECMWF (European Centre for Medium-Range Weather Forecasts) ERA5-Land Reanalysis at $0.1^\circ$ spatial resolution.
- **Parameters**: Daily precipitation sum over the previous complete calendar year (e.g. 2025-01-01 to 2025-12-31).
- **Semantics**: True empirical annual rainfall ($\text{mm}$).

### SoilGrids (ISRIC — World Soil Information)
- **Endpoint**: `https://rest.isric.org/soilgrids/v2.0/properties/query`
- **Provider**: ISRIC — World Soil Information (Wageningen, Netherlands).
- **Depth Layer**: `0-5cm` (standard topsoil layer).
- **Properties Retrieved**:
  - `phhox` (pH in $H_2O \times 10$) $\rightarrow$ divided by $10.0$.
  - `sand`, `clay`, `silt` (mass fraction in $g/kg$) $\rightarrow$ divided by $10.0$ to get $\%$.
- **Semantics**: Mapped/interpolated global topsoil physics. Not a substitute for laboratory Soil Health Cards.

---

## 4. Production Retraining Requirements (V2 Roadmap)

For future production retraining of the crop recommendation ML model:

1. **Dataset Unification Standard**:
   - Merge state-level empirical data from **ICAR-AICRP** (All India Coordinated Research Projects) and **DAC&FW Agricoop** portals.
   - Require latitude, longitude, year, verified Soil Health Card ($N, P, K$ in $\text{kg/ha}$), and recorded crop yield ($\text{quintals/ha}$).
2. **Target Reformulation**:
   - Transition target from simple multiclass classification to **Multi-Output Yield and Profitability Prediction** conditioned on water availability.
3. **Out-of-Distribution (OOD) Protection**:
   - Implement Mahalanobis distance or Isolation Forest density filtering in the inference pipeline to reject inputs outside empirical feature bounds.
