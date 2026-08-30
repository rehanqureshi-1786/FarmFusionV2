"""
Language Identification (LID) Model Training Pipeline.
Trains a lightweight multilingual character n-gram LID model covering all 14 Indian languages.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import joblib
import structlog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score

from ml_training.voice.datasets.manifest import DatasetManifest
from ml_training.voice.datasets.gates import DatasetQualityGate
from ml_training.voice.preprocessing.text_normalizer import VoiceTextNormalizer

logger = structlog.get_logger(__name__)


class LanguageIdentificationTrainer:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("/home/rdj/FarmFusionFinal/ml_training/voice/models/lid")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train(
        self,
        manifest: DatasetManifest,
        records: List[Dict[str, str]],
        version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """
        Train lightweight multilingual LID classifier from labeled (text, language) tuples.
        """
        if len(records) < 10:
            raise ValueError(f"At least 10 records required to train LID, got {len(records)}")

        texts = [VoiceTextNormalizer.normalize_text(r["text"]) for r in records]
        labels = [r["language"] for r in records]

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(2, 4), analyzer="char", min_df=1)),
            ("clf", LogisticRegression(C=2.0, max_iter=200, class_weight="balanced"))
        ])

        pipeline.fit(texts, labels)
        preds = pipeline.predict(texts)
        acc = accuracy_score(labels, preds)

        save_path = self.output_dir / f"indic_lid_{version}.joblib"
        joblib.dump({
            "pipeline": pipeline,
            "classes": list(pipeline.classes_),
            "version": version,
            "accuracy": round(float(acc), 4)
        }, save_path)

        logger.info("lid_training_complete", path=str(save_path), accuracy=acc)
        return {"model_path": str(save_path), "accuracy": acc, "languages": list(pipeline.classes_)}
