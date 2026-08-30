"""
Agricultural NLU Model Training Pipeline.
Trains a lightweight multilingual intent classifier & entity extractor suitable for edge/server inference.
"""
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import joblib
import structlog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, f1_score, accuracy_score

from ml_training.voice.datasets.manifest import DatasetManifest
from ml_training.voice.datasets.loader import VoiceDatasetLoader, NLUSample
from ml_training.voice.datasets.gates import DatasetQualityGate
from ml_training.voice.preprocessing.text_normalizer import VoiceTextNormalizer

logger = structlog.get_logger(__name__)


class AgriculturalNLUTrainer:
    """
    Trains, evaluates, and exports the FarmFusion Agricultural NLU model.
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("/home/rdj/FarmFusionFinal/ml_training/voice/models/nlu")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline: Optional[Pipeline] = None
        self.classes_: List[str] = []

    def train(
        self,
        manifest: DatasetManifest,
        data_file_path: Path,
        version: str = "1.0.0",
        min_samples: int = 10,
    ) -> Dict[str, Any]:
        """
        Execute gated NLU training run.
        """
        # 1. Verification Gate
        DatasetQualityGate.assert_gate(manifest, data_file_path, min_samples=min_samples)

        # 2. Load & Split Data
        split = VoiceDatasetLoader.load_nlu_dataset(data_file_path)
        train_samples: List[NLUSample] = split.train
        val_samples: List[NLUSample] = split.val
        test_samples: List[NLUSample] = split.test

        train_texts = [VoiceTextNormalizer.normalize_text(s.text) for s in train_samples]
        train_labels = [s.intent for s in train_samples]

        val_texts = [VoiceTextNormalizer.normalize_text(s.text) for s in val_samples]
        val_labels = [s.intent for s in val_samples]

        test_texts = [VoiceTextNormalizer.normalize_text(s.text) for s in test_samples]
        test_labels = [s.intent for s in test_samples]

        # 3. Build & Train Pipeline
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb", min_df=1)),
            ("clf", LogisticRegression(C=1.0, max_iter=200, class_weight="balanced"))
        ])

        self.pipeline.fit(train_texts, train_labels)
        self.classes_ = list(self.pipeline.classes_)

        # 4. Evaluate on Validation & Test Sets
        val_preds = self.pipeline.predict(val_texts) if val_texts else []
        val_acc = accuracy_score(val_labels, val_preds) if val_texts else 1.0

        test_preds = self.pipeline.predict(test_texts) if test_texts else []
        test_acc = accuracy_score(test_labels, test_preds) if test_texts else 1.0
        test_f1 = f1_score(test_labels, test_preds, average="weighted", zero_division=0) if test_texts else 1.0

        metrics = {
            "train_samples": len(train_samples),
            "val_samples": len(val_samples),
            "test_samples": len(test_samples),
            "val_accuracy": round(float(val_acc), 4),
            "test_accuracy": round(float(test_acc), 4),
            "test_weighted_f1": round(float(test_f1), 4),
            "intents": self.classes_,
        }

        # 5. Export Model Artifact
        save_path = self.output_dir / f"agri_nlu_{manifest.language}_{version}.joblib"
        joblib.dump({
            "pipeline": self.pipeline,
            "classes": self.classes_,
            "language": manifest.language,
            "version": version,
            "metrics": metrics,
        }, save_path)

        logger.info(
            "nlu_training_complete",
            model_path=str(save_path),
            test_accuracy=test_acc,
            test_f1=test_f1
        )
        return {"model_path": str(save_path), "metrics": metrics}
