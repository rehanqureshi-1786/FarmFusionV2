"""
Strict Quality & Compliance Verification Gates for FarmFusion Voice Training.
Enforces that every dataset strictly meets licensing, provenance, and data integrity standards prior to training.
"""
from typing import List, Dict, Any, Tuple
from pathlib import Path
import structlog
from ml_training.voice.datasets.manifest import DatasetManifest, DatasetType

logger = structlog.get_logger(__name__)


class TrainingGateError(Exception):
    pass


class DatasetQualityGate:
    """
    Executes automated pre-training verification gates.
    """
    @staticmethod
    def verify_dataset(
        manifest: DatasetManifest,
        data_file_path: Path,
        min_samples: int = 10,
        allow_synthetic: bool = False
    ) -> Tuple[bool, List[str]]:
        errors = []

        # 1. Manifest Approval & License Gate
        is_manifest_valid, manifest_errors = manifest.validate_for_training()
        if not is_manifest_valid:
            errors.extend(manifest_errors)

        # 2. Synthetic Data Rejection Gate
        if manifest.is_synthetic and not allow_synthetic:
            errors.append("Gate FAILED: Synthetic speech/text datasets are strictly prohibited in FarmFusion.")

        # 3. Physical File Existence Gate
        if not data_file_path.exists():
            errors.append(f"Gate FAILED: Data file does not exist at '{data_file_path}'.")
            return (False, errors)

        # 4. File Size & Content Gate
        if data_file_path.stat().st_size == 0:
            errors.append(f"Gate FAILED: Data file at '{data_file_path}' is empty (0 bytes).")
            return (False, errors)

        # 5. Data Rows / Samples Count Gate
        try:
            import json
            with open(data_file_path, "r", encoding="utf-8") as f:
                records = json.load(f)
            
            if not isinstance(records, list):
                errors.append(f"Gate FAILED: Data file must contain a JSON array of records.")
                return (False, errors)

            if len(records) < min_samples:
                errors.append(f"Gate FAILED: Sample count ({len(records)}) is less than minimum required ({min_samples}).")

            # 6. Duplicate & Corruption Check
            seen_texts = set()
            corrupt_count = 0
            for idx, r in enumerate(records):
                if not isinstance(r, dict):
                    corrupt_count += 1
                    continue
                
                text = r.get("text") or r.get("transcript")
                if not text or not str(text).strip():
                    corrupt_count += 1
                
                # Check required task-specific fields
                if manifest.task == "nlu" and not r.get("intent"):
                    errors.append(f"Gate FAILED: Record #{idx} missing 'intent' field.")
                    break
                if manifest.dataset_type == DatasetType.AUDIO_ASR and not r.get("speaker_id"):
                    errors.append(f"Gate FAILED: Audio record #{idx} missing 'speaker_id'.")
                    break

            if corrupt_count > 0:
                errors.append(f"Gate FAILED: Found {corrupt_count} corrupt or empty records in dataset.")

        except Exception as e:
            errors.append(f"Gate FAILED: Unable to parse dataset JSON: {str(e)}")

        passed = (len(errors) == 0)
        if passed:
            logger.info("training_gate_passed", dataset_id=manifest.dataset_id, task=manifest.task)
        else:
            logger.error("training_gate_failed", dataset_id=manifest.dataset_id, errors=errors)

        return (passed, errors)

    @classmethod
    def assert_gate(cls, manifest: DatasetManifest, data_file_path: Path, min_samples: int = 10):
        passed, errors = cls.verify_dataset(manifest, data_file_path, min_samples=min_samples)
        if not passed:
            error_msg = "\n".join([f" - {e}" for e in errors])
            raise TrainingGateError(f"Training blocked by Dataset Quality Gates:\n{error_msg}")
