"""
Abstract Base Interface for Local Dialect Understanding.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class LocalDialectResult(BaseModel):
    parent_language: str
    detected_dialect: Optional[str] = None
    confidence: float
    support_tier: int
    is_native: bool = True
    evidence: List[str] = []
    normalized_text: Optional[str] = None


class LocalDialectModel(ABC):
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
    def detect_and_normalize(self, text: str, detected_language: str = "hi") -> LocalDialectResult:
        pass
