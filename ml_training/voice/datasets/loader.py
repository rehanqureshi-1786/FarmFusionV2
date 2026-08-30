"""
Modular Dataset Loaders & Split Generators for FarmFusion Voice Training.
Supports:
- Type A: Text-only language/dialect classification
- Type B: Intent / Slot agricultural NLU
- Type C: Audio + Transcript ASR with speaker-disjoint splits
- Type D: Audio + Transcript TTS with phonetic quality checks
"""
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import random
import structlog
from pydantic import BaseModel, Field

from ml_training.voice.datasets.manifest import DatasetManifest, DatasetType

logger = structlog.get_logger(__name__)


class NLUSample(BaseModel):
    id: str
    text: str
    language: str
    dialect: Optional[str] = None
    region: Optional[str] = None
    intent: str
    entities: Dict[str, Any] = Field(default_factory=dict)
    canonical_text: Optional[str] = None
    source: str = "ICAR-Agmarknet-FarmerBench"


class ASRSample(BaseModel):
    id: str
    audio_path: str
    transcript: str
    language: str
    dialect: Optional[str] = None
    speaker_id: str
    duration_sec: float
    sampling_rate: int = 16000
    snr_db: Optional[float] = None


class TTSSample(BaseModel):
    id: str
    audio_path: str
    text: str
    phonemes: Optional[str] = None
    speaker_id: str
    language: str
    dialect: Optional[str] = None
    duration_sec: float
    sampling_rate: int = 22050


class DatasetSplit(BaseModel):
    train: List[Any]
    val: List[Any]
    test: List[Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VoiceDatasetLoader:
    """
    Loads and splits voice and language datasets with zero speaker-leakage guarantees.
    """
    @staticmethod
    def load_nlu_dataset(
        file_path: Path,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = 42
    ) -> DatasetSplit:
        if not file_path.exists():
            raise FileNotFoundError(f"NLU dataset file not found: {file_path}")

        samples = []
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                samples.append(NLUSample(**item))

        random.seed(seed)
        random.shuffle(samples)

        n = len(samples)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)

        train_samples = samples[:n_train]
        val_samples = samples[n_train:n_train + n_val]
        test_samples = samples[n_train + n_val:]

        logger.info(
            "nlu_dataset_loaded",
            total=n,
            train=len(train_samples),
            val=len(val_samples),
            test=len(test_samples)
        )

        return DatasetSplit(
            train=train_samples,
            val=val_samples,
            test=test_samples,
            metadata={"dataset_type": DatasetType.INTENT_SLOT, "total": n}
        )

    @staticmethod
    def load_asr_dataset_speaker_disjoint(
        file_path: Path,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = 42
    ) -> DatasetSplit:
        """
        Partition ASR audio samples by speaker ID to strictly prevent speaker leakage.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"ASR dataset file not found: {file_path}")

        samples_by_speaker: Dict[str, List[ASRSample]] = {}
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                sample = ASRSample(**item)
                samples_by_speaker.setdefault(sample.speaker_id, []).append(sample)

        speakers = list(samples_by_speaker.keys())
        random.seed(seed)
        random.shuffle(speakers)

        n_spk = len(speakers)
        n_train_spk = max(1, int(n_spk * train_ratio))
        n_val_spk = max(1, int(n_spk * val_ratio)) if n_spk >= 3 else 0

        train_spks = set(speakers[:n_train_spk])
        val_spks = set(speakers[n_train_spk:n_train_spk + n_val_spk])
        test_spks = set(speakers[n_train_spk + n_val_spk:])

        train_samples = [s for spk in train_spks for s in samples_by_speaker[spk]]
        val_samples = [s for spk in val_spks for s in samples_by_speaker[spk]]
        test_samples = [s for spk in test_spks for s in samples_by_speaker[spk]]

        # Leakage verification assertion
        assert len(train_spks.intersection(val_spks)) == 0, "Speaker leakage detected between train and val!"
        assert len(train_spks.intersection(test_spks)) == 0, "Speaker leakage detected between train and test!"

        logger.info(
            "asr_speaker_disjoint_split_created",
            total_speakers=n_spk,
            train_speakers=len(train_spks),
            val_speakers=len(val_spks),
            test_speakers=len(test_spks),
            train_samples=len(train_samples),
            val_samples=len(val_samples),
            test_samples=len(test_samples)
        )

        return DatasetSplit(
            train=train_samples,
            val=val_samples,
            test=test_samples,
            metadata={"dataset_type": DatasetType.AUDIO_ASR, "speaker_disjoint": True}
        )
