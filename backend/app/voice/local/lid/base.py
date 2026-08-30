"""
Abstract Base Interface for Local Language Identification (LID).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class LocalLIDResult(BaseModel):
    detected_language: str
    confidence: float
    is_code_switched: bool = False
    secondary_language: Optional[str] = None
    script: str = "Devanagari"
    evidence: List[str] = []


class LocalLanguageDetector(ABC):
    @abstractmethod
    def load(self) -> bool:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def detect_language(self, text: str) -> LocalLIDResult:
        pass
