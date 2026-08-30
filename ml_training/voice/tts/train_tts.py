"""
Text-to-Speech (TTS) Voice Model Adaptation Pipeline.
Configures acoustic fine-tuning on high-quality licensed speech data with pronunciation & speaker checks.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import structlog
from pydantic import BaseModel, Field

from ml_training.voice.datasets.manifest import DatasetManifest, DatasetType
from ml_training.voice.datasets.gates import DatasetQualityGate

logger = structlog.get_logger(__name__)


class TTSTrainingConfig(BaseModel):
    base_architecture: str = "piper_vits"
    target_language: str = "hi"
    target_dialect: Optional[str] = None
    sampling_rate: int = 22050
    batch_size: int = 8
    learning_rate: float = 2e-4
    epochs: int = 1000
    single_speaker: bool = True
    speaker_id: str = "indic_rural_farmer_01"


class TTSAdaptationPipeline:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("/home/rdj/FarmFusionFinal/ml_training/voice/models/tts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def prepare_training_job(
        self,
        manifest: DatasetManifest,
        data_file_path: Path,
        config: TTSTrainingConfig,
        version: str = "0.1.0",
    ) -> Dict[str, Any]:
        DatasetQualityGate.assert_gate(manifest, data_file_path, min_samples=20)
        if manifest.dataset_type != DatasetType.AUDIO_TTS:
            raise ValueError(f"Expected AUDIO_TTS dataset type, got {manifest.dataset_type}")

        job_spec = {
            "job_id": f"tts_adapt_{manifest.language}_{version}",
            "config": config.model_dump(),
            "manifest": manifest.model_dump(),
            "output_dir": str(self.output_dir / f"{manifest.language}_{version}"),
            "status": "READY_FOR_TRAINING",
        }

        job_file = self.output_dir / f"job_spec_{manifest.language}_{version}.json"
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(job_spec, f, indent=2)

        logger.info("tts_training_job_prepared", job_file=str(job_file))
        return job_spec
