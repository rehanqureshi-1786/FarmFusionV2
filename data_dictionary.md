# FarmFusion Agricultural Data Dictionary

This document defines the exact scientific semantics, measurement units, collection methods, authoritative sources, and valid operational ranges for every agricultural parameter used across FarmFusion.

---

## 1. Soil Parameters

| Parameter | Symbol / Key | Unit | Standard Definition | Measurement Method / Depth | Source / Provider | Valid Physical Range | Agronomic Normal Range (India) |
|---|---|---|---|---|---|---|---|
| **Available Nitrogen** | `N` | $\text{kg/ha}$ | Alkaline permanganate oxidizable Nitrogen available for plant uptake | Lab Soil Test (Subbiah & Asija method, 0–15 cm) | Laboratory Soil Health Card (SHC) / Farmer OCR | $0 - 500\text{ kg/ha}$ | Low: $<280$, Medium: $280-560$, High: $>560$ |
| **Available Phosphorus** | `P` | $\text{kg/ha}$ | Plant-available orthophosphate ($P_2O_5$) | Olsen extraction (neutral/alkaline) or Bray's (acidic) (0–15 cm) | Laboratory Soil Health Card (SHC) / Farmer OCR | $0 - 250\text{ kg/ha}$ | Low: $<10$, Medium: $10-25$, High: $>25$ |
| **Available Potassium** | `K` | $\text{kg/ha}$ | Neutral normal ammonium acetate extractable potassium ($K_2O$) | Flame Photometer ($1\text{N NH}_4\text{OAc}$, 0–15 cm) | Laboratory Soil Health Card (SHC) / Farmer OCR | $0 - 500\text{ kg/ha}$ | Low: $<108$, Medium: $108-280$, High: $>280$ |
| **Soil Reaction (pH)** | `ph` | $-\log[H^+]$ | Measure of soil acidity or alkalinity in 1:2.5 soil-water suspension | Potentiometric glass electrode pH meter (0–15 cm or 0–5 cm) | SoilGrids (ISRIC) or Lab Soil Health Card | $3.0 - 10.5$ | Acidic: $<6.5$, Neutral: $6.5-7.5$, Alkaline: $>7.5$ |
| **Sand Fraction** | `sand` | $\%$ ($\text{w/w}$) | Mineral particles with diameter $0.05 - 2.0\text{ mm}$ | Laser diffraction / Hydrometer (depth: 0–5 cm) | SoilGrids (ISRIC) | $0 - 100\%$ | Texture dependent |
| **Clay Fraction** | `clay` | $\%$ ($\text{w/w}$) | Mineral particles with diameter $<0.002\text{ mm}$ | Laser diffraction / Pipette (depth: 0–5 cm) | SoilGrids (ISRIC) | $0 - 100\%$ | Texture dependent |
| **Silt Fraction** | `silt` | $\%$ ($\text{w/w}$) | Mineral particles with diameter $0.002 - 0.05\text{ mm}$ | Laser diffraction / Pipette (depth: 0–5 cm) | SoilGrids (ISRIC) | $0 - 100\%$ | Texture dependent |
| **Farmer Soil Class** | `soil_type` | Categorical | Farmer-selected major soil grouping | Visual & tactile physical appraisal | Farmer Selection | `Sandy Soil`, `Black Soil`, `Red Soil`, `Alluvial Soil` | N/A |

> [!IMPORTANT]
> **SoilGrids Semantics Distinction**:
> SoilGrids provides modelled organic Nitrogen ($cg/kg$), pH ($pH \times 10$), and texture fractions from global spatial interpolation models. It **DOES NOT** provide plant-available $N, P, K$ in $\text{kg/ha}$. Therefore, in FarmFusion, SoilGrids data is strictly labeled `Source: SoilGrids (ISRIC) • MAPPED` and is never converted to fake fertilizer recommendations.

---

## 2. Weather & Climate Parameters

| Parameter | Symbol / Key | Unit | Standard Definition | Temporal Resolution / Semantics | Source / Provider | Valid Physical Range | Typical Operational Range |
|---|---|---|---|---|---|---|---|
| **Air Temperature** | `temperature` / `temperature_c` | $^\circ\text{C}$ | Dry bulb ambient air temperature at 2 meters above ground | Current instantaneous observation | Open-Meteo API | $-10.0 - 55.0^\circ\text{C}$ | $10.0 - 45.0^\circ\text{C}$ |
| **Relative Humidity** | `humidity` / `humidity_percent` | $\%$ | Ratio of actual vapor pressure to saturation vapor pressure at current air temperature | Current instantaneous observation | Open-Meteo API | $0.0 - 100.0\%$ | $10.0 - 100.0\%$ |
| **Annual Rainfall** | `annual_rainfall` / `rainfall_mm` | $\text{mm}$ | Total cumulative precipitation over a complete calendar year | Annual historical aggregation (previous complete calendar year, e.g. 2025) | Open-Meteo ERA5-Land Reanalysis | $0.0 - 5000.0\text{ mm}$ | $200.0 - 2500.0\text{ mm}$ (India) |
| **Agricultural Season** | `season` | Categorical | Primary cropping season in Indian agro-climatic zones | Temporal calendar window (`Kharif`: Jun–Oct, `Rabi`: Nov–Mar, `Zaid`: Apr–May) | FarmFusion Season Engine | `Kharif`, `Rabi`, `Zaid` | N/A |

---

## 3. Location & Geography Parameters

| Parameter | Symbol / Key | Unit | Standard Definition | Source / Provider | Valid Range |
|---|---|---|---|---|---|
| **Latitude** | `latitude` | Decimal degrees | Geodetic latitude (WGS84 ellipsoid) | Device GPS / Location Services | $-90.0^\circ \text{ to } +90.0^\circ$ (India: $6.0^\circ - 38.0^\circ$) |
| **Longitude** | `longitude` | Decimal degrees | Geodetic longitude (WGS84 ellipsoid) | Device GPS / Location Services | $-180.0^\circ \text{ to } +180.0^\circ$ (India: $68.0^\circ - 98.0^\circ$) |
| **Location Name** | `location_name` / `display_name` | String | Reverse-geocoded place identifier (Village, District, State, Country) | Android Geocoder / OpenStreetMap Nominatim | Descriptive text string |

---

## 4. Derived & Engineered ML Features

These features are calculated strictly for the Mode A (Soil Report) Machine Learning model:

| Feature Name | Formulation | Agronomic Rationale |
|---|---|---|
| `NPK_sum` | $N + P + K$ | Represents total macronutrient soil fertility reserve |
| `N_to_P_ratio` | $\frac{N}{P + 1.0}$ | Captures nitrogen-phosphorus balance critical for vegetative vs root development |
| `temp_humidity_interaction` | $\frac{\text{temperature} \times \text{humidity}}{100.0}$ | Measures thermal-humidity index (heat stress and disease pressure indicator) |

---

## 5. Provenance & Integrity Status Vocabulary

Every field exposed to the farmer or internal agents carries one of the following statuses:

- `REAL`: Measured directly from an external physical sensor, device GPS, or real-time atmospheric API (e.g. Open-Meteo).
- `USER_PROVIDED`: Entered, confirmed, or corrected directly by the farmer (e.g. OCR confirmation, soil type selection).
- `MAPPED`: Spatially modeled data from geospatial databases (e.g. SoilGrids ISRIC).
- `DERIVED`: Mathematically computed from verified parameters (e.g. seasonal window, feature interaction).
- `UNAVAILABLE`: Data is physically absent or requires an unperformed measurement (e.g. N/P/K without a lab soil report). **Value is strictly `null`**.
