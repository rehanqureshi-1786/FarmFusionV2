"""
Regional Dialect Classifier & Morphological Rule Adaptation Trainer.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import joblib
import structlog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

from ml_training.voice.datasets.manifest import DatasetManifest
from ml_training.voice.preprocessing.text_normalizer import VoiceTextNormalizer

logger = structlog.get_logger(__name__)


class DialectClassifierTrainer:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("/home/rdj/FarmFusionFinal/ml_training/voice/models/dialect")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train(
        self,
        manifest: DatasetManifest,
        records: List[Dict[str, str]],
        version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """
        Train dialect identifier (e.g. Marwari vs Mewari vs Standard Hindi).
        """
        if len(records) < 10:
            raise ValueError(f"At least 10 records required to train dialect classifier, got {len(records)}")

        texts = [VoiceTextNormalizer.normalize_text(r["text"]) for r in records]
        labels = [r["dialect"] for r in records]

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb", min_df=1)),
            ("clf", LogisticRegression(C=1.5, max_iter=200, class_weight="balanced"))
        ])

        pipeline.fit(texts, labels)
        preds = pipeline.predict(texts)
        acc = accuracy_score(labels, preds)

        save_path = self.output_dir / f"dialect_{manifest.language}_{version}.joblib"
        joblib.dump({
            "pipeline": pipeline,
            "classes": list(pipeline.classes_),
            "parent_language": manifest.language,
            "version": version,
            "accuracy": round(float(acc), 4)
        }, save_path)

        logger.info("dialect_training_complete", path=str(save_path), accuracy=acc)
        return {"model_path": str(save_path), "accuracy": acc, "dialects": list(pipeline.classes_)}
