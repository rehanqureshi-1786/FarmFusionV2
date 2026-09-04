"""
DisasterRiskPredictor - Authentic ML Inference Engine based on DisasterPredictorAI.
Combines 4-model soft voting ensemble with 12-feature thermodynamic/aerodynamic pipeline
and deterministic agronomic risk scoring.
"""

import os
import joblib
import pandas as pd
import numpy as np
import structlog
from typing import Dict, Any, List, Optional, Tuple

logger = structlog.get_logger(__name__)


class DisasterRiskPredictor:
    """
    Inference engine wrapping the DisasterPredictorAI multi-model soft voting ensemble.
    Ingests 5 core meteorological parameters, engineers 7 physical features,
    and returns continuous risk scores, probability distributions, traceable trigger factors,
    and agronomic precautions.
    """

    def __init__(self, model_dir: Optional[str] = None):
        if model_dir is None:
            artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
            if os.path.exists(artifacts_dir) and os.path.exists(os.path.join(artifacts_dir, "model_xgboost.pkl")):
                model_dir = artifacts_dir
            else:
                model_dir = os.path.dirname(os.path.abspath(__file__))

        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        try:
            model_path = os.path.join(self.model_dir, "disaster_model_ensemble.pkl")
            scaler_path = os.path.join(self.model_dir, "feature_scaler.pkl")
            encoder_path = os.path.join(self.model_dir, "label_encoder.pkl")
            features_path = os.path.join(self.model_dir, "feature_columns.pkl")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.label_encoder = joblib.load(encoder_path)
            self.feature_columns = joblib.load(features_path)

            xgb_path = os.path.join(self.model_dir, "model_xgboost.pkl")
            if os.path.exists(xgb_path):
                self.xgboost_model = joblib.load(xgb_path)
            else:
                self.xgboost_model = None

            logger.info(
                "disaster_predictor_artifacts_loaded",
                model_type=type(self.model).__name__,
                xgboost_loaded=self.xgboost_model is not None,
                classes=list(self.label_encoder.classes_),
                features_count=len(self.feature_columns)
            )
        except Exception as exc:
            logger.error("disaster_predictor_load_failed", error=str(exc))
            raise RuntimeError(f"Failed to load DisasterPredictorAI artifacts: {exc}") from exc

    def predict(
        self,
        temperature: float,
        humidity: float,
        rainfall: float,
        wind_speed: float,
        pressure: float,
        crop_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute full inference pipeline on meteorological parameters.
        
        Args:
            temperature: 2m air temperature (°C)
            humidity: Relative humidity (%)
            rainfall: 24h cumulative rainfall (mm)
            wind_speed: 10m wind speed (km/h)
            pressure: Atmospheric pressure at MSL (hPa)
            crop_name: Optional farmer crop name for localized advice
            
        Returns:
            Dict containing disaster_type, risk_level, risk_score, probability,
            confidence (0.0 - 1.0), all class probabilities, trigger factors, and recommendations.
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("DisasterPredictorAI models are not loaded.")

        # 1. Base input dictionary
        base_features = {
            "temperature": float(temperature),
            "humidity": float(humidity),
            "rainfall": float(rainfall),
            "wind_speed": float(wind_speed),
            "pressure": float(pressure),
        }

        # 2. Advanced Feature Engineering (Exact DisasterPredictorAI formula match)
        base_features["temp_humidity_index"] = base_features["temperature"] * (base_features["humidity"] / 100.0)
        base_features["rain_intensity"] = base_features["rainfall"] / (base_features["wind_speed"] + 1.0)
        base_features["pressure_anomaly"] = abs(base_features["pressure"] - 1013.25)
        base_features["extreme_conditions"] = (
            (1 if base_features["rainfall"] > 80.0 else 0) +
            (1 if base_features["wind_speed"] > 40.0 else 0) +
            (1 if base_features["humidity"] > 85.0 else 0)
        )
        base_features["wind_rain_interaction"] = base_features["wind_speed"] * base_features["rainfall"] / 100.0
        base_features["heat_stress"] = base_features["temperature"] * (1.0 + base_features["humidity"] / 200.0)
        base_features["atmospheric_instability"] = (1013.25 - base_features["pressure"]) * base_features["wind_speed"] / 100.0

        # 3. Align features with trained order
        df = pd.DataFrame([base_features])
        X = df[self.feature_columns]

        # 4. Standard Scaling & Model Inference
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)[0]
        pred_idx = self.model.predict(X_scaled)[0]
        label = self.label_encoder.inverse_transform([pred_idx])[0]

        # 5. Extract probabilities for all classes
        class_probs: Dict[str, float] = {}
        for idx, cls_name in enumerate(self.label_encoder.classes_):
            class_probs[cls_name] = round(float(proba[idx]), 4)

        max_confidence = float(np.max(proba))
        primary_prob = class_probs.get(label, max_confidence)

        # Physical Grounding and Plausibility Gates:
        # In DisasterPredictorAI's dataset, Flood Risk rainfall is [50.2mm - 205.7mm].
        # In real-world Indian monsoon conditions, relative humidity (75-90%) with normal precipitation (<35mm)
        # is regular agricultural weather, NOT a flood catastrophe.
        if "Flood" in label and rainfall < 35.0:
            label = "Low Risk"
        elif "Cyclone" in label and wind_speed < 35.0:
            label = "Flood Risk" if rainfall >= 60.0 else "Low Risk"
        elif "Drought" in label and (rainfall > 15.0 or humidity > 60.0):
            label = "Low Risk"

        # 6. Continuous Risk Score Calculation
        if label == "Low Risk":
            base_risk = 10.0 + (class_probs.get("Low Risk", 0.8) * 15.0)  # 10 - 25
        elif "Flood" in label:
            if rainfall < 50.0:
                base_risk = 35.0 + ((rainfall - 35.0) / 15.0) * 15.0  # 35 - 50 (MEDIUM)
            elif rainfall < 80.0:
                base_risk = 55.0 + ((rainfall - 50.0) / 30.0) * 20.0  # 55 - 75 (HIGH)
            else:
                base_risk = 75.0 + (primary_prob * 20.0)  # 75 - 95 (CRITICAL)
        elif "Cyclone" in label:
            base_risk = 65.0 + (primary_prob * 30.0)  # 65 - 95
        elif "Drought" in label:
            if temperature > 38.0 and rainfall < 5.0:
                base_risk = 50.0 + (primary_prob * 30.0)
            else:
                base_risk = 30.0 + (primary_prob * 20.0)
        else:
            base_risk = 40.0

        # Add secondary risk contribution if secondary probability > 0.20
        sorted_probs = sorted(class_probs.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_probs) > 1 and sorted_probs[1][0] != "Low Risk" and sorted_probs[1][1] > 0.20 and label != "Low Risk":
            base_risk += sorted_probs[1][1] * 15.0

        # Weather-based risk adjustments
        weather_risk = 0.0
        # Rainfall increments
        if rainfall > 80.0:
            weather_risk += 25.0
        elif rainfall > 60.0:
            weather_risk += 18.0
        elif rainfall > 50.0:
            weather_risk += 12.0
        elif rainfall > 35.0 and label != "Low Risk":
            weather_risk += 6.0

        # Wind speed increments
        if wind_speed > 40.0:
            weather_risk += 25.0
        elif wind_speed > 30.0:
            weather_risk += 18.0
        elif wind_speed > 20.0 and label != "Low Risk":
            weather_risk += 10.0

        # Temperature increments
        if temperature > 42.0:
            weather_risk += 20.0
        elif temperature > 38.0:
            weather_risk += 12.0
        elif temperature > 35.0 and "Drought" in label:
            weather_risk += 6.0
        elif temperature < -5.0:
            weather_risk += 15.0
        elif temperature < 0.0:
            weather_risk += 10.0

        # Pressure increments
        if pressure < 965.0:
            weather_risk += 20.0
        elif pressure < 980.0:
            weather_risk += 15.0
        elif pressure < 995.0 and label != "Low Risk":
            weather_risk += 8.0

        # Humidity increments
        if humidity > 92.0 and rainfall >= 50.0:
            weather_risk += 10.0
        elif humidity < 25.0 and temperature > 35.0:
            weather_risk += 8.0

        # Pleasant weather reduction
        if (rainfall < 40.0 and 20.0 < temperature < 32.0 and 
            wind_speed < 20.0):
            weather_risk = max(0.0, weather_risk - 10.0)

        # Dynamic confidence multiplier
        confidence_multiplier = 0.85 + (max_confidence * 0.30)
        total_risk = (base_risk + weather_risk) * confidence_multiplier
        risk_score = round(min(max(total_risk, 0.0), 100.0), 1)

        # Enforce domain minimums and caps
        if "Flood" in label:
            if rainfall < 50.0:
                risk_score = min(risk_score, 50.0)
            else:
                risk_score = max(risk_score, 55.0)
        elif "Cyclone" in label:
            if wind_speed < 40.0:
                risk_score = min(risk_score, 50.0)
            else:
                risk_score = max(risk_score, 60.0)
        elif "Drought" in label:
            if temperature < 35.0 or rainfall > 10.0:
                risk_score = min(risk_score, 40.0)
            else:
                risk_score = max(risk_score, 45.0)
        elif "Low Risk" in label:
            risk_score = min(risk_score, 35.0)

        # 7. Deterministic Risk Level Categorization
        if risk_score >= 90.0 or (risk_score >= 80.0 and base_features["extreme_conditions"] >= 2):
            risk_level = "CRITICAL"
        elif risk_score >= 75.0:
            risk_level = "HIGH"
        elif risk_score >= 40.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # 8. Traceable Trigger Factors (Derived directly from actual inputs)
        trigger_factors: List[str] = []
        if rainfall >= 80.0:
            trigger_factors.append(f"Extreme 24-hour precipitation ({rainfall:.1f} mm)")
        elif rainfall >= 50.0:
            trigger_factors.append(f"Heavy 24-hour precipitation ({rainfall:.1f} mm)")
        elif rainfall >= 35.0 and "Flood" in label:
            trigger_factors.append(f"Moderate 24-hour precipitation ({rainfall:.1f} mm)")
        elif rainfall < 5.0 and temperature >= 38.0:
            trigger_factors.append(f"Prolonged moisture deficit ({rainfall:.1f} mm rain)")

        if wind_speed >= 40.0:
            trigger_factors.append(f"Severe gale wind gusts ({wind_speed:.1f} km/h)")
        elif wind_speed >= 25.0:
            trigger_factors.append(f"Elevated sustained wind speed ({wind_speed:.1f} km/h)")

        if pressure <= 995.0:
            trigger_factors.append(f"Deep cyclonic atmospheric depression ({pressure:.1f} hPa)")
        elif pressure <= 1000.0 and (wind_speed >= 25.0 or rainfall >= 50.0):
            trigger_factors.append(f"Sub-normal atmospheric pressure ({pressure:.1f} hPa)")

        if humidity >= 90.0 and rainfall >= 50.0:
            trigger_factors.append(f"Atmospheric humidity saturation ({humidity:.0f}%) with heavy rain")
        elif humidity <= 20.0 and temperature >= 38.0:
            trigger_factors.append(f"Critical atmospheric dryness ({humidity:.0f}% RH)")

        if temperature >= 40.0:
            trigger_factors.append(f"Heatwave thermal stress ({temperature:.1f}°C)")

        if not trigger_factors:
            trigger_factors.append(
                f"Moderate conditions: {temperature:.1f}°C, {humidity:.0f}% RH, {wind_speed:.1f} km/h wind"
            )

        # 9. Traceable Farm Recommendations
        recommendations = self._generate_recommendations(label, risk_level, crop_name)

        # Normalized confidence: 0.0 - 1.0 float (Original DisasterPredictorAI scaled percentage / 100)
        normalized_confidence = round(max_confidence, 4)
        normalized_probability = round(primary_prob, 4)

        # Raw XGBoost inference result
        xgboost_result = {}
        if getattr(self, "xgboost_model", None) is not None:
            try:
                xgb_pred_idx = self.xgboost_model.predict(X_scaled)[0]
                xgb_probs = self.xgboost_model.predict_proba(X_scaled)[0]
                xgboost_result = {
                    "predicted_label": str(self.label_encoder.inverse_transform([xgb_pred_idx])[0]),
                    "confidence": round(float(np.max(xgb_probs)), 4),
                    "probabilities": {
                        cls_name: round(float(xgb_probs[idx]), 4)
                        for idx, cls_name in enumerate(self.label_encoder.classes_)
                    }
                }
            except Exception as exc:
                logger.warning("xgboost_inference_failed", error=str(exc))

        return {
            "disaster_type": label,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "probability": normalized_probability,
            "confidence": normalized_confidence,
            "prediction_horizon": "24-48 hours",
            "trigger_factors": trigger_factors,
            "recommendations": recommendations,
            "probabilities": class_probs,
            "xgboost": xgboost_result,
            "input_metrics": {
                "temperature_c": temperature,
                "humidity_percent": humidity,
                "rainfall_mm": rainfall,
                "wind_speed_kmh": wind_speed,
                "pressure_hpa": pressure,
            }
        }

    def _generate_recommendations(
        self, disaster_type: str, risk_level: str, crop_name: Optional[str]
    ) -> List[str]:
        crop_prefix = f"For {crop_name}: " if crop_name else ""

        if "Flood" in disaster_type:
            if risk_level in ["HIGH", "CRITICAL"]:
                return [
                    f"{crop_prefix}Clear and deepen farm drainage channels to discharge excess water.",
                    "Relocate all mobile diesel engines, electric pump sets, and livestock to higher ground.",
                    "Immediately suspend scheduled irrigation and foliar fertilizer/pesticide spraying.",
                    "Inspect field bunds to prevent soil erosion and water stagnation in root zones."
                ]
            else:
                return [
                    f"{crop_prefix}Ensure field furrows and drainage outlets are free of weed debris.",
                    "Hold off on fresh fertilizer top-dressing until heavy rain clears.",
                    "Monitor low-lying farm sections for signs of water accumulation."
                ]

        elif "Cyclone" in disaster_type:
            if risk_level in ["HIGH", "CRITICAL"]:
                return [
                    f"{crop_prefix}Provide mechanical staking/support to tall crops (sugarcane, banana, papaya).",
                    "Firmly secure or dismantle polyhouse plastic covers and nursery shade netting.",
                    "Avoid entering fields or working near high-tension electrical lines during wind gusts.",
                    "Store harvested grains in waterproof godowns or under tied tarpaulins."
                ]
            else:
                return [
                    f"{crop_prefix}Check greenhouse and polyhouse anchor ropes for tightness.",
                    "Delay spray operations due to severe droplet drift from gusty winds.",
                    "Keep emergency farm drainage and pruning tools ready."
                ]

        elif "Drought" in disaster_type:
            return [
                f"{crop_prefix}Apply straw, sugarcane trash, or plastic mulch to conserve soil moisture.",
                "Schedule micro-irrigation (drip or sprinkler) strictly during early morning or night.",
                "Avoid nitrogenous fertilizer top-dressing to prevent thermal crop scorching.",
                "Protect farm livestock from heat stress with shaded resting sheds and fresh water."
            ]

        else:
            return [
                f"{crop_prefix}Atmospheric risk is low; proceed with standard agronomic schedule.",
                "Maintain routine field weed management and soil health checks.",
                "Continue standard irrigation scheduling as per crop growth stage."
            ]


# Singleton instance for application runtime
disaster_predictor = DisasterRiskPredictor()
