"""
FarmFusion Crop Recommendation Model V2 Training Pipeline (57K Dataset).

Trains a high-capacity multi-class XGBoost model across 57 Indian crops using the 57,000-row
agro-ecological dataset (`external/AgriAdvisor-AI/datasets/Crop_recommendation_dataset.csv`).

Key Highlights:
1. Grounded in authentic SAU/ICAR agronomic response envelopes.
2. Direct mapping of `WATERREQUIRED` to seasonal water requirement (in mm).
3. Exact 10-feature production contract:
   [N, P, K, temperature, humidity, ph, rainfall, NPK_sum, N_to_P_ratio, temp_humidity_interaction]
4. Stratified 70/15/15 Train/Val/Test partitioning.
5. Probability calibration using validation fold.
6. Non-destructive export to `backend/app/ml_models/crop/v2/`.
7. Metadata explicitly documents:
   "stcr_data_used": false
   "synthetic_stcr_data_used": false
"""
import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
try:
    from sklearn.frozen import FrozenEstimator
except ImportError:
    FrozenEstimator = None
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    top_k_accuracy_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "external" / "AgriAdvisor-AI" / "datasets" / "Crop_recommendation_dataset.csv"
EXPORT_DIR = ROOT_DIR / "backend" / "app" / "ml_models" / "crop" / "v2"

PRODUCTION_FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
    "NPK_sum",
    "N_to_P_ratio",
    "temp_humidity_interaction",
]

FEATURE_UNITS = {
    "N": "kg/ha (plant-available soil nitrogen)",
    "P": "kg/ha (plant-available soil phosphorus)",
    "K": "kg/ha (plant-available soil potassium)",
    "temperature": "degree_celsius (seasonal growing temperature)",
    "humidity": "percent (relative humidity)",
    "ph": "soil_pH (0-14 scale)",
    "rainfall": "mm_seasonal (cumulative seasonal crop water requirement)",
    "NPK_sum": "kg/ha (engineered sum: N + P + K)",
    "N_to_P_ratio": "ratio (engineered: N / (P + 1e-6))",
    "temp_humidity_interaction": "index (engineered: temp * humidity / 100)",
}

CANONICAL_CROP_MAPPING = {
    "rice": "Rice",
    "wheat": "Wheat",
    "maize": "Maize",
    "sorghum": "Sorghum (Jowar)",
    "Pearl millet": "Pearl Millet (Bajra)",
    "ragi": "Finger Millet (Ragi)",
    "bengalgram": "Chickpea (Gram)",
    "redgram": "Pigeonpea (Arhar/Tur)",
    "blackgram": "Blackgram (Urad)",
    "greengram": "Mungbean (Moong)",
    "groundnut": "Groundnut (Peanut)",
    "soyabean": "Soybean",
    "cotton": "Cotton",
    "sugarcane": "Sugarcane",
    "jute": "Jute",
    "onion": "Onion",
    "small onion": "Small Onion (Shallots)",
    "tomato": "Tomato",
    "watermelon": "Watermelon",
    "muskmelon": "Muskmelon",
    # Additional legitimate Indian crops from 57K dataset
    "samai": "Little Millet (Samai)",
    "thinai": "Foxtail Millet (Thinai)",
    "varagu": "Kodo Millet (Varagu)",
    "kudiraivali": "Barnyard Millet (Kudiraivali)",
    "panivaragu": "Proso Millet (Panivaragu)",
    "cowpea": "Cowpea (Lobia)",
    "horsegram": "Horsegram (Kollu)",
    "french bean": "French Bean",
    "peas": "Green Peas (Matar)",
    "sunflower": "Sunflower",
    "gingely": "Sesame (Gingelly/Til)",
    "castor": "Castor",
    "chillies": "Chilli (Mirch)",
    "bhendi": "Okra (Bhendi)",
    "brinjal": "Brinjal (Eggplant/Baingan)",
    "capsicum": "Capsicum (Bell Pepper)",
    "cabbage": "Cabbage (Patta Gobhi)",
    "cauliflower": "Cauliflower (Phool Gobhi)",
    "carrot": "Carrot (Gajar)",
    "beetroot": "Beetroot (Chukandar)",
    "radish": "Radish (Mooli)",
    "cucumber": "Cucumber (Kheera)",
    "pumpkin": "Pumpkin (Kaddu)",
    "bottle gourd": "Bottle Gourd (Lauki)",
    "bitter gourd": "Bitter Gourd (Karela)",
    "snake gourd": "Snake Gourd (Chichinda)",
    "ash gourd": "Ash Gourd (Petha)",
    "ribbed gourd": "Ridge Gourd (Torai)",
    "tinda": "Apple Gourd (Tinda)",
    "chowchow": "Chayote (Chow Chow)",
    "cluster bean": "Cluster Bean (Guar)",
    "vegetable cowpea": "Vegetable Cowpea",
    "annual moringa": "Drumstick (Moringa)",
    "sweet potato": "Sweet Potato (Shakarkand)",
    "tapoica": "Tapioca (Cassava)",
    "elephant foot yam": "Elephant Foot Yam (Suran/Jimikand)",
    "sugarbeet": "Sugarbeet",
}


def load_and_preprocess_57k(dataset_path: Path = DATASET_PATH) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Loads 57k dataset, applies canonical names, and engineers standard 10 features."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"57K dataset not found at '{dataset_path}'")

    raw_df = pd.read_csv(dataset_path)

    # Feature transformation
    feat_df = pd.DataFrame()
    feat_df["N"] = raw_df["N"].astype(float)
    feat_df["P"] = raw_df["P"].astype(float)
    feat_df["K"] = raw_df["K"].astype(float)
    feat_df["temperature"] = raw_df["TEMP"].astype(float)
    feat_df["humidity"] = raw_df["RELATIVE_HUMIDITY"].astype(float)
    feat_df["ph"] = raw_df["SOIL_PH"].astype(float)
    feat_df["rainfall"] = raw_df["WATERREQUIRED"].astype(float)

    # Engineered Interaction Features
    feat_df["NPK_sum"] = feat_df["N"] + feat_df["P"] + feat_df["K"]
    feat_df["N_to_P_ratio"] = feat_df["N"] / (feat_df["P"] + 1e-6)
    feat_df["temp_humidity_interaction"] = feat_df["temperature"] * feat_df["humidity"] / 100.0

    # Target class canonicalization
    raw_crops = raw_df["CROPS"].astype(str).str.strip()
    feat_df["crop"] = raw_crops.map(CANONICAL_CROP_MAPPING).fillna(raw_crops.str.title())
    feat_df["soil"] = raw_df["SOIL"].astype(str).str.strip()
    feat_df["season"] = raw_df["SEASON"].astype(str).str.strip()

    return feat_df, raw_df


def train_and_export_v2_model():
    """Execution function for training Model V2."""
    print("=" * 90)
    print("FARMFUSION CROP RECOMMENDATION MODEL V2 — MASTER TRAINING PIPELINE")
    print("=" * 90)
    
    logger.info("Loading 57K dataset from: %s", DATASET_PATH.resolve())
    feat_df, raw_df = load_and_preprocess_57k()

    # Pre-Training Safety Checks
    print("\n--- PHASE 4: PRE-TRAINING SAFETY VERIFICATION ---")
    print(f"Dataset Path:       {DATASET_PATH.resolve()}")
    print(f"Total Rows:         {len(feat_df)}")
    print(f"Total Raw Columns:  {raw_df.shape[1]}")
    print(f"Total Nulls:        {feat_df.isnull().sum().sum()}")
    print(f"Total Duplicates:   {raw_df.duplicated().sum()}")
    
    X = feat_df[PRODUCTION_FEATURES]
    y_raw = feat_df["crop"]

    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    class_names = list(le.classes_)

    print(f"Classes Count:      {len(class_names)}")
    print(f"Feature Columns:    {list(X.columns)}")
    print(f"Feature Dimensions: {X.shape[1]}")

    # Stratified 70/15/15 Split
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=(0.15 / 0.85), random_state=42, stratify=y_train_val
    )

    print(f"Train Count:        {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"Validation Count:   {len(X_val)} ({len(X_val)/len(X)*100:.1f}%)")
    print(f"Test Count:         {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")

    # Safety Assertions
    assert len(feat_df) == 57000, f"Expected 57,000 rows, got {len(feat_df)}"
    assert len(class_names) == 57, f"Expected 57 classes, got {len(class_names)}"
    assert len(X_train) == 39900, f"Expected 39,900 train samples, got {len(X_train)}"
    assert len(X_val) == 8550, f"Expected 8,550 val samples, got {len(X_val)}"
    assert len(X_test) == 8550, f"Expected 8,550 test samples, got {len(X_test)}"
    assert X.shape[1] == 10, f"Expected 10 features, got {X.shape[1]}"
    assert feat_df.isnull().sum().sum() == 0, "Null values detected in feature matrix"
    assert raw_df.duplicated().sum() == 0, "Duplicate rows detected in raw dataset"
    print("✅ All Pre-Training Safety Assertions Passed Successfully!")

    # Model Training: High-Performance XGBoost
    print("\n--- PHASE 5: MODEL TRAINING & PROBABILITY CALIBRATION ---")
    xgb_params = {
        "n_estimators": 350,
        "max_depth": 6,
        "learning_rate": 0.08,
        "subsample": 0.85,
        "colsample_bytree": 0.85,
        "objective": "multi:softprob",
        "eval_metric": "mlogloss",
        "random_state": 42,
        "n_jobs": -1,
    }
    print(f"Training XGBClassifier with params: {xgb_params}")
    base_model = xgb.XGBClassifier(**xgb_params)
    base_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    print("✅ XGBoost base model fitting complete.")

    # Probability Calibration on Validation Fold
    logger.info("Calibrating multi-class probabilities on validation fold...")
    if FrozenEstimator is not None:
        calibrator = CalibratedClassifierCV(estimator=FrozenEstimator(base_model), method="sigmoid")
    else:
        calibrator = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv="prefit")
    calibrator.fit(X_val, y_val)
    print("✅ Probability calibration complete.")

    # Evaluation on Held-Out Test Set
    print("\n--- PHASE 6: HELD-OUT TEST EVALUATION ---")
    y_pred = base_model.predict(X_test)
    y_proba = base_model.predict_proba(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    bal_acc = float(balanced_accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro"))
    weighted_f1 = float(f1_score(y_test, y_pred, average="weighted"))
    top3_acc = float(top_k_accuracy_score(y_test, y_proba, k=min(3, len(class_names))))
    top5_acc = float(top_k_accuracy_score(y_test, y_proba, k=min(5, len(class_names))))

    print(f"  Test Accuracy:          {acc:.4f} ({acc*100:.2f}%)")
    print(f"  Test Balanced Accuracy: {bal_acc:.4f} ({bal_acc*100:.2f}%)")
    print(f"  Test Macro F1:          {macro_f1:.4f}")
    print(f"  Test Weighted F1:       {weighted_f1:.4f}")
    print(f"  Test Top-3 Accuracy:    {top3_acc:.4f} ({top3_acc*100:.2f}%)")
    print(f"  Test Top-5 Accuracy:    {top5_acc:.4f} ({top5_acc*100:.2f}%)")

    # Empirical OOD Bounds (Computed strictly from Training set)
    ood_bounds = {}
    for col in PRODUCTION_FEATURES:
        vals = X_train[col].astype(float)
        ood_bounds[col] = {
            "min": float(round(np.min(vals), 2)),
            "max": float(round(np.max(vals), 2)),
            "p01": float(round(np.percentile(vals, 1), 2)),
            "p99": float(round(np.percentile(vals, 99), 2)),
            "mean": float(round(np.mean(vals), 2)),
            "std": float(round(np.std(vals), 2)),
        }

    # Export Artifacts
    print("\n--- PHASE 7: EXPORTING ARTIFACTS ---")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    model_file = EXPORT_DIR / "crop_recommendation_v2.joblib"
    encoder_file = EXPORT_DIR / "crop_label_encoder_v2.joblib"
    calibrator_file = EXPORT_DIR / "crop_model_v2_calibrator.joblib"
    meta_file = EXPORT_DIR / "crop_model_metadata_v2.json"

    joblib.dump(base_model, model_file)
    joblib.dump(le, encoder_file)
    joblib.dump(calibrator, calibrator_file)

    metadata = {
        "model_name": "FarmFusion Crop Recommendation Model V2",
        "architecture": "XGBClassifier (Gradient Boosted Decision Trees)",
        "version": "2.0.0-57k-production",
        "training_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "random_seed": 42,
        "stcr_data_used": False,
        "synthetic_stcr_data_used": False,
        "dataset_name": "AgriAdvisor Indian Agro-Ecological Crop Recommendation Dataset (57k rows)",
        "dataset_total_samples": len(feat_df),
        "train_samples": len(X_train),
        "validation_samples": len(X_val),
        "test_samples": len(X_test),
        "n_classes": len(class_names),
        "classes": class_names,
        "n_features": len(PRODUCTION_FEATURES),
        "feature_names": PRODUCTION_FEATURES,
        "feature_units": FEATURE_UNITS,
        "hyperparameters": xgb_params,
        "test_metrics": {
            "accuracy": round(acc, 4),
            "balanced_accuracy": round(bal_acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "top_3_accuracy": round(top3_acc, 4),
            "top_5_accuracy": round(top5_acc, 4),
        },
        "ood_distribution_bounds": ood_bounds,
        "provenance_statement": (
            "STCR experimental microdata was not used because it was not available. "
            "Model V2 is trained on the verified 57k Indian agro-ecological dataset derived from SAU/ICAR crop recommendation guidelines."
        ),
    }

    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Saved Model:      {model_file}")
    print(f"✅ Saved Encoder:    {encoder_file}")
    print(f"✅ Saved Calibrator: {calibrator_file}")
    print(f"✅ Saved Metadata:   {meta_file}")
    print("=" * 90)
    return metadata


if __name__ == "__main__":
    train_and_export_v2_model()
