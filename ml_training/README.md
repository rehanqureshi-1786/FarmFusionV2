# FarmFusion ML Training Infrastructure (Google Colab Workflow)

This directory contains the training pipeline for **FarmFusion Crop Recommendation Model V2**.

## 1. Laptop Resource Constraint
All heavy machine learning operations (data ingestion, multi-source joins, hyperparameter optimization, training, cross-validation, probability calibration, and evaluation) **MUST be executed on Google Colab**. The local developer machine is dedicated exclusively to FastAPI backend services, Android compilation, and inference execution.

---

## 2. Directory Layout
```
ml_training/
├── README.md                              # Operational Guide & Colab instructions
├── dataset_provenance_v2.md               # Scientific provenance, feature semantics & join feasibility
├── notebooks/
│   └── FarmFusion_Crop_Model_V2.ipynb     # Master Google Colab training & evaluation notebook
└── data/                                  # Local placeholder directory (gitignored raw/processed data)
    ├── raw/
    └── processed/
```

---

## 3. How to Run on Google Colab

1. **Open in Colab**:
   * Navigate to [Google Colab](https://colab.research.google.com/).
   * Upload `ml_training/notebooks/FarmFusion_Crop_Model_V2.ipynb` or open it directly from your GitHub repository.

2. **Configure Environment Secrets (Optional)**:
   * If accessing private data buckets or authenticated endpoints (e.g. UPAg API), set the corresponding credentials in Colab's **Secrets** panel (`🔑`).
   * Never hardcode API keys or credentials directly in notebook cells.

3. **Execute Notebook Sections**:
   * **Section A (Environment)**: Installs required packages (`xgboost`, `lightgbm`, `catboost`, `scikit-learn`, `joblib`, etc.).
   * **Section B & C (Data Ingestion & Raw Preservation)**: Ingests real datasets from authoritative sources and preserves pristine copies in `data/raw/`.
   * **Section D & E (Validation & Feasibility Join)**: Runs strict schema checks. If missing real data or invalid joins are detected, execution **halts immediately**.
   * **Section F & G (Feature Engineering & Splitting)**: Computes seasonal rainfall and partitions data using spatial (state-level) and temporal holdouts to prevent leakage.
   * **Section H (Model Benchmarking)**: Evaluates XGBoost, LightGBM, CatBoost, and Random Forest using Macro-F1, balanced accuracy, top-3 accuracy, and per-class recall.
   * **Section I (Calibration & OOD Analysis)**: Calculates ECE/Brier score, performs probability calibration, and extracts Out-Of-Distribution (OOD) boundaries.
   * **Section J (Model Export)**: Generates production artifacts:
     - `models/crop_model_v2.joblib`
     - `models/crop_label_encoder_v2.joblib`
     - `models/crop_model_v2_calibrator.joblib`
     - `models/crop_model_v2_metadata.json`

4. **Deploying Artifacts to Local Backend**:
   * Download the generated `models/` directory from Google Colab.
   * Place the files into:
     ```
     backend/app/ml_models/
     ```
   * Ensure `crop_model_v2_metadata.json` is present. The backend `CropMLService` will verify the V2 artifacts before loading.
