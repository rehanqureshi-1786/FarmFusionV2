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
from pydantic import BaseModel, Field
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
from typing import List, Dict, Any, Optional
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
        from datetime import datetime
        logger.info(f"Processing voice query: {request.query[:50]}...")

        # Validate input
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        # Execute LangGraph Multilingual Orchestrator Pipeline
        farmer_context = {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "location_name": request.location
        }
        turn_result = await run_orchestrator_pipeline(
            user_input=request.query,
            detected_language=request.language_hint or "hi",
            farmer_context=farmer_context
        )

        intent = turn_result.get("intent", "unknown")

        # Determine client ActionType
        if intent == "navigation":
            action = ActionType.NAVIGATE.value
        elif intent == "disease":
            action = ActionType.OPEN_CAMERA.value
        elif turn_result.get("requires_consequential_confirmation") or intent == "consequential_action":
            action = ActionType.CONFIRM_ACTION.value
        elif turn_result.get("requires_clarification") or intent == "clarify":
            action = ActionType.ASK_CLARIFICATION.value
        else:
            action = ActionType.SHOW_RESULT.value

        # Build follow-up suggestions based on intent and turn
        if intent == "weather":
            suggestions = ["कल बारिश होगी क्या?", "फसल की सलाह दो"]
        elif intent == "crop_recommendation":
            suggestions = ["पहली वाली क्यों?", "गेहूं का मंडी भाव क्या है?"]
        elif intent == "mandi":
            suggestions = ["इस फसल की देखभाल कैसे करें?", "मौसम कैसा रहेगा?"]
        elif intent == "explain_recommendation":
            suggestions = ["अगर बारिश कम हो जाए तो?", "मंडी भाव बताओ"]
        else:
            suggestions = ["आज मौसम कैसा है?", "खेत में क्या बोएं?", "मंडी भाव बताओ"]

        # Real Local Neural TTS Synthesis for Android Farm Assistant
        from app.voice.local.tts.local_tts import local_tts_engine
        from app.voice.provider_router import universal_voice_router
        import base64

        final_text = turn_result.get("final_response", "")
        resp_lang = turn_result.get("response_language") or turn_result.get("detected_language") or request.language_hint or "hi"
        resp_dialect = turn_result.get("response_dialect") or turn_result.get("detected_dialect")

        tts_decision = universal_voice_router.route_tts(resp_lang, dialect=resp_dialect)
        audio_b64 = None
        tts_provider_name = tts_decision.selected_provider
        tts_model_name = getattr(tts_decision, "selected_model", None) or getattr(tts_decision, "model_id", None)
        is_native_tts = tts_decision.is_native
        is_local_tts = tts_decision.is_local
        fallback_used = tts_decision.fallback_used
        fallback_reason = tts_decision.fallback_reason
        tts_lang = tts_decision.actual_tts_language
        tts_dial = tts_decision.actual_tts_dialect

        if final_text and local_tts_engine.supports_language(tts_lang):
            try:
                synth_res = await local_tts_engine.synthesize(
                    final_text,
                    language=tts_lang,
                    dialect=tts_dial
                )
                if synth_res and synth_res.audio_bytes:
                    audio_b64 = base64.b64encode(synth_res.audio_bytes).decode("utf-8")
                    tts_provider_name = synth_res.provider
                    tts_model_name = synth_res.model_id
                    is_native_tts = synth_res.is_native
                    is_local_tts = True
                    fallback_used = synth_res.fallback_used
                    fallback_reason = synth_res.fallback_reason
            except Exception as e:
                logger.warning(f"Local TTS synthesis failed: {e}")

        response = VoiceQueryResponse(
            intent=intent,
            action=action,
            response=final_text,
            data=turn_result.get("tool_output"),
            detected_language=turn_result.get("detected_language", request.language_hint or "hi"),
            detected_dialect=turn_result.get("detected_dialect"),
            confidence=float(turn_result.get("intent_confidence", 0.9)),
            input_language=turn_result.get("detected_language", "hi"),
            input_dialect=turn_result.get("detected_dialect"),
            response_language=resp_lang,
            response_dialect=resp_dialect,
            tts_language=tts_lang,
            tts_dialect=tts_dial,
            tts_provider=tts_provider_name,
            tts_model=tts_model_name,
            native_tts=is_native_tts,
            local_tts=is_local_tts,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            audio_base64=audio_b64,
            audio_format="audio/wav" if audio_b64 else None,
            follow_up_suggestions=suggestions,
            timestamp=datetime.now().isoformat()
        )

        logger.info(f"Query processed successfully. Intent: {response.intent}, Dialect: {response.detected_dialect}, Native TTS: {response.native_tts}, Has Audio: {bool(response.audio_base64)}")
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
    from app.voice.languages import LANGUAGE_REGISTRY
    from app.voice.providers import voice_provider_manager

    languages_list = []
    for code, prof in LANGUAGE_REGISTRY.items():
        caps = voice_provider_manager.get_capabilities(code)
        languages_list.append({
            "code": prof.canonical_code,
            "name": prof.name,
            "name_native": prof.native_name,
            "script": prof.script,
            "is_dialect": prof.is_dialect,
            "parent_language": prof.parent_language,
            "support_tier": prof.support_tier,
            "status": caps["status"],
            "asr": {
                "native": prof.asr.native_supported,
                "fallback": prof.asr.fallback_code is not None,
                "fallback_code": prof.asr.fallback_code,
            },
            "tts": {
                "native": prof.tts.native_supported,
                "fallback": prof.tts.fallback_code is not None,
                "fallback_code": prof.tts.fallback_code,
            },
            "vocabulary_normalization": prof.supports_agricultural_vocabulary,
            "code_switching": True,
        })

    return {
        "languages": languages_list,
        "total_languages": len(languages_list),
        "auto_detect": True,
        "recommended": ["hi", "hi-en", "en"],
        "message": "Language and regional dialects are automatically detected from input. Non-native TTS gracefully falls back to verified parent languages."
    }


@router.get("/capabilities", summary="Get overall voice platform capabilities")
async def get_all_voice_capabilities():
    """Returns platform capability summary across all supported languages and providers."""
    from app.voice.languages import LANGUAGE_REGISTRY
    from app.voice.providers import get_language_capability
    caps = {code: get_language_capability(code) for code in LANGUAGE_REGISTRY.keys()}
    return {
        "platform": "FarmFusion Voice Platform",
        "total_languages": len(caps),
        "native_voice_languages": sum(1 for c in caps.values() if c["status"] == "NATIVE"),
        "parent_fallback_varieties": sum(1 for c in caps.values() if c["status"] == "PARENT_FALLBACK"),
        "capabilities": caps,
    }


@router.get("/languages/{language_code}", summary="Get capability for a specific language or dialect")
async def get_single_language_capability(language_code: str):
    """Returns detailed machine-readable capability for a specific language or dialect code."""
    from app.voice.providers import get_language_capability
    return get_language_capability(language_code)


@router.get("/dialects", summary="Get supported regional dialects and varieties")
async def get_supported_dialects():
    """Returns list of audited regional dialects with parent fallback mapping."""
    from app.voice.languages import LANGUAGE_REGISTRY
    dialects = [
        {
            "code": p.canonical_code,
            "name": p.name,
            "native_name": p.native_name,
            "parent_language": p.parent_language,
            "support_tier": p.support_tier,
            "fallback_tts": p.fallback_language,
        }
        for p in LANGUAGE_REGISTRY.values() if p.is_dialect
    ]
    return {"total_dialects": len(dialects), "dialects": dialects}


@router.get("/providers", summary="Get active voice ASR and TTS providers")
async def get_voice_providers():
    """Returns active speech and translation provider metadata with Truthful Model Status."""
    from app.voice.local.tts.local_tts import local_tts_engine
    return {
        "asr": {
            "primary": "MeitY Bhashini ASR (ULCA pipeline)",
            "local_fallback": "Local Conformer Int8 / IndicWhisper (When binary installed)",
            "streaming_supported": True,
        },
        "tts": {
            "primary": "MeitY Bhashini TTS API (Verified Cloud Native TTS)",
            "local_engine": "FarmFusion Local Neural TTS Engine (ONNX / VITS / Indic-TTS)",
            "local_weights_installed": local_tts_engine.is_available(),
            "parent_fallback": "Bhashini Hindi TTS for regional dialects",
            "caching": "Redis (tts:{lang}:{hash})",
            "streaming_supported": True,
        },
        "nlu_normalization": "FarmFusion Local Multilingual NLU + 19-Category Agricultural Catalog",
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
            "languages": 14,
            "dialects": 7,
            "actions": ["show_result", "open_camera", "fetch_data", "ask_clarification", "navigate", "error"],
            "intents": 18
        }
    }


# ============ LOCAL VOICE AGENT ENDPOINTS ============

from app.voice.local.runtime import voice_runtime_router, RuntimeMode
from app.voice.local.model_registry import local_model_registry
from app.voice.local.package_manager import language_package_manager
from app.voice.local.capabilities import detect_device_capabilities


@router.get(
    "/local/status",
    summary="Get Local Voice Agent status and capabilities"
)
async def get_local_voice_status():
    """
    Returns current local voice agent status, device capability tier,
    active runtime mode, and available local models.
    """
    device_info = detect_device_capabilities()
    manifests = local_model_registry.list_manifests()
    return {
        "runtime_mode": voice_runtime_router.mode.value,
        "device_tier": device_info.tier.value,
        "device_capabilities": {
            "total_ram_mb": device_info.total_ram_mb,
            "cpu_count": device_info.cpu_count,
            "cpu_arch": device_info.cpu_arch,
            "supported_runtimes": device_info.supported_runtimes,
        },
        "engines": {
            "asr": voice_runtime_router.asr_engine.capabilities(),
            "nlu": voice_runtime_router.nlu_engine.capabilities(),
            "dialect": voice_runtime_router.dialect_engine.capabilities(),
            "tts": voice_runtime_router.tts_engine.capabilities(),
            "language_detector": voice_runtime_router.lid_engine.capabilities(),
        },
        "registered_models": [
            {
                "model_id": m.model_id,
                "task": m.task.value,
                "language": m.language,
                "dialect": m.dialect,
                "version": m.version,
                "status": local_model_registry.get_model_status(m.model_id).value,
                "size_mb": m.size_mb,
            }
            for m in manifests
        ]
    }


@router.get(
    "/local/language-packs",
    summary="List available and installed language packs"
)
async def list_local_language_packs():
    """
    Returns metadata for all installed modular language packs.
    """
    packs = language_package_manager.list_installed_packs()
    return {
        "total_packs": len(packs),
        "packs": [
            {
                "pack_id": p.pack_id,
                "language": p.language,
                "dialect": p.dialect,
                "name": p.name,
                "native_name": p.native_name,
                "version": p.version,
                "support_tier": p.support_tier,
                "status": p.status,
                "size_kb": p.size_kb,
            }
            for p in packs
        ]
    }


class SetRuntimeModeRequest(BaseModel):
    mode: str = Field(..., description="Runtime mode: offline, hybrid, or online")


@router.post(
    "/local/mode",
    summary="Set Voice Runtime Mode (offline, hybrid, online)"
)
async def set_voice_runtime_mode(req: SetRuntimeModeRequest):
    """
    Switch active voice runtime mode between offline, hybrid, and online.
    """
    mode_str = req.mode.lower()
    if mode_str not in [m.value for m in RuntimeMode]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode '{req.mode}'. Must be one of: offline, hybrid, online"
        )
    voice_runtime_router.set_mode(RuntimeMode(mode_str))
    return {
        "status": "success",
        "current_mode": voice_runtime_router.mode.value
    }


class LocalVoiceQueryRequest(BaseModel):
    query: str = Field(..., description="Farmer text query")
    language_hint: Optional[str] = Field("hi", description="BCP-47 language code hint")
    dialect_hint: Optional[str] = Field(None, description="Optional dialect code e.g. rwr, mew")


@router.post(
    "/local/query",
    summary="Execute query using Local Voice Agent"
)
async def process_local_voice_query(req: LocalVoiceQueryRequest):
    """
    Processes farmer query through the local voice runtime router.
    Enforces zero fabrication and returns structured response.
    """
    res = await voice_runtime_router.process_voice_query(
        text_query=req.query,
        language_hint=req.language_hint,
    )
    return {
        "response_text": res.response_text,
        "runtime_mode": res.runtime_mode.value,
        "detected_language": res.detected_language,
        "detected_dialect": res.detected_dialect,
        "intent": res.intent,
        "action": res.action,
        "native_tts": res.native_tts,
        "fallback_used": res.fallback_used,
        "fallback_reason": res.fallback_reason,
        "tool_output": res.tool_output,
    }

