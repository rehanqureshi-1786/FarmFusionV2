"""
Voice Assistant Models - Pydantic schemas for voice/text input processing
These models define the data structure for the multilingual voice assistant
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from enum import Enum


class IntentType(str, Enum):
    """Supported intent types for the voice assistant."""
    GET_WEATHER = "weather"
    GET_MANDI_PRICE = "mandi"
    CROP_PREDICTION = "crop_recommendation"
    DISEASE_DETECTION = "disease"
    SCHEME = "scheme"
    NAVIGATION = "navigation"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


class LanguageType(str, Enum):
    """Supported languages for communication with farmers."""
    HINDI = "hi"
    ENGLISH = "en"
    HINGLISH = "hi-en"
    MARATHI = "mr"
    GUJARATI = "gu"
    PUNJABI = "pa"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MALAYALAM = "ml"
    BENGALI = "bn"
    ODIA = "or"
    ASSAMESE = "as"
    URDU = "ur"
    MAITHILI = "mai"
    UNKNOWN = "unknown"


class ActionType(str, Enum):
    """Actions that the system can take in response to user intent."""
    FETCH_DATA = "fetch_data"
    SHOW_RESULT = "show_result"
    OPEN_CAMERA = "open_camera"
    NAVIGATE = "navigate"
    ASK_CLARIFICATION = "ask_clarification"
    CONFIRM_ACTION = "confirm_action"
    ERROR = "error"


# ============ REQUEST MODELS ============

class VoiceQueryRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "गेहूं का रेट क्या है",
                "location": "Madhya Pradesh",
                "language_hint": "hi"
            }
        }
    )
    query: str = Field(..., description="User's voice/text query in any supported language")
    location: Optional[str] = Field(None, description="Optional user location")
    latitude: Optional[float] = Field(None, description="Optional device latitude")
    longitude: Optional[float] = Field(None, description="Optional device longitude")
    language_hint: Optional[str] = Field(None, description="Optional language hint (e.g. 'hi', 'en', 'mr')")


# ============ INTENT DETECTION MODELS ============

class DetectedIntent(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "intent": "mandi",
                "crop": "wheat",
                "location": "auto",
                "language": "hi",
                "confidence": 0.95,
                "extracted_entities": {"timeframe": "today"}
            }
        }
    )
    intent: str = Field(..., description="The detected user intent/action type")
    crop: Optional[str] = Field(None, description="Crop mentioned in the query")
    location: Optional[str] = Field(None, description="Location mentioned")
    language: str = Field(..., description="Detected language of the query")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score (0.0 to 1.0)")
    extracted_entities: Dict[str, Any] = Field(default_factory=dict, description="Additional entities extracted")


# ============ RESPONSE DATA MODELS ============

class WeatherData(BaseModel):
    location: str
    temperature_c: float
    condition: str
    humidity: int
    wind_speed: float
    forecast: str
    advice: str


class MandiPriceData(BaseModel):
    crop: str
    market_name: str
    price_per_quintal: float
    price_trend: str
    last_updated: str


class CropPredictionData(BaseModel):
    recommended_crops: List[str]
    soil_type: Optional[str]
    confidence: float
    reasoning: str


class DiseaseDetectionData(BaseModel):
    action: str = "open_camera"
    message: str
    instructions: str


# ============ MAIN RESPONSE MODEL ============

class VoiceQueryResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "intent": "mandi",
                "action": "show_result",
                "response": "गेहूं का वर्तमान भाव ₹2,150 प्रति क्विंटल है।",
                "data": {
                    "crop": "wheat",
                    "price": 2150,
                    "unit": "per quintal",
                    "trend": "stable"
                },
                "detected_language": "hi",
                "detected_dialect": "rwr",
                "confidence": 0.95,
                "input_language": "hi",
                "input_dialect": "rwr",
                "response_language": "hi",
                "response_dialect": "rwr",
                "tts_language": "hi",
                "native_tts": False,
                "fallback_used": True,
                "fallback_reason": "No native Marwari (rwr) TTS voice model available in Bhashini. Using parent language Hindi (hi) TTS.",
                "follow_up_suggestions": [
                    "चावल का भाव क्या है?",
                    "अगले महीने का अनुमान"
                ],
                "timestamp": "2026-08-30T10:30:00Z"
            }
        }
    )
    intent: str = Field(..., description="Detected intent from user query")
    action: str = Field(..., description="Action for the Android app to perform")
    response: str = Field(..., description="Natural language response in user's language/dialect")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured data relevant to the intent")
    detected_language: str = Field(..., description="Language detected from user query")
    detected_dialect: Optional[str] = Field(None, description="Regional dialect detected from user query (e.g. 'rwr', 'mew')")
    confidence: float = Field(..., description="Confidence score for the intent detection")
    input_language: Optional[str] = Field("hi", description="Input language code")
    input_dialect: Optional[str] = Field(None, description="Input regional dialect code")
    response_language: Optional[str] = Field("hi", description="Generated response language code")
    response_dialect: Optional[str] = Field(None, description="Generated response dialect code")
    tts_language: Optional[str] = Field("hi", description="TTS synthesis voice language")
    tts_dialect: Optional[str] = Field(None, description="TTS dialect code")
    tts_provider: Optional[str] = Field(None, description="TTS provider name e.g. local_neural_vits_tts")
    tts_model: Optional[str] = Field(None, description="TTS model ID e.g. farmfusion_tts_hindi_vits_v1")
    native_tts: Optional[bool] = Field(False, description="True if native dialect voice model was used; False if parent fallback")
    local_tts: Optional[bool] = Field(True, description="True if synthesized via local on-device neural weights")
    fallback_used: Optional[bool] = Field(False, description="Whether TTS or ASR fallback was used")
    fallback_reason: Optional[str] = Field(None, description="Reason for fallback if applicable")
    audio_base64: Optional[str] = Field(None, description="Base64-encoded 16kHz 16-bit PCM WAV audio for Android native playback")
    audio_format: Optional[str] = Field("audio/wav", description="MIME format of the synthesized audio")
    follow_up_suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up questions/actions")
    timestamp: str = Field(..., description="ISO format timestamp of the response")

    # F7 typed action survival (requirement #8): the full ResponseEnvelope and its
    # action_payload are passed through so Android can handle ANSWER / NAVIGATE /
    # REQUEST_INPUT / CALL / NOTIFY / CLARIFY directly instead of a legacy intent->action map.
    envelope: Optional[Dict[str, Any]] = Field(None, description="Full F7 ResponseEnvelope payload")
    action_payload: Optional[Dict[str, Any]] = Field(
        None,
        description="F7 StructuredActionPayload {action, destination, android_route, required_input, target_phone, call_reason, ...}",
    )


# ============ ERROR MODELS ============

class VoiceAssistantError(BaseModel):
    error: str
    message: str
    detected_language: str = "hi"
    suggestions: Optional[List[str]] = None
