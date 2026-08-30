"""
Voice Runtime Router for FarmFusion Local Voice Intelligence Layer.
Coordinates local models, cloud providers (Bhashini), language packs, and execution modes (OFFLINE, HYBRID, ONLINE).
"""
from typing import Dict, Any, Optional
import structlog
from pydantic import BaseModel, Field

from app.voice.local.config import RuntimeMode, local_voice_config
from app.voice.local.capabilities import detect_device_capabilities, DeviceCapabilities
from app.voice.local.model_registry import local_model_registry
from app.voice.local.package_manager import language_package_manager
from app.voice.local.asr import LocalASREngine
from app.voice.local.lid import LocalLanguageDetectorEngine
from app.voice.local.dialect import LocalDialectEngine
from app.voice.local.nlu import LocalAgriculturalNLUEngine
from app.voice.local.response import LocalResponseEngine
from app.voice.local.tts import LocalTTSEngine
from app.voice.bhashini import BhashiniClient
from app.orchestrator.graph import run_orchestrator_pipeline

logger = structlog.get_logger(__name__)


class VoiceRuntimeResult(BaseModel):
    user_input: str
    transcription: str
    detected_language: str
    detected_dialect: Optional[str] = None
    intent: str
    action: str
    response_text: str
    tool_output: Optional[Dict[str, Any]] = None
    runtime_mode: RuntimeMode
    asr_provider: str
    nlu_provider: str
    tts_provider: str
    tts_language: str
    native_tts: bool
    fallback_used: bool
    fallback_reason: Optional[str] = None
    audio_bytes: bytes = b""


class VoiceRuntimeRouter:
    """
    Modular Voice Runtime Router supporting OFFLINE, HYBRID, and ONLINE execution modes.
    """
    def __init__(self, mode: Optional[RuntimeMode] = None):
        self.mode = mode or local_voice_config.mode
        self.device_caps: DeviceCapabilities = detect_device_capabilities()
        self.asr_engine = LocalASREngine()
        self.lid_engine = LocalLanguageDetectorEngine()
        self.dialect_engine = LocalDialectEngine()
        self.nlu_engine = LocalAgriculturalNLUEngine()
        self.response_engine = LocalResponseEngine()
        self.tts_engine = LocalTTSEngine()
        self.bhashini_client = BhashiniClient()

    def set_mode(self, mode: RuntimeMode):
        self.mode = mode
        logger.info("runtime_mode_changed", new_mode=mode)

    async def process_voice_query(
        self,
        audio_bytes: Optional[bytes] = None,
        text_query: Optional[str] = None,
        language_hint: Optional[str] = None,
        farmer_context: Optional[Dict[str, Any]] = None,
    ) -> VoiceRuntimeResult:
        """
        Execute full end-to-end voice query processing with mode-aware provider routing.
        """
        asr_provider = "none"
        transcription = text_query or ""
        fallback_used = False
        fallback_reason = None

        # 1. Speech Recognition (ASR)
        if audio_bytes and len(audio_bytes) > 0:
            if self.mode == RuntimeMode.OFFLINE:
                if self.asr_engine.is_available():
                    asr_res = await self.asr_engine.transcribe(audio_bytes, language=language_hint or "hi")
                    transcription = asr_res.transcription
                    asr_provider = "local_onnx"
                else:
                    return VoiceRuntimeResult(
                        user_input="",
                        transcription="",
                        detected_language=language_hint or "hi",
                        intent="error",
                        action="error",
                        response_text="ऑफलाइन मोड: लोकल ASR मॉडल डिवाइस पर इनस्टॉल नहीं है।",
                        runtime_mode=self.mode,
                        asr_provider="local_unavailable",
                        nlu_provider="none",
                        tts_provider="none",
                        tts_language=language_hint or "hi",
                        native_tts=False,
                        fallback_used=True,
                        fallback_reason="Local ASR model not installed on device in offline mode",
                    )
            elif self.mode == RuntimeMode.HYBRID:
                if self.asr_engine.is_available():
                    asr_res = await self.asr_engine.transcribe(audio_bytes, language=language_hint or "hi")
                    transcription = asr_res.transcription
                    asr_provider = "local_onnx"
                else:
                    # Graceful fallback to Bhashini
                    b_res = await self.bhashini_client.transcribe_audio(audio_bytes, language=language_hint or "hi")
                    transcription = b_res.get("transcription", "")
                    asr_provider = "bhashini_cloud"
                    fallback_used = True
                    fallback_reason = "Local ASR model not installed; routed to Bhashini cloud provider."
            else: # ONLINE
                b_res = await self.bhashini_client.transcribe_audio(audio_bytes, language=language_hint or "hi")
                transcription = b_res.get("transcription", "")
                asr_provider = "bhashini_cloud"

        # 2. Local Language & Dialect Identification
        lid_res = self.lid_engine.detect_language(transcription)
        detected_lang = language_hint or lid_res.detected_language
        dialect_res = self.dialect_engine.detect_and_normalize(transcription, detected_language=detected_lang)
        detected_dialect = dialect_res.detected_dialect

        # 3. NLU & Semantic Tool Execution
        if self.mode == RuntimeMode.OFFLINE:
            # Local NLU & offline-safe tool execution
            nlu_res = await self.nlu_engine.parse(transcription, language=detected_lang, dialect=detected_dialect)
            nlu_provider = "local_nlu_rule_engine"
            
            # Offline tool execution (no live weather/mandi network fabrication)
            if nlu_res.intent in ["weather", "mandi"]:
                tool_output = {"error": "OFFLINE_NETWORK_REQUIRED", "message": "Live weather and mandi prices require an active network connection."}
                response_text = "ऑफलाइन मोड: वर्तमान मौसम और लाइव मंडी भाव देखने के लिए इंटरनेट कनेक्शन की आवश्यकता है।"
                action = "show_result"
            else:
                # Local crop recommendation & agronomic knowledge rules
                turn_result = await run_orchestrator_pipeline(
                    user_input=transcription,
                    detected_language=detected_lang,
                    detected_dialect=detected_dialect,
                    farmer_context=farmer_context or {},
                )
                tool_output = turn_result.get("tool_output")
                response_text = turn_result.get("final_response", "")
                action = turn_result.get("action", "show_result")
        else:
            # HYBRID & ONLINE mode: Run full LangGraph Orchestrator & real ToolRegistry
            nlu_provider = "langgraph_orchestrator"
            turn_result = await run_orchestrator_pipeline(
                user_input=transcription,
                detected_language=detected_lang,
                detected_dialect=detected_dialect,
                farmer_context=farmer_context or {},
            )
            tool_output = turn_result.get("tool_output")
            response_text = turn_result.get("final_response", "")
            action = turn_result.get("action", "show_result")

        # 4. Text-to-Speech (TTS) Synthesis
        tts_provider = "none"
        tts_audio = b""
        tts_lang = detected_lang
        native_tts = False

        if self.mode == RuntimeMode.OFFLINE:
            if self.tts_engine.is_available() and self.tts_engine.supports_language(detected_lang) and (not detected_dialect):
                tts_res = await self.tts_engine.synthesize(
                    response_text,
                    language=detected_lang,
                    dialect=detected_dialect
                )
                tts_audio = tts_res.audio_bytes
                tts_provider = tts_res.provider
                tts_lang = tts_res.actual_tts_language
                native_tts = tts_res.is_native
            else:
                tts_provider = "local_tts_unavailable"
                tts_lang = detected_lang
                native_tts = False
                fallback_used = True
                fallback_reason = f"OFFLINE_TTS_UNAVAILABLE: Real neural TTS model weights for {detected_lang} are not installed on this device."
        elif self.mode == RuntimeMode.HYBRID:
            if self.tts_engine.is_available() and self.tts_engine.supports_language(detected_lang) and (not detected_dialect):
                tts_res = await self.tts_engine.synthesize(
                    response_text,
                    language=detected_lang,
                    dialect=detected_dialect
                )
                tts_audio = tts_res.audio_bytes
                tts_provider = tts_res.provider
                tts_lang = tts_res.actual_tts_language
                native_tts = tts_res.is_native
            else:
                # Genuine Cloud Bhashini TTS Fallback
                tts_audio = await self.bhashini_client.generate_tts(
                    response_text,
                    language="hi" if detected_dialect else detected_lang
                )
                tts_provider = "bhashini_cloud"
                tts_lang = "hi" if detected_dialect else detected_lang
                native_tts = (not bool(detected_dialect))
                if detected_dialect:
                    fallback_used = True
                    fallback_reason = f"Dialect {detected_dialect} synthesized via Bhashini Hindi parent TTS."
        else: # ONLINE
            tts_audio = await self.bhashini_client.generate_tts(
                response_text,
                language="hi" if detected_dialect else detected_lang
            )
            tts_provider = "bhashini_cloud"
            tts_lang = "hi" if detected_dialect else detected_lang
            native_tts = (not bool(detected_dialect))

        return VoiceRuntimeResult(
            user_input=transcription,
            transcription=transcription,
            detected_language=detected_lang,
            detected_dialect=detected_dialect,
            intent=turn_result.get("intent", "unknown") if self.mode != RuntimeMode.OFFLINE else nlu_res.intent,
            action=action,
            response_text=response_text,
            tool_output=tool_output,
            runtime_mode=self.mode,
            asr_provider=asr_provider,
            nlu_provider=nlu_provider,
            tts_provider=tts_provider,
            tts_language=tts_lang,
            native_tts=native_tts,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            audio_bytes=tts_audio,
        )


voice_runtime_router = VoiceRuntimeRouter()
