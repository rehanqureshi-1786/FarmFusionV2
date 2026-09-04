"""
Train Real XGBoost Disaster Prediction Model on Genuine Indian Weather & Disaster Data
======================================================================================
Trains XGBoost (and voting ensemble) on 6,982 genuine historical Indian records:
- Real catastrophic floods (Mumbai, Kerala, Chennai, Assam, Yamuna)
- Real severe cyclones (Tauktae, Biparjoy, Amphan, Fani, Hudhud)
- Real intense droughts (Latur, Bundelkhand, Thar, Vidarbha)
- Multi-year real agricultural weather across 10 Indian states (Low Risk)
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, VotingClassifier
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

# Directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
CSV_PATH = os.path.join(BACKEND_DIR, "..", "ml_training", "real_indian_disaster_dataset.csv")
ARTIFACTS_DIR = os.path.join(BACKEND_DIR, "app", "ml", "disaster", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the 12 DisasterPredictorAI physical & interaction features."""
    df = df.copy()
    df['temp_humidity_index'] = df['temperature'] * (df['humidity'] / 100.0)
    df['rain_intensity'] = df['rainfall'] / (df['wind_speed'] + 1.0)
    df['pressure_anomaly'] = (df['pressure'] - 1013.25).abs()
    df['extreme_conditions'] = (
        (df['rainfall'] > 75.0).astype(int) +
        (df['wind_speed'] > 40.0).astype(int) +
        (df['humidity'] > 85.0).astype(int)
    )
    df['wind_rain_interaction'] = df['wind_speed'] * df['rainfall'] / 100.0
    df['heat_stress'] = df['temperature'] * (1.0 + df['humidity'] / 200.0)
    df['atmospheric_instability'] = (1013.25 - df['pressure']) * df['wind_speed'] / 100.0
    return df


def balance_dataset(df: pd.DataFrame, target_per_class: int = 1500) -> pd.DataFrame:
    """
    Balance dataset using realistic physical jitter around real historical events.
    Preserves exact meteorological correlations for the genuine disaster events.
    """
    dfs = []
    for label, group in df.groupby("label"):
        n_samples = len(group)
        if n_samples >= target_per_class:
            # Subsample Low Risk to prevent overwhelming the minority classes
            dfs.append(group.sample(n=target_per_class, random_state=42))
        else:
            # Upsample genuine historical disaster events with subtle physical Gaussian noise (±2-3%)
            dfs.append(group)
            needed = target_per_class - n_samples
            n_repeats = (needed // n_samples) + 1
            repeated = pd.concat([group] * n_repeats).iloc[:needed].copy()
            
            # Add small measurement jitter while respecting physical bounds
            repeated["temperature"] = (repeated["temperature"] + np.random.normal(0, 0.8, len(repeated))).clip(-5, 52)
            repeated["humidity"] = (repeated["humidity"] + np.random.normal(0, 1.5, len(repeated))).clip(5, 100)
            repeated["rainfall"] = (repeated["rainfall"] + np.random.normal(0, 2.5, len(repeated))).clip(lower=0)
            repeated["wind_speed"] = (repeated["wind_speed"] + np.random.normal(0, 1.8, len(repeated))).clip(lower=0)
            repeated["pressure"] = (repeated["pressure"] + np.random.normal(0, 1.2, len(repeated))).clip(890, 1050)
            dfs.append(repeated)
            
    balanced = pd.concat(dfs).sample(frac=1, random_state=42).reset_index(drop=True)
    return balanced


def main():
    print("=" * 70)
    print("TRAINING XGBOOST DISASTER MODEL ON REAL INDIAN DATA")
    print("=" * 70)

    # 1. Load Dataset
    print(f"\n[1/6] Loading dataset from {CSV_PATH}...")
    df_raw = pd.read_csv(CSV_PATH)
    print(f"✓ Loaded {len(df_raw)} records")
    print(df_raw["label"].value_counts())

    # 2. Balance classes
    print("\n[2/6] Balancing classes around real events...")
    df_balanced = balance_dataset(df_raw, target_per_class=1500)
    print("Balanced Class Distribution:")
    print(df_balanced["label"].value_counts())

    # 3. Feature Engineering
    print("\n[3/6] Engineering 12 meteorological & interaction features...")
    df_feat = compute_features(df_balanced)
    
    feature_columns = [
        "temperature", "humidity", "rainfall", "wind_speed", "pressure",
        "temp_humidity_index", "rain_intensity", "pressure_anomaly",
        "extreme_conditions", "wind_rain_interaction", "heat_stress",
        "atmospheric_instability"
    ]
    X = df_feat[feature_columns].values
    y_raw = df_feat["label"].values

    # 4. Encoding and Scaling
    print("\n[4/6] Encoding and standard scaling...")
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.20, random_state=42, stratify=y
    )

    # 5. Model Training (XGBoost + Ensemble)
    print("\n[5/6] Training XGBoost model...")
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric="mlogloss"
    )
    xgb_model.fit(X_train, y_train)

    xgb_preds = xgb_model.predict(X_test)
    xgb_acc = accuracy_score(y_test, xgb_preds)
    print(f"\n✓ XGBoost Test Accuracy: {xgb_acc * 100:.2f}%")
    print("\nXGBoost Classification Report:")
    print(classification_report(y_test, xgb_preds, target_names=label_encoder.classes_))

    # Also train other ensemble members
    print("Training supporting ensemble models...")
    rf_model = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
    rf_model.fit(X_train, y_train)

    gb_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, learning_rate=0.08, random_state=42)
    gb_model.fit(X_train, y_train)

    et_model = ExtraTreesClassifier(n_estimators=150, max_depth=8, random_state=42)
    et_model.fit(X_train, y_train)

    # Soft Voting Classifier
    ensemble = VotingClassifier(
        estimators=[
            ('rf', rf_model),
            ('gb', gb_model),
            ('et', et_model),
            ('xgb', xgb_model)
        ],
        voting='soft'
    )
    ensemble.fit(X_train, y_train)

    ens_preds = ensemble.predict(X_test)
    ens_acc = accuracy_score(y_test, ens_preds)
    print(f"\n✓ Full Ensemble Test Accuracy: {ens_acc * 100:.2f}%")

    # 6. Save Model Artifacts
    print(f"\n[6/6] Saving trained artifacts to {ARTIFACTS_DIR}...")
    joblib.dump(ensemble, os.path.join(ARTIFACTS_DIR, "disaster_model_ensemble.pkl"))
    joblib.dump(xgb_model, os.path.join(ARTIFACTS_DIR, "model_xgboost.pkl"))
    joblib.dump(rf_model, os.path.join(ARTIFACTS_DIR, "model_randomforest.pkl"))
    joblib.dump(gb_model, os.path.join(ARTIFACTS_DIR, "model_gradientboosting.pkl"))
    joblib.dump(et_model, os.path.join(ARTIFACTS_DIR, "model_extratrees.pkl"))
    joblib.dump(scaler, os.path.join(ARTIFACTS_DIR, "feature_scaler.pkl"))
    joblib.dump(label_encoder, os.path.join(ARTIFACTS_DIR, "label_encoder.pkl"))
    joblib.dump(feature_columns, os.path.join(ARTIFACTS_DIR, "feature_columns.pkl"))

    print("\nALL ARTIFACTS SAVED SUCCESSFULLY!")
    print("Classes:", list(label_encoder.classes_))


if __name__ == "__main__":
    main()
