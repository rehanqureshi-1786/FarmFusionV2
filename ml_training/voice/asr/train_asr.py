"""
ASR Adaptation & Fine-Tuning Pipeline for Indian Languages and Dialects.
Provides structured fine-tuning configuration, agricultural entity weighting, and export specs for IndicWhisper / Conformer.
"""
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import structlog
from pydantic import BaseModel, Field

from ml_training.voice.datasets.manifest import DatasetManifest, DatasetType
from ml_training.voice.datasets.gates import DatasetQualityGate
from ml_training.voice.datasets.loader import VoiceDatasetLoader

logger = structlog.get_logger(__name__)


class ASRTrainingConfig(BaseModel):
    base_model_name: str = "ai4bharat/indicwhisper-hindi"
    target_language: str = "hi"
    target_dialect: Optional[str] = None
    learning_rate: float = 1e-4
    warmup_steps: int = 500
    max_steps: int = 5000
    batch_size: int = 16
    gradient_accumulation_steps: int = 2
    fp16: bool = True
    use_peft_lora: bool = True
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = Field(default_factory=lambda: ["q_proj", "v_proj"])
    agri_entity_loss_weight: float = 2.0


class ASRAdaptationPipeline:
    """
    Manages end-to-end ASR adaptation workflow on verified speech datasets.
    """
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("/home/rdj/FarmFusionFinal/ml_training/voice/models/asr")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def prepare_training_job(
        self,
        manifest: DatasetManifest,
        data_file_path: Path,
        config: ASRTrainingConfig,
        version: str = "0.1.0",
    ) -> Dict[str, Any]:
        """
        Validate dataset gates and prepare fine-tuning job spec and speaker-disjoint splits.
        """
        # 1. Quality Gates
        DatasetQualityGate.assert_gate(manifest, data_file_path, min_samples=20)
        if manifest.dataset_type != DatasetType.AUDIO_ASR:
            raise ValueError(f"Expected AUDIO_ASR dataset type, got {manifest.dataset_type}")

        # 2. Speaker-Disjoint Split
        split = VoiceDatasetLoader.load_asr_dataset_speaker_disjoint(data_file_path)

        job_spec = {
            "job_id": f"asr_adapt_{manifest.language}_{version}",
            "config": config.model_dump(),
            "manifest": manifest.model_dump(),
            "train_samples": len(split.train),
            "val_samples": len(split.val),
            "test_samples": len(split.test),
            "output_dir": str(self.output_dir / f"{manifest.language}_{version}"),
            "status": "READY_FOR_TRAINING",
        }

        # Save job configuration
        job_file = self.output_dir / f"job_spec_{manifest.language}_{version}.json"
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(job_spec, f, indent=2)

        logger.info("asr_training_job_prepared", job_file=str(job_file))
        return job_spec
