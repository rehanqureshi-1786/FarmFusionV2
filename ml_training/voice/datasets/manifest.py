"""
Dataset Manifest & Provenance Schema for FarmFusion Voice & Language Training.
Enforces strict licensing, ethical compliance, domain tagging, and approval gates before any model training can occur.
"""
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import hashlib
import json
from pydantic import BaseModel, Field, field_validator


class DatasetTask(str, Enum):
    LID = "lid"                   # Language Identification
    DIALECT = "dialect"           # Dialect Identification & Morphological Normalization
    NLU = "nlu"                   # Agricultural Intent Classification & Slot Filling
    ASR = "asr"                   # Automatic Speech Recognition Adaptation
    TTS = "tts"                   # Text-to-Speech Voice Adaptation
    VOCABULARY = "vocabulary"     # Agricultural Lexicon & Entity Normalization


class DatasetType(str, Enum):
    TEXT_ONLY = "text_only"       # Raw or labeled text utterances
    INTENT_SLOT = "intent_slot"   # Semantic intent & slot annotations
    AUDIO_ASR = "audio_asr"       # Audio files with paired transcription
    AUDIO_TTS = "audio_tts"       # High-quality studio/clean audio with verified phonetic transcripts


class DatasetLicense(str, Enum):
    CC_BY_4_0 = "CC-BY-4.0"
    CC_BY_SA_4_0 = "CC-BY-SA-4.0"
    CC0_1_0 = "CC0-1.0"
    MIT = "MIT"
    APACHE_2_0 = "Apache-2.0"
    OPEN_GOV_INDIA = "GODL-India" # Government Open Data License - India
    RESEARCH_ONLY = "Academic-Research-Only"
    COMMERCIAL_VERIFIED = "Commercial-Verified"
    CUSTOM_PROPRIETARY = "Custom-Proprietary"


class DatasetManifest(BaseModel):
    dataset_id: str
    task: DatasetTask
    dataset_type: DatasetType
    language: str
    dialect: Optional[str] = None
    region: Optional[str] = None
    source: str
    license: DatasetLicense
    license_url: Optional[str] = None
    speaker_count: int = Field(default=0, ge=0)
    audio_hours: float = Field(default=0.0, ge=0.0)
    text_rows: int = Field(default=0, ge=0)
    sampling_rate_hz: Optional[int] = 16000
    script: str = "Devanagari"
    domain: str = "agriculture"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sha256_checksum: Optional[str] = None
    approved_for_training: bool = False
    approval_notes: Optional[str] = None
    is_synthetic: bool = False

    @field_validator("is_synthetic")
    @classmethod
    def reject_synthetic_speech(cls, v: bool, info) -> bool:
        if v:
            raise ValueError("Synthetic speech data is strictly prohibited in FarmFusion training manifests.")
        return v

    def validate_for_training(self) -> tuple[bool, List[str]]:
        """
        Strict validation gate. Returns (is_valid, list_of_errors).
        Training MUST be blocked if is_valid is False.
        """
        errors = []
        if not self.approved_for_training:
            errors.append(f"Dataset '{self.dataset_id}' is NOT approved for training (approved_for_training != True).")
        if not self.source or not self.source.strip():
            errors.append(f"Dataset '{self.dataset_id}' is missing provenance source information.")
        if not self.license:
            errors.append(f"Dataset '{self.dataset_id}' is missing a valid license.")
        if self.dataset_type in [DatasetType.AUDIO_ASR, DatasetType.AUDIO_TTS] and self.audio_hours <= 0.0:
            errors.append(f"Audio dataset '{self.dataset_id}' specifies 0.0 audio hours.")
        if self.dataset_type in [DatasetType.TEXT_ONLY, DatasetType.INTENT_SLOT] and self.text_rows <= 0:
            errors.append(f"Text dataset '{self.dataset_id}' specifies 0 text rows.")
        return (len(errors) == 0, errors)

    def save_manifest(self, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load_manifest(cls, manifest_path: Path) -> "DatasetManifest":
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
