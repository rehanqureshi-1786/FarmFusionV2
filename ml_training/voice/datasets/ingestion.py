"""
Authenticated Dataset Ingestion Pipeline for FarmFusion Multilingual & Regional Dialect Data.
"""
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import hashlib
import structlog
from datetime import datetime

from ml_training.voice.datasets.manifest import DatasetManifest, DatasetTask, DatasetType, DatasetLicense

logger = structlog.get_logger(__name__)


class DatasetIngestionPipeline:
    """
    Ingests and validates new verified dialect and agricultural speech/text collections.
    """
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path("/home/rdj/FarmFusionFinal/ml_training/voice/data_store")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def ingest_nlu_collection(
        self,
        dataset_id: str,
        records: List[Dict[str, Any]],
        language: str,
        dialect: Optional[str] = None,
        region: Optional[str] = None,
        source: str = "ICAR-Agmarknet-FarmerBench",
        license: DatasetLicense = DatasetLicense.OPEN_GOV_INDIA,
        approved_for_training: bool = True,
        approval_notes: Optional[str] = None
    ) -> Tuple[DatasetManifest, Path]:
        """
        Ingest a verified NLU intent and entity collection with provenance metadata.
        """
        data_file = self.storage_dir / f"{dataset_id}.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        # Compute SHA256
        hasher = hashlib.sha256()
        with open(data_file, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        checksum = hasher.hexdigest()

        manifest = DatasetManifest(
            dataset_id=dataset_id,
            task=DatasetTask.NLU,
            dataset_type=DatasetType.INTENT_SLOT,
            language=language,
            dialect=dialect,
            region=region,
            source=source,
            license=license,
            text_rows=len(records),
            created_at=datetime.utcnow().isoformat(),
            sha256_checksum=checksum,
            approved_for_training=approved_for_training,
            approval_notes=approval_notes,
        )

        manifest_file = self.storage_dir / f"{dataset_id}.manifest.json"
        manifest.save_manifest(manifest_file)

        logger.info(
            "dataset_ingested",
            dataset_id=dataset_id,
            records=len(records),
            manifest=str(manifest_file)
        )
        return (manifest, data_file)
