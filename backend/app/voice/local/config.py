"""
Local Voice Intelligence Layer Configuration.
Defines runtime modes (OFFLINE, HYBRID, ONLINE), device execution profiles, and local model paths.
"""
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field


class RuntimeMode(str, Enum):
    OFFLINE = "offline"   # Strictly local models and knowledge; no external network calls
    HYBRID = "hybrid"     # Prioritize local models; fallback to cloud/Bhashini for missing models
    ONLINE = "online"     # Use cloud providers (Bhashini, OpenRouter, etc.) by default


class DeviceTier(str, Enum):
    LOW_END = "low_end"       # <= 2GB RAM, 4-core CPU -> Quantized Int8, tiny models, rule-based NLU
    MID_RANGE = "mid_range"   # 3GB-6GB RAM, 6-8 core CPU -> ONNX Int8 ASR, lightweight TTS, SLM
    HIGH_END = "high_end"     # >= 8GB RAM, NPU/GPU -> Full IndicWhisper tiny/base, VITS TTS


class LocalVoiceConfig(BaseModel):
    mode: RuntimeMode = RuntimeMode.HYBRID
    models_dir: Path = Field(default=Path("/home/rdj/FarmFusionFinal/backend/models/voice"))
    language_packs_dir: Path = Field(
        default=Path("/home/rdj/FarmFusionFinal/backend/app/voice/local/language_packs")
    )
    max_memory_mb: int = 1024
    allow_cellular_download: bool = False
    preferred_device_tier: DeviceTier = DeviceTier.MID_RANGE
    onnx_execution_provider: str = "CPUExecutionProvider"


local_voice_config = LocalVoiceConfig()
