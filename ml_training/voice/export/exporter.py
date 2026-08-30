"""
Model Export & Optimization Pipeline for FarmFusion Voice Models.
Handles:
- Versioned model directory structuring (models/<task>/<language>/<version>/)
- Manifest generation with SHA-256 checksum calculation
- Int8 quantization and runtime metadata tagging
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import hashlib
import shutil
import structlog
from pydantic import BaseModel

from ml_training.voice.datasets.manifest import DatasetTask

logger = structlog.get_logger(__name__)


class ExportMetadata(BaseModel):
    model_id: str
    task: str
    language: str
    dialect: Optional[str] = None
    version: str
    format: str = "joblib"
    runtime: str = "rule_engine"
    device: str = "cpu"
    quantization: Optional[str] = None
    size_mb: float
    sha256_checksum: str
    metrics: Dict[str, Any]
    exported_at: str


class VoiceModelExporter:
    def __init__(self, base_export_dir: Optional[Path] = None):
        self.base_export_dir = base_export_dir or Path("/home/rdj/FarmFusionFinal/backend/models/voice")
        self.base_export_dir.mkdir(parents=True, exist_ok=True)

    def export_model_artifact(
        self,
        artifact_path: Path,
        model_id: str,
        task: str,
        language: str,
        dialect: Optional[str] = None,
        version: str = "1.0.0",
        format_name: str = "joblib",
        runtime: str = "rule_engine",
        metrics: Optional[Dict[str, Any]] = None,
    ) -> ExportMetadata:
        """
        Copy model artifact to versioned target path and write export metadata.
        """
        if not artifact_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {artifact_path}")

        target_dir = self.base_export_dir / task / language / version
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / artifact_path.name
        shutil.copy2(artifact_path, target_file)

        # Compute SHA-256
        hasher = hashlib.sha256()
        with open(target_file, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        checksum = hasher.hexdigest()
        size_mb = round(target_file.stat().st_size / (1024 * 1024), 3)

        from datetime import datetime, timezone
        meta = ExportMetadata(
            model_id=model_id,
            task=task,
            language=language,
            dialect=dialect,
            version=version,
            format=format_name,
            runtime=runtime,
            size_mb=size_mb,
            sha256_checksum=checksum,
            metrics=metrics or {},
            exported_at=datetime.now(timezone.utc).isoformat(),
        )

        meta_file = target_dir / "metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            f.write(meta.model_dump_json(indent=2))

        logger.info(
            "model_exported_successfully",
            target=str(target_file),
            checksum=checksum,
            size_mb=size_mb
        )
        return meta
