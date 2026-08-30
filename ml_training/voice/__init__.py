"""
FarmFusion Voice & Language Model Training Subsystem.
"""
from ml_training.voice.datasets import (
    DatasetManifest,
    DatasetTask,
    DatasetType,
    DatasetLicense,
    VoiceDatasetLoader,
    DatasetQualityGate,
    TrainingGateError,
    DatasetIngestionPipeline,
)
from ml_training.voice.preprocessing import VoiceAudioProcessor, VoiceTextNormalizer
from ml_training.voice.nlu import AgriculturalNLUTrainer, CanonicalIntent, CANONICAL_SLOT_TYPES
from ml_training.voice.lid import LanguageIdentificationTrainer
from ml_training.voice.dialect import DialectClassifierTrainer
from ml_training.voice.asr import ASRTrainingConfig, ASRAdaptationPipeline
from ml_training.voice.tts import TTSTrainingConfig, TTSAdaptationPipeline
from ml_training.voice.evaluation import (
    compute_wer,
    compute_cer,
    compute_agricultural_entity_accuracy,
    VoiceModelEvaluator,
)
from ml_training.voice.export import VoiceModelExporter, LanguagePackBundleGenerator

__all__ = [
    "DatasetManifest",
    "DatasetTask",
    "DatasetType",
    "DatasetLicense",
    "VoiceDatasetLoader",
    "DatasetQualityGate",
    "TrainingGateError",
    "DatasetIngestionPipeline",
    "VoiceAudioProcessor",
    "VoiceTextNormalizer",
    "AgriculturalNLUTrainer",
    "CanonicalIntent",
    "CANONICAL_SLOT_TYPES",
    "LanguageIdentificationTrainer",
    "DialectClassifierTrainer",
    "ASRTrainingConfig",
    "ASRAdaptationPipeline",
    "TTSTrainingConfig",
    "TTSAdaptationPipeline",
    "compute_wer",
    "compute_cer",
    "compute_agricultural_entity_accuracy",
    "VoiceModelEvaluator",
    "VoiceModelExporter",
    "LanguagePackBundleGenerator",
]
