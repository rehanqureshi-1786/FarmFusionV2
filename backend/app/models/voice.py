from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class IntentType(str, Enum):
    query_weather = "query_weather"
    query_market = "query_market"
    report_issue = "report_issue"


class LanguageType(str, Enum):
    en = "en"
    hi = "hi"


class ActionType(str, Enum):
    recommend_crop = "recommend_crop"
    check_health = "check_health"


class DetectedIntent(BaseModel):
    intent: IntentType
    confidence: float


class VoiceQueryRequest(BaseModel):
    user_id: Optional[int] = None
    text: str
    language: LanguageType = LanguageType.en


class VoiceQueryResponse(BaseModel):
    success: bool
    response: str


class VoiceAssistantError(BaseModel):
    message: str
