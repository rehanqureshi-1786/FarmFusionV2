"""
Voice Assistant API Routes

This module provides the main voice/text input endpoint for FarmFusion.
Farmers can send their queries in Hindi, Hinglish, English, or regional languages.

Endpoints:
- POST /voice - Main voice/text query endpoint
- POST /voice/text - Alternative text-only endpoint
- GET /voice/languages - Get supported languages
- GET /voice/intents - Get supported intents
"""
from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from app.orchestrator.graph import run_orchestrator_pipeline
from app.voice.bhashini import BhashiniClient
from app.models.voice import (
    VoiceQueryRequest,
    VoiceQueryResponse,
    VoiceAssistantError,
    IntentType,
    LanguageType,
    ActionType,
    DetectedIntent
)
from app.services.voice_service import voice_service
from typing import List, Dict, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/voice", tags=["voice-assistant"])


@router.websocket("/session")
async def voice_session_websocket(websocket: WebSocket):
    """
    WS /voice/session
    Real-time streaming voice WebSocket session connecting Android app to Bhashini ASR/TTS and LangGraph Orchestrator.
    """
    await websocket.accept()
    logger.info("voice_websocket_connected")
    bhashini = BhashiniClient()
    try:
        while True:
            # Receive text payload or audio bytes
            data = await websocket.receive_text()
            logger.info("voice_ws_message_received", message=data)
            
            # Transcribe audio if needed or run orchestrator directly on query text
            orchestrator_result = await run_orchestrator_pipeline(
                user_input=data,
                detected_language="hi",
                session_id="ws_session"
            )
            
            # Generate TTS audio for final response
            final_text = orchestrator_result.get("final_response", "")
            tts_audio = await bhashini.generate_tts(final_text, language="hi")
            
            await websocket.send_json({
                "response_text": final_text,
                "intent": orchestrator_result.get("intent"),
                "detected_language": orchestrator_result.get("detected_language"),
                "requires_clarification": orchestrator_result.get("requires_clarification"),
                "tts_audio_base64": tts_audio.hex()
            })
    except WebSocketDisconnect:
        logger.info("voice_websocket_disconnected")
    except Exception as e:
        logger.error("voice_websocket_error", error=str(e))
        await websocket.close()



# ============ MAIN VOICE ENDPOINT ============

@router.post(
    "",
    response_model=VoiceQueryResponse,
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Bad request - invalid input"},
        500: {"description": "Internal server error"},
    }
)
async def process_voice_query(request: VoiceQueryRequest) -> VoiceQueryResponse:
    """
    # 🎤 FarmFusion Voice Assistant - Main Endpoint

    This is the primary endpoint for processing farmer voice/text queries.
    It uses AI to understand the query in Hindi, Hinglish, English, or regional languages.

    ## Features:
    - 🧠 **AI-Powered Intent Detection**: Automatically understands what the farmer wants
    - 🌐 **Multilingual**: Supports Hindi, Hinglish, English, Marathi, Gujarati, etc.
    - 🎯 **Smart Actions**: Returns appropriate actions for the Android app
    - 💬 **Natural Responses**: Generates responses in the same language as input

    ## Supported Intents:
    - **get_weather**: "mausam kaisa hai", "what's the weather"
    - **get_mandi_price**: "gehu ka rate", "wheat price", "भाव क्या है"
    - **crop_prediction**: "konsi fasal", "which crop to grow", "क्या बोएं"
    - **disease_detection**: "paudhe ki bimari", "plant disease", "रोग पहचान"
    - **general_query**: Any other farming questions

    ## Example Requests:

    ### Hindi Query:
    ```json
    {
        "query": "गेहूं का रेट क्या है",
        "location": "Madhya Pradesh",
        "language_hint": "hi"
    }
    ```

    ### Hinglish Query:
    ```json
    {
        "query": "gehu ka rate kya hai",
        "location": "Punjab"
    }
    ```

    ### English Query:
    ```json
    {
        "query": "what's the weather today?",
        "location": "Nagpur"
    }
    ```

    ## Example Response:
    ```json
    {
        "intent": "get_mandi_price",
        "action": "show_result",
        "response": "गेहूं का वर्तमान भाव ₹2,150 प्रति क्विंटल है। भाव स्थिर हैं।",
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
    ```

    ## Action Types:
    - **show_result**: Display the response to user
    - **fetch_data**: Android should fetch additional data
    - **open_camera**: Open camera for disease detection
    - **navigate**: Navigate to another screen
    - **ask_clarification**: Ask user for more information

    ## Error Handling:
    - Returns 400 for invalid input
    - Returns 500 for server errors
    - Always returns a user-friendly error message

    ## Rate Limits:
    - 20 requests/minute (Groq API free tier)
    """
    try:
        logger.info(f"Processing voice query: {request.query[:50]}...")

        # Validate input
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        # Process the query using the voice service
        response = await voice_service.process_query(request)

        logger.info(f"Query processed successfully. Intent: {response.intent}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


# Alternative endpoint for text-only queries (more explicit)
@router.post(
    "/text",
    response_model=VoiceQueryResponse,
    summary="Process text query (alternative endpoint)"
)
async def process_text_query(request: VoiceQueryRequest) -> VoiceQueryResponse:
    """
    # Alternative Text Query Endpoint

    Same functionality as the main `/voice` endpoint, but explicitly for text.
    Use this if you want to clearly indicate the input is text (not audio).

    ## Request Body:
    Same as `/voice` endpoint

    ## Response:
    Same as `/voice` endpoint
    """
    return await process_voice_query(request)


# ============ UTILITY ENDPOINTS ============

@router.get(
    "/languages",
    response_model=Dict[str, Any],
    summary="Get supported languages"
)
async def get_supported_languages():
    """
    # Supported Languages

    Returns a list of languages supported by the voice assistant.
    The system automatically detects the language from the input.

    ## Response:
    ```json
    {
        "languages": [
            {"code": "hi", "name": "Hindi", "script": "Devanagari"},
            {"code": "hi-en", "name": "Hinglish", "script": "Roman"},
            {"code": "en", "name": "English", "script": "Latin"},
            ...
        ],
        "auto_detect": true
    }
    ```
    """
    languages = [
        {"code": "hi", "name": "Hindi", "name_native": "हिन्दी", "script": "Devanagari"},
        {"code": "hi-en", "name": "Hinglish", "name_native": "हिंग्लिश", "script": "Roman"},
        {"code": "en", "name": "English", "name_native": "English", "script": "Latin"},
        {"code": "mr", "name": "Marathi", "name_native": "मराठी", "script": "Devanagari"},
        {"code": "gu", "name": "Gujarati", "name_native": "ગુજરાતી", "script": "Gujarati"},
        {"code": "pa", "name": "Punjabi", "name_native": "ਪੰਜਾਬੀ", "script": "Gurmukhi"},
        {"code": "ta", "name": "Tamil", "name_native": "தமிழ்", "script": "Tamil"},
        {"code": "te", "name": "Telugu", "name_native": "తెలుగు", "script": "Telugu"},
        {"code": "kn", "name": "Kannada", "name_native": "ಕನ್ನಡ", "script": "Kannada"},
        {"code": "ml", "name": "Malayalam", "name_native": "മലയാളം", "script": "Malayalam"},
        {"code": "bn", "name": "Bengali", "name_native": "বাংলা", "script": "Bengali"},
    ]

    return {
        "languages": languages,
        "auto_detect": True,
        "recommended": ["hi", "hi-en", "en"],
        "message": "Language is automatically detected from the input. No need to specify manually."
    }


@router.get(
    "/intents",
    response_model=Dict[str, Any],
    summary="Get supported intents"
)
async def get_supported_intents():
    """
    # Supported Intents

    Returns a list of actions/intents the voice assistant can handle.
    Each intent represents a type of question or request from farmers.

    ## Response:
    ```json
    {
        "intents": [
            {
                "code": "get_weather",
                "name": "Weather Information",
                "examples": ["mausam kaisa hai", "what's the weather"],
                "actions": ["fetch_weather", "show_forecast"]
            },
            ...
        ]
    }
    ```
    """
    intents = [
        {
            "code": "get_weather",
            "name": "Weather Information",
            "description": "Get current weather and forecast",
            "examples": [
                "mausam kaisa hai",
                "कल बारिश होगी",
                "what's the weather today",
                "temperature kitna hai"
            ],
            "actions": ["fetch_data", "show_result"]
        },
        {
            "code": "get_mandi_price",
            "name": "Market Prices",
            "description": "Get current crop prices from mandi/market",
            "examples": [
                "gehu ka rate kya hai",
                "गेहूं का भाव",
                "wheat price today",
                "chawal ka daam"
            ],
            "actions": ["fetch_data", "show_result"]
        },
        {
            "code": "crop_prediction",
            "name": "Crop Recommendation",
            "description": "Get recommendations for which crop to grow",
            "examples": [
                "konsi fasal lagau",
                "मुझे क्या बोना चाहिए",
                "which crop should I grow",
                "best crop for my land"
            ],
            "actions": ["fetch_data", "show_result"]
        },
        {
            "code": "disease_detection",
            "name": "Disease Detection",
            "description": "Identify crop diseases from photos or symptoms",
            "examples": [
                "paudhe pe kida lag gaye",
                "पत्ते पीले हो रहे हैं",
                "my plant is dying",
                "disease check karo"
            ],
            "actions": ["open_camera", "show_result"]
        },
        {
            "code": "general_query",
            "name": "General Questions",
            "description": "Answer general farming questions",
            "examples": [
                "khad kaise dale",
                "सिंचाई कब करें",
                "how to increase yield",
                "farming tips"
            ],
            "actions": ["show_result"]
        }
    ]

    return {
        "intents": intents,
        "count": len(intents),
        "note": "Intents are automatically detected. You don't need to specify them manually."
    }


@router.post(
    "/intent-only",
    response_model=DetectedIntent,
    summary="Get only intent detection (debugging)"
)
async def detect_intent_only(request: VoiceQueryRequest) -> DetectedIntent:
    """
    # Intent Detection Only (Debug)

    Returns only the intent detection result without executing any actions.
    Useful for debugging and understanding how the AI interprets queries.

    ## Response:
    ```json
    {
        "intent": "get_mandi_price",
        "crop": "wheat",
        "location": "auto",
        "language": "hi-en",
        "confidence": 0.95,
        "extracted_entities": {}
    }
    ```
    """
    try:
        intent = await voice_service.detect_intent(
            query=request.query,
            language_hint=request.language_hint
        )
        return intent
    except Exception as e:
        logger.error(f"Error detecting intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent detection failed: {str(e)}"
        )


@router.get(
    "/examples",
    response_model=Dict[str, Any],
    summary="Get example queries"
)
async def get_example_queries():
    """
    # Example Queries

    Returns example queries in different languages to help test the voice assistant.

    ## Response:
    Various example queries categorized by intent and language.
    """
    examples = {
        "hindi": {
            "get_weather": ["आज मौसम कैसा है?", "कल बारिश होगी क्या?", "तापमान कितना है?"],
            "get_mandi_price": ["गेहूं का रेट क्या है?", "चावल का भाव बताओ", "सरसों का दाम"],
            "crop_prediction": ["मुझे क्या बोना चाहिए?", "कौन सी फसल अच्छी है?", "सलाह दें"],
            "disease_detection": ["पत्ते पीले हो रहे हैं", "कीड़े लग गए हैं", "रोग पहचानें"]
        },
        "hinglish": {
            "get_weather": ["mausam kaisa hai", "kal baarish hogi", "temperature kitna hai"],
            "get_mandi_price": ["gehu ka rate kya hai", "chawal ka bhav", "soybean ka daam"],
            "crop_prediction": ["konsi fasal lagau", "kya beej dalun", "recommend karo"],
            "disease_detection": ["paudhe pe kida lag gaye", "patti pe daag hai", "check karo"]
        },
        "english": {
            "get_weather": ["what's the weather?", "will it rain today?", "temperature please"],
            "get_mandi_price": ["wheat price", "rate of rice", "market rates today"],
            "crop_prediction": ["which crop should I grow?", "best crop for my farm", "recommend crops"],
            "disease_detection": ["my plant has yellow leaves", "identify disease", "pest problem"]
        }
    }

    return {
        "examples": examples,
        "note": "Copy these queries to test the /voice endpoint"
    }


@router.get(
    "/health",
    summary="Voice assistant health check"
)
async def voice_health_check():
    """
    # Health Check

    Simple endpoint to verify the voice assistant is working.

    ## Response:
    ```json
    {
        "status": "healthy",
        "service": "voice-assistant",
        "features": {
            "intent_detection": true,
            "multilingual": true,
            "actions": ["show_result", "open_camera", ...]
        }
    }
    ```
    """
    return {
        "status": "healthy",
        "service": "voice-assistant",
        "version": "1.0.0",
        "features": {
            "intent_detection": True,
            "multilingual": True,
            "languages": 11,
            "actions": ["show_result", "open_camera", "fetch_data", "ask_clarification", "error"],
            "intents": 5
        }
    }
