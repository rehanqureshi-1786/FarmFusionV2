import json
from pathlib import Path

def create_38class_notebook():
    cells = []

    def add_md(source_text):
        lines = [line + "\n" for line in source_text.strip().split("\n")]
        if lines:
            lines[-1] = lines[-1].rstrip("\n")
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": lines
        })

    def add_code(source_text):
        lines = [line + "\n" for line in source_text.strip().split("\n")]
        if lines:
            lines[-1] = lines[-1].rstrip("\n")
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": lines
        })

    # Header
    add_md("""# 🌱 FarmFusion Crop Disease Detection Model V2 (38-Class EfficientNet-B3)

**Project**: FarmFusion Multilingual AI Agricultural Copilot  
**Model**: EfficientNet-B3 Transfer Learning with Mixed Precision (AMP) & Probability Calibration  
**Dataset**: Full PlantVillage Dataset (~54,300 images across 38 crop & disease classes)  
**Target Hardware**: Google Colab GPU (NVIDIA Tesla T4 16GB)  
**Output Target**: `/content/exported_models_38/`  
**Safety Rules**: Pre-flight verification, stratified 80/10/10 split, confidence tiering, no hallucinated classes.

---""")

    # 1. Environment Setup
    add_md("## 1. Environment Setup & Tesla T4 GPU Verification")
    add_code("""!pip install -q timm torchvision torch scikit-learn matplotlib seaborn pandas numpy Pillow tqdm joblib

import os
import sys
import json
import time
import copy
import shutil
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast, GradScaler
import torchvision.transforms as transforms
import timm

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, f1_score,
    precision_score, recall_score, top_k_accuracy_score,
    confusion_matrix, classification_report
)

# Set seed for strict reproducibility
RANDOM_SEED = 42
torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)
    torch.backends.cudnn.deterministic = True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("=== RUNTIME DIAGNOSTIC ===")
print(f"Python:       {sys.version.split()[0]}")
print(f"PyTorch:      {torch.__version__}")
print(f"Timm:         {timm.__version__}")
print(f"Device:       {device}")
if device.type == "cuda":
    print(f"GPU:          {torch.cuda.get_device_name(0)}")
    print(f"Memory:       {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
print("==========================")""")

    # 2. Dataset Acquisition
    add_md("""## 2. Dataset Acquisition & 38-Class Dataset Verification

If the full 38-class dataset (~54k images) is not already present at `/content/data_38`, download it via Kaggle.
*(The 15-class subset at `/content/data/PlantVillage` is preserved and not used here)*.""")
    
    add_code("""# Optional download block for full 38-class PlantVillage dataset
# !pip install -q kaggle
# !mkdir -p /content/data_38
# !kaggle datasets download -d abdallahalidev/plantvillage-dataset -p /content/data_38 --unzip
print("If dataset is already downloaded at /content/data_38 or ./data_38, proceed to locator below.")""")

    # 3. Dynamic 38-Class Dataset Locator & Audit
    add_md("## 3. Dynamic 38-Class Dataset Locator & Pre-Flight Dataset Audit")
    add_code("""def find_38class_dataset() -> Optional[Path]:
    \"\"\"Locate directory containing the full 38-class PlantVillage dataset.\"\"\"
    candidates = [
        Path("/content/data_38/plantvillage dataset/color"),
        Path("/content/data_38/plantvillage dataset/segmented"),
        Path("/content/data_38/PlantVillage"),
        Path("/content/data_38"),
        Path("./data_38/plantvillage dataset/color"),
        Path("./data_38/PlantVillage"),
        Path("./data_38"),
        Path("/content/plantvillage_full"),
        Path("/content/data/plantvillage_full")
    ]
    for p in candidates:
        if p.exists() and p.is_dir():
            subdirs = [d for d in p.iterdir() if d.is_dir()]
            # Full PlantVillage has ~38 classes including Apple, Grape, Corn, Orange, Peach, etc.
            if len(subdirs) >= 30 and any("Apple" in d.name for d in subdirs):
                return p

    # Recursive search under /content and current directory
    for root_scan in [Path("/content"), Path(".")]:
        if root_scan.exists():
            for dirpath, dirnames, _ in os.walk(root_scan):
                if len(dirnames) >= 30 and any("Apple" in d for d in dirnames) and any("Grape" in d for d in dirnames):
                    return Path(dirpath)
    return None

DATA_DIR_38 = find_38class_dataset()

if DATA_DIR_38 is None:
    print("=" * 65)
    print("❌ FULL 38-CLASS PLANTVILLAGE DATASET NOT FOUND")
    print("=" * 65)
    print("The currently active dataset at /content/data/PlantVillage contains ONLY 15 classes (20,638 images).")
    print("\\nTo download the full 38-class PlantVillage dataset (~54,300 images), run:")
    print("!kaggle datasets download -d abdallahalidev/plantvillage-dataset -p /content/data_38 --unzip")
    print("=" * 65)
    raise FileNotFoundError("Full 38-class dataset not found. Stopping to prevent training on 15-class subset.")

print(f"✓ 38-Class Dataset Located: {DATA_DIR_38.resolve()}")

# Audit classes and image counts
class_dirs = sorted([d for d in DATA_DIR_38.iterdir() if d.is_dir()])
class_names = [d.name for d in class_dirs]
num_classes = len(class_names)

print(f"Number of class folders: {num_classes}")

audit_records = []
all_samples = []
corrupt_count = 0

for class_idx, class_dir in enumerate(tqdm(class_dirs, desc="Auditing 38 Classes")):
    cls_name = class_dir.name
    files = [f for f in class_dir.iterdir() if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    valid_count = 0

    for f in files:
        try:
            with Image.open(f) as img:
                img.verify()
                valid_count += 1
                all_samples.append((str(f), class_idx))
        except Exception:
            corrupt_count += 1

    audit_records.append({
        "Class Index": class_idx,
        "Class Name": cls_name,
        "Valid Images": valid_count
    })

audit_df = pd.DataFrame(audit_records)
total_images = audit_df["Valid Images"].sum()

print("\\n" + "=" * 65)
print("38-CLASS DATASET AUDIT COMPLETE")
print("=" * 65)
print(f"Dataset Path:       {DATA_DIR_38.resolve()}")
print(f"Number of Classes:  {num_classes}")
print(f"Total Valid Images: {total_images}")
print(f"Corrupt Images:     {corrupt_count}")
print("=" * 65)

display(audit_df)""")

    # 4. Stratified Split
    add_md("## 4. Reproducible Stratified Dataset Splitting (80% Train / 10% Val / 10% Test)")
    add_code("""# Stratified 80/10/10 Split with seed 42
all_labels = [s[1] for s in all_samples]

train_samples, temp_samples, train_labels, temp_labels = train_test_split(
    all_samples,
    all_labels,
    test_size=0.20,
    random_state=RANDOM_SEED,
    stratify=all_labels
)

val_samples, test_samples, val_labels, test_labels = train_test_split(
    temp_samples,
    temp_labels,
    test_size=0.50,
    random_state=RANDOM_SEED,
    stratify=temp_labels
)

# Overlap Assertions
train_paths = set(s[0] for s in train_samples)
val_paths = set(s[0] for s in val_samples)
test_paths = set(s[0] for s in test_samples)

assert len(train_paths.intersection(val_paths)) == 0, "Overlap in Train and Val!"
assert len(train_paths.intersection(test_paths)) == 0, "Overlap in Train and Test!"
assert len(val_paths.intersection(test_paths)) == 0, "Overlap in Val and Test!"
assert len(train_samples) + len(val_samples) + len(test_samples) == len(all_samples)

print(f"--- STRATIFIED SPLIT SUMMARY (38 Classes) ---")
print(f"Total Samples: {len(all_samples)}")
print(f"Train Count:   {len(train_samples)} ({len(train_samples)/len(all_samples)*100:.1f}%)")
print(f"Val Count:     {len(val_samples)} ({len(val_samples)/len(all_samples)*100:.1f}%)")
print(f"Test Count:    {len(test_samples)} ({len(test_samples)/len(all_samples)*100:.1f}%)")""")

    # 5. Transforms & DataLoaders
    add_md("## 5. EfficientNet-B3 Preprocessing & DataLoaders (300×300)")
    add_code("""IMG_SIZE = 300
BATCH_SIZE = 32
NUM_WORKERS = 2

train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

val_test_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

class SampleListDataset(Dataset):
    def __init__(self, samples: List[Tuple[str, int]], transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        path, label = self.samples[idx]
        with Image.open(path) as img:
            image = img.convert("RGB")
        if self.transform is not None:
            image = self.transform(image)
        return image, label

train_dataset = SampleListDataset(train_samples, transform=train_transform)
val_dataset = SampleListDataset(val_samples, transform=val_test_transform)
test_dataset = SampleListDataset(test_samples, transform=val_test_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True if torch.cuda.is_available() else False)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True if torch.cuda.is_available() else False)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True if torch.cuda.is_available() else False)

print(f"DataLoaders constructed:")
print(f" - Train Batches: {len(train_loader)} ({len(train_dataset)} samples)")
print(f" - Val Batches:   {len(val_loader)} ({len(val_dataset)} samples)")
print(f" - Test Batches:  {len(test_loader)} ({len(test_dataset)} samples)")""")

    # 6. Pre-flight Check
    add_md("## 6. Pre-Flight Diagnostic Check")
    add_code("""# Pre-flight single batch verification
sample_imgs, sample_lbls = next(iter(train_loader))
sample_imgs, sample_lbls = sample_imgs.to(device), sample_lbls.to(device)

OUTPUT_DIR = Path("/content/exported_models_38")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("=== PRE-FLIGHT CHECK ===")
print(f"DATASET:              PlantVillage 38-Class")
print(f"CLASSES:              {num_classes}")
print(f"TOTAL IMAGES:         {len(all_samples)}")
print(f"GPU:                  {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
print(f"AVAILABLE GPU MEMORY: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB" if torch.cuda.is_available() else "N/A")
print(f"OUTPUT DIRECTORY:     {OUTPUT_DIR.resolve()}")
print("=" * 60)
print("38-CLASS TRAINING READY")
print("=" * 60)""")

    # 7. Model Architecture & Loss
    add_md("## 7. Model Architecture, Class Weights & Mixed Precision Setup")
    add_code("""def create_38class_model(num_classes: int = 38, pretrained: bool = True) -> nn.Module:
    \"\"\"Build EfficientNet-B3 classification model for 38 classes.\"\"\"
    model = timm.create_model("efficientnet_b3", pretrained=pretrained, num_classes=num_classes)
    return model

# Calculate balanced class weights for 38 classes
train_labels_arr = np.array(train_labels)
computed_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.arange(num_classes),
    y=train_labels_arr
)
class_weights_tensor = torch.tensor(computed_weights, dtype=torch.float).to(device)
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
scaler = GradScaler()  # For AMP Mixed Precision training on Tesla T4""")

    # 8. Full Training Loop
    add_md("## 8. Full Training Loop with Mixed Precision (AMP) & Early Stopping\n\nTrains for ~15 epochs with early stopping on validation Macro F1.")
    add_code("""model = create_38class_model(num_classes=num_classes, pretrained=True).to(device)

optimizer = optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-2)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="max",
    factor=0.5,
    patience=2
)

NUM_EPOCHS = 15
EARLY_STOPPING_PATIENCE = 4

best_model_wts = copy.deepcopy(model.state_dict())
best_val_macro_f1 = 0.0
best_epoch = 0
epochs_no_improve = 0

history = {
    "train_loss": [], "train_acc": [],
    "val_loss": [], "val_acc": [], "val_balanced_acc": [],
    "val_macro_f1": [], "val_weighted_f1": [], "lr": []
}

print(f"Starting 38-Class Training: {NUM_EPOCHS} Epochs with Mixed Precision on {device}...")

for epoch in range(NUM_EPOCHS):
    epoch_start = time.time()
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in tqdm(train_loader, desc=f"Epoch {epoch+1:02d}/{NUM_EPOCHS:02d} [Train]"):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        # Mixed precision forward pass
        with autocast():
            outputs = model(inputs)
            loss = criterion(outputs, labels)

        if torch.isnan(loss):
            raise ValueError(f"NaN loss at epoch {epoch+1}")

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        running_loss += loss.item() * inputs.size(0)
        preds = torch.argmax(outputs, dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    train_loss = running_loss / total
    train_acc = correct / total

    # Validation Phase
    model.eval()
    val_loss = 0.0
    val_preds = []
    val_targets = []

    with torch.no_grad():
        for inputs, labels in tqdm(val_loader, desc=f"Epoch {epoch+1:02d}/{NUM_EPOCHS:02d} [Val]"):
            inputs, labels = inputs.to(device), labels.to(device)
            with autocast():
                outputs = model(inputs)
                loss = criterion(outputs, labels)
            val_loss += loss.item() * inputs.size(0)
            preds = torch.argmax(outputs, dim=1)
            val_preds.extend(preds.cpu().numpy())
            val_targets.extend(labels.cpu().numpy())

    val_loss = val_loss / len(val_dataset)
    val_acc = accuracy_score(val_targets, val_preds)
    val_bal_acc = balanced_accuracy_score(val_targets, val_preds)
    val_macro_f1 = f1_score(val_targets, val_preds, average="macro")
    val_weighted_f1 = f1_score(val_targets, val_preds, average="weighted")

    current_lr = optimizer.param_groups[0]["lr"]
    scheduler.step(val_macro_f1)

    history["train_loss"].append(train_loss)
    history["train_acc"].append(train_acc)
    history["val_loss"].append(val_loss)
    history["val_acc"].append(val_acc)
    history["val_balanced_acc"].append(val_bal_acc)
    history["val_macro_f1"].append(val_macro_f1)
    history["val_weighted_f1"].append(val_weighted_f1)
    history["lr"].append(current_lr)

    epoch_time = time.time() - epoch_start
    print(
        f"Epoch {epoch+1:02d}/{NUM_EPOCHS:02d} ({epoch_time:.1f}s) | "
        f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
        f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}% BalAcc: {val_bal_acc*100:.2f}% MacroF1: {val_macro_f1:.4f} | "
        f"LR: {current_lr:.6f}"
    )

    if val_macro_f1 > best_val_macro_f1:
        best_val_macro_f1 = val_macro_f1
        best_epoch = epoch + 1
        best_model_wts = copy.deepcopy(model.state_dict())
        epochs_no_improve = 0
        print(f"  ★ New best 38-class checkpoint saved! (Val Macro F1: {best_val_macro_f1:.4f})")
    else:
        epochs_no_improve += 1
        print(f"  No improvement for {epochs_no_improve}/{EARLY_STOPPING_PATIENCE} epochs.")
        if epochs_no_improve >= EARLY_STOPPING_PATIENCE:
            print(f"Early stopping at epoch {epoch+1}. Restoring best weights from epoch {best_epoch}.")
            break

model.load_state_dict(best_model_wts)
print(f"\\nTraining complete. Best checkpoint was Epoch {best_epoch} with Val Macro F1: {best_val_macro_f1:.4f}")""")

    # 9. Test Evaluation
    add_md("## 9. Untouched Test Set Evaluation (38 Classes)")
    add_code("""import matplotlib.pyplot as plt
import seaborn as sns

model.eval()
test_preds = []
test_targets = []
test_probs = []

with torch.no_grad():
    for inputs, labels in tqdm(test_loader, desc="Testing"):
        inputs, labels = inputs.to(device), labels.to(device)
        with autocast():
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1)

        test_probs.extend(probs.cpu().numpy())
        test_preds.extend(preds.cpu().numpy())
        test_targets.extend(labels.cpu().numpy())

test_preds_arr = np.array(test_preds)
test_targets_arr = np.array(test_targets)
test_probs_arr = np.array(test_probs)

test_acc = accuracy_score(test_targets_arr, test_preds_arr)
test_bal_acc = balanced_accuracy_score(test_targets_arr, test_preds_arr)
test_macro_f1 = f1_score(test_targets_arr, test_preds_arr, average="macro")
test_weighted_f1 = f1_score(test_targets_arr, test_preds_arr, average="weighted")
test_top3_acc = top_k_accuracy_score(test_targets_arr, test_probs_arr, k=min(3, num_classes))

report_text = classification_report(test_targets_arr, test_preds_arr, target_names=class_names)
cm = confusion_matrix(test_targets_arr, test_preds_arr)

print("========================================")
print("   38-CLASS UNTOUCHED TEST SET METRICS  ")
print("========================================")
print(f"Accuracy:          {test_acc*100:.2f}%")
print(f"Balanced Accuracy: {test_bal_acc*100:.2f}%")
print(f"Macro F1:          {test_macro_f1:.4f}")
print(f"Weighted F1:       {test_weighted_f1:.4f}")
print(f"Top-3 Accuracy:    {test_top3_acc*100:.2f}%")
print("----------------------------------------")
print("\\nPer-Class Classification Report:\\n")
print(report_text)""")

    # 10. Confidence Calibration & Safety Tiers
    add_md("## 10. Probability Calibration & FarmFusion Safety Tiers")
    add_code("""# Expected Calibration Error (ECE) & Brier Score
confidences = np.max(test_probs_arr, axis=1)
predictions = np.argmax(test_probs_arr, axis=1)
accuracies = (predictions == test_targets_arr)

n_bins = 10
bin_boundaries = np.linspace(0, 1, n_bins + 1)
ece = 0.0
for i in range(n_bins):
    in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
    prop = np.mean(in_bin)
    if prop > 0:
        ece += np.abs(np.mean(confidences[in_bin]) - np.mean(accuracies[in_bin])) * prop

one_hot = np.zeros_like(test_probs_arr)
for i, t in enumerate(test_targets_arr):
    one_hot[i, t] = 1.0
brier = np.mean(np.sum((test_probs_arr - one_hot)**2, axis=1))

# FarmFusion Safety Confidence Tier Breakdown
tier_high = np.sum(confidences >= 0.75)
tier_med = np.sum((confidences >= 0.45) & (confidences < 0.75))
tier_low = np.sum((confidences >= 0.30) & (confidences < 0.45))
tier_unclear = np.sum(confidences < 0.30)
tot = len(confidences)

print("=== 38-CLASS CALIBRATION & SAFETY METRICS ===")
print(f"Brier Score:                {brier:.4f}")
print(f"Expected Calibration Error: {ece:.4f}")
print(f"\\nFarmFusion Confidence Tier Distribution:")
print(f"  - HIGH    (>= 0.75):   {tier_high:5d} ({tier_high/tot*100:.1f}%)")
print(f"  - MEDIUM  (0.45-0.74): {tier_med:5d} ({tier_med/tot*100:.1f}%)")
print(f"  - LOW     (0.30-0.44): {tier_low:5d} ({tier_low/tot*100:.1f}%)")
print(f"  - UNCLEAR (< 0.30):    {tier_unclear:5d} ({tier_unclear/tot*100:.1f}%)")
print("=============================================")""")

    # 11. Artifact Export
    add_md("## 11. Export Production Artifacts to `/content/exported_models_38/`")
    add_code("""EXPORT_DIR_38 = Path("/content/exported_models_38")
EXPORT_DIR_38.mkdir(parents=True, exist_ok=True)

# 1. Weights
model_path = EXPORT_DIR_38 / "disease_model_v2_38class.pth"
torch.save(model.state_dict(), model_path)

# 2. Label mapping
mapping_path = EXPORT_DIR_38 / "disease_label_mapping_v2_38class.json"
mapping_data = {
    "num_classes": num_classes,
    "class_names": class_names,
    "class_to_idx": {name: i for i, name in enumerate(class_names)},
    "idx_to_class": {str(i): name for i, name in enumerate(class_names)}
}
with open(mapping_path, "w") as f:
    json.dump(mapping_data, f, indent=2)

# 3. Model metadata
metadata_path = EXPORT_DIR_38 / "disease_model_metadata_v2_38class.json"
metadata_data = {
    "model_name": "FarmFusion Disease Model V2 (38-Class)",
    "architecture": "efficientnet_b3",
    "image_size": IMG_SIZE,
    "normalization": {
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225]
    },
    "dataset_source": "PlantVillage Full Dataset (38 Classes)",
    "num_classes": num_classes,
    "class_names": class_names,
    "splits": {
        "total_images": len(all_samples),
        "train_count": len(train_samples),
        "val_count": len(val_samples),
        "test_count": len(test_samples),
        "random_seed": RANDOM_SEED
    },
    "training": {
        "epochs_trained": len(history["train_loss"]),
        "best_epoch": best_epoch,
        "best_val_macro_f1": best_val_macro_f1,
        "optimizer": "AdamW",
        "learning_rate": 2e-4,
        "precision": "Mixed Precision (AMP FP16)"
    },
    "test_metrics": {
        "accuracy": float(test_acc),
        "balanced_accuracy": float(test_bal_acc),
        "macro_f1": float(test_macro_f1),
        "weighted_f1": float(test_weighted_f1),
        "top3_accuracy": float(test_top3_acc),
        "brier_score": float(brier),
        "ece": float(ece)
    },
    "confidence_thresholds": {
        "HIGH": ">=0.75",
        "MEDIUM": "0.45-0.74",
        "LOW": "0.30-0.44",
        "UNCLEAR": "<0.30"
    },
    "timestamp_utc": datetime.datetime.utcnow().isoformat(),
    "framework_versions": {
        "torch": torch.__version__,
        "timm": timm.__version__
    }
}

with open(metadata_path, "w") as f:
    json.dump(metadata_data, f, indent=2)

print("Export verified:")
for p in [model_path, mapping_path, metadata_path]:
    size_mb = p.stat().st_size / (1024 * 1024)
    print(f" ✓ {p.name:36} ({size_mb:.2f} MB)")""")

    # 12. Final Report
    add_md("## 12. Final Training Report")
    add_code("""print(\"\"\"
========================================
FARMFUSION 38-CLASS DISEASE MODEL V2
========================================

Dataset: PlantVillage (Full 38-Class)
Images:  {total_images}
Classes: 38
GPU:     {gpu_name}

Training:
Train:       {train_count} images
Validation:  {val_count} images
Test:        {test_count} images

Best Epoch:               {best_epoch}
Best Validation Macro F1: {best_val_macro_f1:.4f}

TEST RESULTS
Accuracy:          {test_acc:.2f}%
Balanced Accuracy: {bal_acc:.2f}%
Macro F1:          {macro_f1:.4f}
Weighted F1:       {weighted_f1:.4f}
Top-3 Accuracy:    {top3_acc:.2f}%

Artifacts:
- /content/exported_models_38/disease_model_v2_38class.pth
- /content/exported_models_38/disease_label_mapping_v2_38class.json
- /content/exported_models_38/disease_model_metadata_v2_38class.json
========================================
\"\"\".format(
    total_images=len(all_samples),
    gpu_name=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
    train_count=len(train_samples),
    val_count=len(val_samples),
    test_count=len(test_samples),
    best_epoch=best_epoch,
    best_val_macro_f1=best_val_macro_f1,
    test_acc=test_acc * 100,
    bal_acc=test_bal_acc * 100,
    macro_f1=test_macro_f1,
    weighted_f1=test_weighted_f1,
    top3_acc=test_top3_acc * 100
))""")

    nb_json = {
        "cells": cells,
        "metadata": {
            "accelerator": "GPU",
            "colab": {
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }

    target_file = Path("/home/rdj/FarmFusionFinal/ml_training/disease_detection/notebooks/FarmFusion_Disease_Model_V2_38Class.ipynb")
    with open(target_file, "w") as f:
        json.dump(nb_json, f, indent=1)
    print(f"Wrote new notebook to {target_file}")

create_38class_notebook()
