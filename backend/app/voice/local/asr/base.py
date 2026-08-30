"""
Abstract Base Interface for Local ASR (Speech-to-Text) Models.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LocalASRResult(BaseModel):
    transcription: str
    detected_language: str
    confidence: float
    is_native: bool
    model_id: Optional[str] = None
    error: Optional[str] = None


class LocalASRModel(ABC):
    @abstractmethod
    def load(self) -> bool:
        """Load model into runtime/memory."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Return True only if model binary is loaded and runnable."""
        pass

    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """Return task, supported languages, quantization, and runtime specs."""
        pass

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: str = "hi") -> LocalASRResult:
        """Transcribe raw audio bytes in-memory and guarantee audio cleanup."""
        pass
