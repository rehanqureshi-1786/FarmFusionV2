# FarmFusion Crop Disease Detection Model V1 — Google Colab Training

This directory contains the training pipeline, dataset audits, configurations, and export scripts for the **FarmFusion Crop Disease Detection Model V1** (`EfficientNet-B3`).

---

## 1. Quick Colab Training Guide

1. Open **Google Colab** ([colab.research.google.com](https://colab.research.google.com/)).
2. Upload the notebook:
   ```
   ml_training/disease_detection/notebooks/FarmFusion_Disease_Model_V1.ipynb
   ```
3. Set Colab Runtime to **GPU** (`Runtime` $\rightarrow$ `Change runtime type` $\rightarrow$ `T4 GPU`).
4. Run all cells sequentially:
   - **Section 1**: Installs PyTorch, timm, albumentations, scikit-learn.
   - **Section 2**: Downloads and unzips PlantVillage, PlantDoc, and Cotton datasets.
   - **Section 3**: Audits class distribution, resolution, and corrupt images.
   - **Section 4**: Performs stratified 70/15/15 train/val/test splits.
   - **Section 5**: Trains EfficientNet-B3 (frozen backbone warmup $\rightarrow$ full fine-tuning).
   - **Section 6**: Evaluates accuracy, Macro F1, top-3 accuracy, confusion matrix.
   - **Section 7**: Computes temperature scaling and Expected Calibration Error (ECE).
   - **Section 8**: Exports `disease_model_v1.pth`, `disease_label_mapping.json`, and metadata.
5. Download the exported artifacts and place them in:
   ```
   backend/app/ml_models/disease_model_v1.pth
   backend/app/ml_models/disease_label_mapping.json
   ```

---

## 2. Directory Structure

```
ml_training/disease_detection/
├── README.md                          # Colab execution guide (this file)
├── dataset_provenance.md              # Dataset audit & Kamal-Shirupa analysis
├── configs/
│   └── disease_classes.json           # 36 canonical crop disease class list
├── notebooks/
│   └── FarmFusion_Disease_Model_V1.ipynb # Master Colab training notebook
└── models/                            # Local directory for exported PyTorch weights
```

---

## 3. Architecture & Safety Specs

* **Architecture**: EfficientNet-B3 (ImageNet-1k pretrained weights).
* **Input Resolution**: 300 × 300 × 3 RGB.
* **Loss Function**: Label-smoothed CrossEntropyLoss ($\epsilon = 0.1$).
* **Optimizer**: AdamW ($\text{lr} = 1\text{e-}4$, weight decay = $1\text{e-}2$).
* **Confidence Tiers**:
  * $\ge 0.75$: `HIGH` (Confident identification).
  * $0.45 - 0.74$: `MEDIUM` (Possible disease, advisory flag).
  * $0.30 - 0.44$: `LOW` (Uncertain, chemical advice suppressed).
  * $< 0.30$: `UNCLEAR` (Poor quality / OOD rejection).
