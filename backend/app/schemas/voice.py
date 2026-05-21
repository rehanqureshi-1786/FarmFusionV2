from typing import Optional
from pydantic import BaseModel
from app.models.voice import LanguageType


class VoiceQueryRequest(BaseModel):
    user_id: Optional[int] = None
    text: str
    language: LanguageType = LanguageType.en


class VoiceQueryResponse(BaseModel):
    success: bool
    response: str
