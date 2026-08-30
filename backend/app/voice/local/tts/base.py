"""
Abstract Base Interface for Local Text-to-Speech (TTS) Synthesis in FarmFusion.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel, Field


class LocalTTSResult(BaseModel):
    audio_bytes: bytes
    sample_rate: int = 22050
    duration_seconds: float = 0.0
    audio_format: str = "audio/wav"
    requested_language: str
    requested_dialect: Optional[str] = None
    actual_tts_language: str
    actual_tts_dialect: Optional[str] = None
    is_native: bool = False
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    model_id: Optional[str] = None
    provider: str = "local_tts_engine"
    error: Optional[str] = None


class LocalTTSModel(ABC):
    @abstractmethod
    def load(self) -> bool:
        """Load local TTS model weights or initialize acoustic synthesizer."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if local TTS is ready for inference."""
        pass

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Check if language has genuine local synthesis support."""
        pass

    @abstractmethod
    def supports_dialect(self, dialect: str) -> bool:
        """Check if dialect has genuine native local synthesis support."""
        pass

    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """Return model metadata and runtime capabilities."""
        pass

    @abstractmethod
    async def synthesize(self, text: str, language: str = "hi", dialect: Optional[str] = None) -> LocalTTSResult:
        """Synthesize natural speech audio buffer for given text and language/dialect."""
        pass

    @abstractmethod
    async def stream(self, text: str, language: str = "hi", dialect: Optional[str] = None) -> AsyncIterator[bytes]:
        """Stream chunks of synthesized audio bytes."""
        pass
