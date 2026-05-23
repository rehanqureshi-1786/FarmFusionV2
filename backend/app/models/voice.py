"""
Voice Assistant Models - Pydantic schemas for voice/text input processing
These models define the data structure for the multilingual voice assistant
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class IntentType(str, Enum):
    """
    Supported intent types for the voice assistant.
    These represent the main actions a farmer can request.
    """
    GET_WEATHER = "get_weather"
    GET_MANDI_PRICE = "get_mandi_price"
    CROP_PREDICTION = "crop_prediction"
    DISEASE_DETECTION = "disease_detection"
    GENERAL_QUERY = "general_query"
    UNKNOWN = "unknown"


class LanguageType(str, Enum):
    """
    Supported languages for communication with farmers.
    The system auto-detects and responds in the same language.
    """
    HINDI = "hi"           # Pure Hindi (Devanagari)
    ENGLISH = "en"         # English
    HINGLISH = "hi-en"     # Mixed Hindi-English (Romanized Hindi)
    MARATHI = "mr"         # Marathi
    GUJARATI = "gu"        # Gujarati
    PUNJABI = "pa"         # Punjabi
    TAMIL = "ta"           # Tamil
    TELUGU = "te"          # Telugu
    KANNADA = "kn"         # Kannada
    MALAYALAM = "ml"       # Malayalam
    BENGALI = "bn"         # Bengali
    UNKNOWN = "unknown"


class ActionType(str, Enum):
    """
    Actions that the system can take in response to user intent.
    These guide the Android app on what to do next.
    """
    FETCH_DATA = "fetch_data"           # Retrieve data from APIs
    SHOW_RESULT = "show_result"          # Display information to user
    OPEN_CAMERA = "open_camera"          # Open camera for disease detection
    NAVIGATE = "navigate"                # Navigate to another screen
    ASK_CLARIFICATION = "ask_clarification"  # Ask user for more info
    ERROR = "error"                      # Handle error


# ============ REQUEST MODELS ============

class VoiceQueryRequest(BaseModel):
    """
    Request model for voice/text queries from farmers.

    This is the main input endpoint for the voice assistant.
    The Android app sends the user's transcribed voice or typed text here.

    Example inputs:
    - "गेहूं का रेट क्या है" (Hindi)
    - "gehu ka rate kya hai" (Hinglish)
    - "what is the price of wheat" (English)
    - "ಬೆಳೆ ರೋಗ ಗುರುತಿಸು" (Kannada - identify crop disease)
    """
    query: str = Field(
        ...,
        description="User's voice/text query in any supported language",
        examples=["गेहूं का रेट क्या है", "gehu ka rate kya hai"]
    )
    location: Optional[str] = Field(
        None,
        description="Optional user location for context (auto-detected if not provided)"
    )
    latitude: Optional[float] = Field(
        None,
        description="Optional device latitude for real weather queries"
    )
    longitude: Optional[float] = Field(
        None,
        description="Optional device longitude for real weather queries"
    )
    language_hint: Optional[str] = Field(
        None,
        description="Optional language hint (e.g., 'hi', 'en', 'mr')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "गेहूं का रेट क्या है",
                "location": "Madhya Pradesh",
                "language_hint": "hi"
            }
        }


# ============ INTENT DETECTION MODELS ============

class DetectedIntent(BaseModel):
    """
    Structured output from AI intent detection.

    This model represents how the AI interprets the user's query.
    It extracts entities like crop names, locations, and determines the intent.

    Examples:
    - Input: "गेहूं का रेट क्या है"
    - Output: intent="get_mandi_price", crop="wheat", location="auto"

    - Input: "what's the weather today"
    - Output: intent="get_weather", crop=null, location="auto"
    """
    intent: IntentType = Field(
        ...,
        description="The detected user intent/action type"
    )
    crop: Optional[str] = Field(
        None,
        description="Crop mentioned in the query (normalized to English)"
    )
    location: Optional[str] = Field(
        None,
        description="Location mentioned or 'auto' for user's current location"
    )
    language: LanguageType = Field(
        ...,
        description="Detected language of the query"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence score (0.0 to 1.0)"
    )
    extracted_entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional entities extracted from the query"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "get_mandi_price",
                "crop": "wheat",
                "location": "auto",
                "language": "hi",
                "confidence": 0.95,
                "extracted_entities": {"timeframe": "today"}
            }
        }


# ============ RESPONSE DATA MODELS ============

class WeatherData(BaseModel):
    """Weather information for a location"""
    location: str
    temperature_c: float
    condition: str
    humidity: int
    wind_speed: float
    forecast: str
    advice: str


class MandiPriceData(BaseModel):
    """Market price information for a crop"""
    crop: str
    market_name: str
    price_per_quintal: float
    price_trend: str  # "up", "down", "stable"
    last_updated: str


class CropPredictionData(BaseModel):
    """Crop recommendation data"""
    recommended_crops: List[str]
    soil_type: Optional[str]
    confidence: float
    reasoning: str


class DiseaseDetectionData(BaseModel):
    """Disease detection action data"""
    action: str = "open_camera"
    message: str
    instructions: str


# ============ MAIN RESPONSE MODEL ============

class VoiceQueryResponse(BaseModel):
    """
    Response model for voice queries.

    This is the main output that the Android app receives.
    It contains everything needed to respond to the farmer:
    - What the user wanted (intent)
    - What action to take (action)
    - What to say/show the user (response)
    - Additional data for display (data)

    Example response for "गेहूं का रेट क्या है":
    {
        "intent": "get_mandi_price",
        "action": "show_result",
        "response": "गेहूं का रेट आज ₹2,150 प्रति क्विंटल है",
        "data": {...}
    }
    """
    intent: IntentType = Field(
        ...,
        description="Detected intent from user query"
    )
    action: ActionType = Field(
        ...,
        description="Action for the Android app to perform"
    )
    response: str = Field(
        ...,
        description="Natural language response in user's language"
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Structured data relevant to the intent"
    )
    detected_language: LanguageType = Field(
        ...,
        description="Language detected from user query"
    )
    confidence: float = Field(
        ...,
        description="Confidence score for the intent detection"
    )
    follow_up_suggestions: Optional[List[str]] = Field(
        None,
        description="Suggested follow-up questions/actions"
    )
    timestamp: str = Field(
        ...,
        description="ISO format timestamp of the response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "get_mandi_price",
                "action": "show_result",
                "response": "गेहूं का वर्तमान भाव ₹2,150 प्रति क्विंटल है। मध्य प्रदेश में भाव स्थिर हैं।",
                "data": {
                    "crop": "wheat",
                    "price": 2150,
                    "unit": "per quintal",
                    "trend": "stable"
                },
                "detected_language": "hi",
                "confidence": 0.95,
                "follow_up_suggestions": [
                    "चावल का भाव क्या है?",
                    "अगले महीने का अनुमान"
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# ============ ERROR MODELS ============

class VoiceAssistantError(BaseModel):
    """Error response for voice assistant"""
    error: str
    message: str
    detected_language: LanguageType = LanguageType.HINDI
    suggestions: Optional[List[str]] = None
