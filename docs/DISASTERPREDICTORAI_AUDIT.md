# DisasterPredictorAI Technical Audit

**Audit Date**: September 4, 2026  
**Source Repository**: [DisasterPredictorAI (GitHub)](https://github.com/rehanqureshi-1786/DisasterPredictorAI)  
**Auditor**: FarmFusion Architecture Team  
**Scope**: Complete technical inspection of model, feature engineering, prediction pipeline, API contracts, risk calculation, and alerting for integration into FarmFusion.

---

## 1. Executive Summary

`DisasterPredictorAI` is a machine-learning disaster risk prediction system designed to forecast localized climate hazards (**Flood Risk**, **Cyclone Risk**, **Drought Risk**, and **Low Risk**) by combining 5 atmospheric weather parameters with 7 non-linear engineered physical features. 

The production model is a **Soft Voting Ensemble (`VotingClassifier`)** combining 4 distinct supervised classifiers (Random Forest, Gradient Boosting, Extra Trees, and XGBoost) achieving **99.92% accuracy** across 6,000 statistical disaster event records.

---

## 2. Model Architecture & Artifacts

### 2.1 Model Types & Versions
- **Primary Production Model**: `disaster_model_ensemble.pkl`
  - Scikit-Learn `VotingClassifier(voting='soft')`
  - Combines 4 ensemble members:
    1. **Random Forest**: `RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=5, min_samples_leaf=2)` (Test Acc: 99.92%, 5-fold CV: 99.96%)
    2. **Gradient Boosting**: `GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, max_depth=7)` (Test Acc: 99.83%, 5-fold CV: 99.96%)
    3. **Extra Trees**: `ExtraTreesClassifier(n_estimators=200, max_depth=20, min_samples_split=5)` (Test Acc: 99.83%, 5-fold CV: 100.0%)
    4. **XGBoost**: `XGBClassifier(n_estimators=150, learning_rate=0.1, max_depth=7, eval_metric='mlogloss')` (Test Acc: 99.83%, 5-fold CV: 99.96%)
  - **Ensemble Performance**: **99.92% Test Accuracy**, **100.0% 5-Fold Cross-Validation**.
- **Fallback / Standalone Models**:
  - `model_randomforest.pkl`
  - `model_gradientboosting.pkl`
  - `model_extratrees.pkl`
  - `model_xgboost.pkl`
- **Trained Artifacts**:
  - `feature_scaler.pkl`: Scikit-Learn `StandardScaler` fitted on 12 features.
  - `label_encoder.pkl`: Scikit-Learn `LabelEncoder` with classes:
    ```python
    ['Cyclone Risk', 'Drought Risk', 'Flood Risk', 'Low Risk']
    ```
  - `feature_columns.pkl`: List of 12 input features in strict sequential order.

### 2.2 Training Dataset
- **File**: `data/real_disaster_dataset.csv`
- **Total Records**: 6,000 samples (4,800 train, 1,200 validation)
- **Class Distribution**:
  - `Low Risk`: 1,750 (29.2%)
  - `Flood Risk`: 1,500 (25.0%)
  - `Drought Risk`: 1,500 (25.0%)
  - `Cyclone Risk`: 1,250 (20.8%)

---

## 3. Features & Preprocessing Pipeline

The model ingests 5 core physical weather measurements and computes 7 non-linear thermodynamic/aerodynamic interaction terms:

| # | Feature Name | Type | Source / Formula | Unit |
|---|---|---|---|---|
| 1 | `temperature` | Raw | NWP 2-meter air temperature | °C |
| 2 | `humidity` | Raw | Relative humidity | % |
| 3 | `rainfall` | Raw | 24-hour cumulative precipitation | mm |
| 4 | `wind_speed` | Raw | Maximum 10-meter wind speed | km/h |
| 5 | `pressure` | Raw | Mean sea level atmospheric pressure | hPa |
| 6 | `temp_humidity_index` | Engineered | `temperature * (humidity / 100)` | Index |
| 7 | `rain_intensity` | Engineered | `rainfall / (wind_speed + 1)` | mm/(km/h) |
| 8 | `pressure_anomaly` | Engineered | `abs(pressure - 1013.25)` | hPa |
| 9 | `extreme_conditions` | Engineered | `(rainfall > 80) + (wind_speed > 40) + (humidity > 85)` | Count (0-3) |
| 10 | `wind_rain_interaction` | Engineered | `(wind_speed * rainfall) / 100` | Interaction |
| 11 | `heat_stress` | Engineered | `temperature * (1 + humidity / 200)` | Index |
| 12 | `atmospheric_instability` | Engineered | `((1013.25 - pressure) * wind_speed) / 100` | Instability |

### 3.1 Preprocessing
1. Construct Pandas DataFrame with all 12 columns in the exact order specified in `feature_columns.pkl`.
2. Apply standard scaling via `scaler.transform(X)`.
3. Predict soft class probabilities via `model.predict_proba(X_scaled)[0]`.

---

## 4. Supported Disaster Types & Time Horizon

1. **Flood Risk**: Triggered by intense rainfall (`>80 mm`), high humidity (`>85%`), and saturated conditions.
2. **Cyclone Risk**: Triggered by high sustained wind speeds (`>40 km/h`), severe low pressure (`<995 hPa`), and coastal proximity.
3. **Drought Risk**: Triggered by persistent high temperature (`>38°C`), near-zero rainfall (`<5 mm`), and low humidity (`<30%`).
4. **Low Risk**: Normal meteorological operating ranges with no imminent agricultural threats.

**Prediction Time Horizon**: **24 to 48 hours** based on 24-hour aggregated precipitation and 48-hour NWP forecast windows.

---

## 5. Risk Calculation & Thresholds

The system calculates a continuous `risk_score` (0 to 100) combining the model's posterior probability with physical threshold adjustments:

```python
# 1. Base Risk from primary predicted class
if label == "Low Risk":
    base_risk = 15 + (primary_prob * 10)       # 15 - 25
elif "Flood" in label:
    base_risk = 60 + (primary_prob * 30)       # 60 - 90
elif "Cyclone" in label:
    base_risk = 65 + (primary_prob * 30)       # 65 - 95
elif "Drought" in label:
    base_risk = 50 + (primary_prob * 30) if temp > 38 else 30 + (primary_prob * 20)

# 2. Weather adjustments (rainfall up to +25, wind up to +25, temp up to +20, pressure up to +20)
# 3. Dynamic confidence multiplier: 0.85 + (max_confidence * 0.30)
# 4. Total Risk: total_risk = (base_risk + weather_risk) * confidence_multiplier (clamped 0 - 100)
```

### Risk Level Categorization (Frontend)
- **Low Risk**: `risk_score < 40`
- **Moderate / Medium Risk**: `40 <= risk_score < 75`
- **High Risk**: `risk_score >= 75`
- **Critical Risk**: `risk_score >= 90` or (`risk_score >= 80` with extreme condition flags)

---

## 6. Original DisasterPredictorAI Endpoints

### 6.1 `POST /predict` (Location-driven)

**Request**:
```json
{
  "city": "Jaipur",
  "lat": 26.9124,
  "lon": 75.7873,
  "phone": "+919876543210",
  "email": "farmer@farmfusion.in"
}
```

**Response**:
```json
{
  "city": "Jaipur",
  "district": "Jaipur",
  "state": "Rajasthan",
  "temperature": 32.4,
  "humidity": 65.0,
  "rainfall": 12.0,
  "wind_speed": 14.5,
  "pressure": 1008.2,
  "prediction": "Low Risk",
  "risk_score": 28.5,
  "alert_sent": false,
  "alert_message": "Alert not sent",
  "alert_phone": null
}
```

### 6.2 `POST /predict-direct` (Raw Meteorological Inputs)

**Request**:
```json
{
  "location": "Kota Farm #3",
  "temperature": 27.5,
  "humidity": 92.0,
  "rainfall": 115.0,
  "wind_speed": 28.0,
  "pressure": 992.0
}
```

**Response**:
```json
{
  "location": "Kota Farm #3",
  "temperature": 27.5,
  "humidity": 92.0,
  "rainfall": 115.0,
  "wind_speed": 28.0,
  "pressure": 992.0,
  "prediction": "Flood Risk",
  "risk_score": 88.5,
  "confidence": 99.2,
  "all_probabilities": {
    "Cyclone Risk": 0.5,
    "Drought Risk": 0.1,
    "Flood Risk": 99.2,
    "Low Risk": 0.2
  }
}
```

### 6.3 Original Alert System
- In `alert_service.py`, alerts were sent via **Twilio SMS / WhatsApp**.
- Trigger criteria:
  - `risk_score >= 70`: "🚨 HIGH RISK ALERT"
  - `risk_score >= 50`: "⚠️ MODERATE RISK"
  - `risk_score < 50`: "ℹ️ LOW RISK"
- **FarmFusion Requirement**: Discard Twilio. Integrate with FarmFusion's existing **Vobiz Outbound Calling Agent** asynchronously for `HIGH` and `CRITICAL` risk tiers.

---

## 7. Next Steps for FarmFusion Phase G

1. **PHASE 2**: Document exact current API/request/response behavior.
2. **PHASE 3**: Propose FarmFusion `POST /api/v1/weather/disaster-risk` endpoint contract, normalized for Indian agriculture.
