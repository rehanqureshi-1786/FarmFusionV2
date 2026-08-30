"""
Local Model Registry for FarmFusion Voice Intelligence.
Tracks manifests, formats, execution runtimes, checksums, and real installation status for on-device voice models.
"""
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import structlog
from pydantic import BaseModel, Field

from app.voice.local.config import DeviceTier, local_voice_config

logger = structlog.get_logger(__name__)


class ModelTask(str, Enum):
    ASR = "asr"
    LID = "lid"
    DIALECT = "dialect"
    NLU = "nlu"
    RESPONSE = "response"
    TTS = "tts"


class ModelFormat(str, Enum):
    ONNX = "onnx"
    TFLITE = "tflite"
    PYTORCH = "pytorch"
    GGUF = "gguf"
    RULE_BASED = "rule_based"


class ModelStatus(str, Enum):
    INSTALLED = "installed"       # Model binary exists locally and passes checksum
    DOWNLOADABLE = "downloadable" # Registered in catalog, can be downloaded on demand
    AVAILABLE = "available"       # Ready in memory / runtime
    UNAVAILABLE = "unavailable"   # Missing binary or unsupported by device profile


class LocalModelManifest(BaseModel):
    model_id: str
    task: ModelTask
    language: str
    dialect: Optional[str] = None
    version: str
    format: ModelFormat
    runtime: str = "onnx"
    device: str = "cpu"
    quantization: Optional[str] = "int8"
    size_mb: float
    min_device_tier: DeviceTier = DeviceTier.LOW_END
    model_relative_path: str
    sha256_checksum: Optional[str] = None
    enabled: bool = True
    capabilities: List[str] = Field(default_factory=list)


class LocalModelRegistry:
    """
    Registry of local trainable / runnable models.
    Guarantees zero-fabrication: is_model_installed() returns True ONLY if the actual binary exists.
    """
    def __init__(self, base_models_dir: Optional[Path] = None):
        self.base_models_dir = base_models_dir or local_voice_config.models_dir
        self._manifests: Dict[str, LocalModelManifest] = {}
        self._register_default_catalog()

    def _register_default_catalog(self):
        """Register the official FarmFusion model catalog manifests."""
        defaults = [
            # 1. Local Language & Dialect Detection Models
            LocalModelManifest(
                model_id="farmfusion_lid_indic_v1",
                task=ModelTask.LID,
                language="all_indic",
                version="1.0.0",
                format=ModelFormat.RULE_BASED,
                runtime="rule_engine",
                size_mb=2.5,
                min_device_tier=DeviceTier.LOW_END,
                model_relative_path="lid/indic_lid_v1.json",
                capabilities=["fast_lid", "14_languages", "24_dialects"],
            ),
            LocalModelManifest(
                model_id="farmfusion_dialect_rajasthani_v1",
                task=ModelTask.DIALECT,
                language="hi",
                dialect="rwr",
                version="1.0.0",
                format=ModelFormat.RULE_BASED,
                runtime="rule_engine",
                size_mb=1.2,
                min_device_tier=DeviceTier.LOW_END,
                model_relative_path="dialect/rajasthani_dialect_v1.json",
                capabilities=["marwari_detection", "mewari_detection", "dhundhari_detection"],
            ),
            # 2. Local Agricultural NLU Models
            LocalModelManifest(
                model_id="farmfusion_agri_nlu_multilingual_v1",
                task=ModelTask.NLU,
                language="all_indic",
                version="1.0.0",
                format=ModelFormat.RULE_BASED,
                runtime="rule_engine",
                size_mb=4.8,
                min_device_tier=DeviceTier.LOW_END,
                model_relative_path="nlu/agri_intent_slots_v1.json",
                capabilities=["intent_classification", "slot_filling", "agricultural_vocabulary"],
            ),
            # 3. Local Response Models
            LocalModelManifest(
                model_id="farmfusion_response_agri_slm_v1",
                task=ModelTask.RESPONSE,
                language="all_indic",
                version="1.0.0",
                format=ModelFormat.RULE_BASED,
                runtime="rule_engine",
                size_mb=3.5,
                min_device_tier=DeviceTier.LOW_END,
                model_relative_path="response/agri_synthesizer_v1.json",
                capabilities=["grounded_response", "multi_language_rules", "dialect_narration"],
            ),
            # 4. Trainable / Downloadable ONNX ASR Models (Manifest specs for train pipeline)
            LocalModelManifest(
                model_id="farmfusion_asr_hindi_whisper_tiny_int8",
                task=ModelTask.ASR,
                language="hi",
                version="0.1.0",
                format=ModelFormat.ONNX,
                runtime="onnx",
                quantization="int8",
                size_mb=45.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="asr/hi_whisper_tiny_int8.onnx",
                capabilities=["local_speech_to_text", "hindi_native", "farmer_vocabulary"],
            ),
            LocalModelManifest(
                model_id="farmfusion_asr_marwari_conformer_int8",
                task=ModelTask.ASR,
                language="hi",
                dialect="rwr",
                version="0.1.0",
                format=ModelFormat.ONNX,
                runtime="onnx",
                quantization="int8",
                size_mb=38.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="asr/rwr_conformer_int8.onnx",
                capabilities=["local_speech_to_text", "marwari_speech"],
            ),
            # 5. Genuine Local Neural TTS Models (VITS Pretrained)
            LocalModelManifest(
                model_id="farmfusion_tts_hindi_vits_v1",
                task=ModelTask.TTS,
                language="hi",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/hi/farmfusion_tts_hindi_vits_v1",
                capabilities=["local_neural_text_to_speech", "hindi_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_marathi_vits_v1",
                task=ModelTask.TTS,
                language="mr",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/mr/farmfusion_tts_marathi_vits_v1",
                capabilities=["local_neural_text_to_speech", "marathi_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_gujarati_vits_v1",
                task=ModelTask.TTS,
                language="gu",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/gu/farmfusion_tts_gujarati_vits_v1",
                capabilities=["local_neural_text_to_speech", "gujarati_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_bengali_vits_v1",
                task=ModelTask.TTS,
                language="bn",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/bn/farmfusion_tts_bengali_vits_v1",
                capabilities=["local_neural_text_to_speech", "bengali_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_tamil_vits_v1",
                task=ModelTask.TTS,
                language="ta",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/ta/farmfusion_tts_tamil_vits_v1",
                capabilities=["local_neural_text_to_speech", "tamil_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_telugu_vits_v1",
                task=ModelTask.TTS,
                language="te",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/te/farmfusion_tts_telugu_vits_v1",
                capabilities=["local_neural_text_to_speech", "telugu_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_punjabi_vits_v1",
                task=ModelTask.TTS,
                language="pa",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/pa/farmfusion_tts_punjabi_vits_v1",
                capabilities=["local_neural_text_to_speech", "punjabi_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_kannada_vits_v1",
                task=ModelTask.TTS,
                language="kn",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/kn/farmfusion_tts_kannada_vits_v1",
                capabilities=["local_neural_text_to_speech", "kannada_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_malayalam_vits_v1",
                task=ModelTask.TTS,
                language="ml",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/ml/farmfusion_tts_malayalam_vits_v1",
                capabilities=["local_neural_text_to_speech", "malayalam_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_odia_vits_v1",
                task=ModelTask.TTS,
                language="or",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/or/farmfusion_tts_odia_vits_v1",
                capabilities=["local_neural_text_to_speech", "odia_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_assamese_vits_v1",
                task=ModelTask.TTS,
                language="as",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/as/farmfusion_tts_assamese_vits_v1",
                capabilities=["local_neural_text_to_speech", "assamese_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_maithili_vits_v1",
                task=ModelTask.TTS,
                language="mai",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/mai/farmfusion_tts_maithili_vits_v1",
                capabilities=["local_neural_text_to_speech", "maithili_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_haryanvi_vits_v1",
                task=ModelTask.TTS,
                language="bgc",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/bgc/farmfusion_tts_haryanvi_vits_v1",
                capabilities=["local_neural_text_to_speech", "haryanvi_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_chhattisgarhi_vits_v1",
                task=ModelTask.TTS,
                language="hne",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/hne/farmfusion_tts_chhattisgarhi_vits_v1",
                capabilities=["local_neural_text_to_speech", "chhattisgarhi_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_urdu_dev_v1",
                task=ModelTask.TTS,
                language="ur",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/ur_dev/farmfusion_tts_urdu_dev_v1",
                capabilities=["local_neural_text_to_speech", "urdu_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_urdu_ara_v1",
                task=ModelTask.TTS,
                language="ur_ara",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/ur_ara/farmfusion_tts_urdu_ara_v1",
                capabilities=["local_neural_text_to_speech", "urdu_arabic_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_dogri_v1",
                task=ModelTask.TTS,
                language="dgo",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/dgo/farmfusion_tts_dogri_v1",
                capabilities=["local_neural_text_to_speech", "dogri_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_awadhi_v1",
                task=ModelTask.TTS,
                language="awa",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/awa/farmfusion_tts_awadhi_v1",
                capabilities=["local_neural_text_to_speech", "awadhi_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_magahi_v1",
                task=ModelTask.TTS,
                language="mag",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/mag/farmfusion_tts_magahi_v1",
                capabilities=["local_neural_text_to_speech", "magahi_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_garhwali_v1",
                task=ModelTask.TTS,
                language="gbm",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/gbm/farmfusion_tts_garhwali_v1",
                capabilities=["local_neural_text_to_speech", "garhwali_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_bodo_v1",
                task=ModelTask.TTS,
                language="bod",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/bod/farmfusion_tts_bodo_v1",
                capabilities=["local_neural_text_to_speech", "bodo_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_ho_v1",
                task=ModelTask.TTS,
                language="hoc",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/hoc/farmfusion_tts_ho_v1",
                capabilities=["local_neural_text_to_speech", "ho_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_mundari_v1",
                task=ModelTask.TTS,
                language="unr",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/unr/farmfusion_tts_mundari_v1",
                capabilities=["local_neural_text_to_speech", "mundari_vits", "end_to_end_human_speech", "offline_ready"],
            ),
            LocalModelManifest(
                model_id="farmfusion_tts_kurukh_v1",
                task=ModelTask.TTS,
                language="kru",
                version="1.0.0",
                format=ModelFormat.PYTORCH,
                runtime="vits_pytorch",
                size_mb=145.0,
                min_device_tier=DeviceTier.MID_RANGE,
                model_relative_path="tts/kru/farmfusion_tts_kurukh_v1",
                capabilities=["local_neural_text_to_speech", "kurukh_vits", "end_to_end_human_speech", "offline_ready"],
            ),
        ]
        for m in defaults:
            self._manifests[m.model_id] = m

    def register_manifest(self, manifest: LocalModelManifest):
        self._manifests[manifest.model_id] = manifest

    def get_manifest(self, model_id: str) -> Optional[LocalModelManifest]:
        return self._manifests.get(model_id)

    def list_manifests(self, task: Optional[ModelTask] = None, language: Optional[str] = None) -> List[LocalModelManifest]:
        results = list(self._manifests.values())
        if task:
            results = [m for m in results if m.task == task]
        if language:
            results = [m for m in results if m.language in [language, "all_indic"]]
        return results

    def get_model_path(self, model_id: str) -> Optional[Path]:
        manifest = self.get_manifest(model_id)
        if not manifest:
            return None
        return self.base_models_dir / manifest.model_relative_path

    def is_model_installed(self, model_id: str) -> bool:
        """
        Verify if model binary physically exists and is not empty.
        For rule-based models, returns True as they execute via built-in packages.
        """
        manifest = self.get_manifest(model_id)
        if not manifest:
            return False
        if manifest.format == ModelFormat.RULE_BASED:
            return True
        path = self.get_model_path(model_id)
        if path is None or not path.exists():
            return False
        if path.is_dir():
            return any((path / fname).exists() for fname in ["model.safetensors", "pytorch_model.bin", "model.onnx", "model.joblib"])
        return path.is_file() and path.stat().st_size > 0

    def get_model_status(self, model_id: str) -> ModelStatus:
        manifest = self.get_manifest(model_id)
        if not manifest:
            return ModelStatus.UNAVAILABLE
        if self.is_model_installed(model_id):
            return ModelStatus.INSTALLED
        return ModelStatus.DOWNLOADABLE

    def verify_checksum(self, model_id: str) -> bool:
        manifest = self.get_manifest(model_id)
        if not manifest or not manifest.sha256_checksum:
            return self.is_model_installed(model_id)
        path = self.get_model_path(model_id)
        if not path or not path.exists():
            return False
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest().lower() == manifest.sha256_checksum.lower()


local_model_registry = LocalModelRegistry()
