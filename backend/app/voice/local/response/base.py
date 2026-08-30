"""
Abstract Base Interface for Local Response Generation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LocalResponseResult(BaseModel):
    response_text: str
    response_language: str
    response_dialect: Optional[str] = None
    grounded: bool = True
    model_id: str


class LocalResponseModel(ABC):
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
    async def generate_response(
        self,
        intent: str,
        tool_payload: Dict[str, Any],
        language: str = "hi",
        dialect: Optional[str] = None
    ) -> LocalResponseResult:
        pass
