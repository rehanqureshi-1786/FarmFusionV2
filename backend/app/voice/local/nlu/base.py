"""
Abstract Base Interface for Local Agricultural Natural Language Understanding (NLU).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class LocalNLUResult(BaseModel):
    intent: str
    confidence: float
    slots: Dict[str, Any] = Field(default_factory=dict)
    canonical_action: str
    safety_classification: str = "READ_ONLY"
    requires_clarification: bool = False
    clarification_question: Optional[str] = None


class LocalAgriculturalNLU(ABC):
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
    async def parse(self, text: str, language: str = "hi", dialect: Optional[str] = None) -> LocalNLUResult:
        pass
