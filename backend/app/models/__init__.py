"""Model package for FarmFusion."""
from .crop import SoilType, CropStatus, Crop
from .user import User, UserRole
from .voice import (ActionType, DetectedIntent, IntentType, LanguageType,
                    VoiceAssistantError, VoiceQueryRequest, VoiceQueryResponse)

__all__ = [
    "SoilType",
    "CropStatus",
    "Crop",
    "User",
    "UserRole",
    "VoiceQueryRequest",
    "VoiceQueryResponse",
    "DetectedIntent",
    "IntentType",
    "LanguageType",
    "ActionType",
    "VoiceAssistantError",
]
