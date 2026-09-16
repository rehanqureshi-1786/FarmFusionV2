"""
Bhashini ASR (Speech-to-Text) and TTS (Text-to-Speech) client.
Supports authentic MeitY ULCA pipeline execution with graceful fallback
to Sarvam AI and Local Neural VITS when Bhashini credentials are unavailable
or the remote service encounters errors.
"""
from __future__ import annotations

import base64
import hashlib
import time
from typing import Any, Dict, Optional, Tuple

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

BHASHINI_AUTH_URL = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
BHASHINI_PIPELINE_ID = "64392f96daac500bd5c7043d"

# In-memory cache for Bhashini pipeline auth configurations (TTL: 1 hour)
_pipeline_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


class BhashiniClient:
    def __init__(self):
        self.user_id = settings.bhashini_user_id
        self.api_key = settings.bhashini_api_key
        self._client = httpx.AsyncClient(timeout=15.0)

    @property
    def is_configured(self) -> bool:
        return bool(self.user_id and self.api_key and not self.api_key.startswith("mock_"))

    async def _get_pipeline_config(self, task_type: str, language: str) -> Optional[Dict[str, Any]]:
        """Fetch or retrieve cached pipeline endpoint config from MeitY auth API."""
        if not self.is_configured:
            return None

        cache_key = f"{task_type}:{language}"
        now = time.time()
        if cache_key in _pipeline_cache:
            ts, config = _pipeline_cache[cache_key]
            if now - ts < 3600:
                return config

        headers = {
            "userID": self.user_id,
            "ulcaApiKey": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "pipelineTasks": [
                {
                    "taskType": task_type,
                    "config": {
                        "language": {
                            "sourceLanguage": language[:2],
                        }
                    },
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": BHASHINI_PIPELINE_ID,
            },
        }

        try:
            resp = await self._client.post(BHASHINI_AUTH_URL, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                _pipeline_cache[cache_key] = (now, data)
                return data
            logger.warning("bhashini_pipeline_config_http_error", status=resp.status_code)
        except Exception as exc:
            logger.warning("bhashini_pipeline_config_failed", error=str(exc))
        return None

    async def transcribe_audio(self, audio_bytes: bytes, language: str = "hi") -> dict:
        """
        Transcribe raw speech bytes to text using Bhashini ASR.
        Cascades cleanly to Sarvam STT and Local ASR if Bhashini is unconfigured or fails.
        Raw audio bytes are processed in memory and NEVER written to disk.
        """
        clean_lang = language[:2] if language else "hi"
        logger.info("bhashini_asr_start", bytes_len=len(audio_bytes), lang=clean_lang, configured=self.is_configured)

        try:
            # 1. Attempt live Bhashini ASR if configured
            if self.is_configured:
                config = await self._get_pipeline_config("asr", clean_lang)
                if config:
                    callback_url = config.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl")
                    inference_auth = config.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {})
                    auth_name = inference_auth.get("name", "Authorization")
                    auth_val = inference_auth.get("value")

                    # Extract service ID
                    service_id = None
                    for task in config.get("pipelineResponseConfig", []):
                        if task.get("taskType") == "asr":
                            cfg_list = task.get("config", [])
                            if cfg_list:
                                service_id = cfg_list[0].get("serviceId")
                            break

                    if callback_url and auth_val and service_id:
                        compute_headers = {auth_name: auth_val, "Content-Type": "application/json"}
                        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                        compute_payload = {
                            "pipelineTasks": [
                                {
                                    "taskType": "asr",
                                    "config": {
                                        "language": {"sourceLanguage": clean_lang},
                                        "serviceId": service_id,
                                        "audioFormat": "wav",
                                        "samplingRate": 16000,
                                    },
                                }
                            ],
                            "inputData": {"audio": [{"audioContent": audio_b64}]},
                        }
                        comp_resp = await self._client.post(callback_url, headers=compute_headers, json=compute_payload)
                        if comp_resp.status_code == 200:
                            out_data = comp_resp.json()
                            pipeline_resp = out_data.get("pipelineResponse", [])
                            if pipeline_resp:
                                transcript = pipeline_resp[0].get("output", [{}])[0].get("source", "")
                                if transcript:
                                    return {
                                        "transcription": transcript.strip(),
                                        "detected_language": clean_lang,
                                        "confidence": 0.94,
                                        "provider": "bhashini_asr",
                                        "error": None,
                                    }

            # 2. Transparent Fallback to Sarvam STT (configured with live key)
            from app.voice.sarvam import SarvamVoiceClient
            sarvam = SarvamVoiceClient()
            if sarvam.is_configured:
                logger.info("bhashini_asr_fallback_to_sarvam", lang=clean_lang)
                sarvam_res = await sarvam.transcribe_audio(audio_bytes, language=clean_lang)
                if sarvam_res and sarvam_res.get("text"):
                    return {
                        "transcription": sarvam_res["text"],
                        "detected_language": sarvam_res.get("language", clean_lang),
                        "confidence": sarvam_res.get("confidence", 0.92),
                        "provider": "sarvam_stt_fallback",
                        "error": None,
                    }

            # 3. Fallback to Local ASR engine
            try:
                from app.voice.local.asr.local_asr import local_asr_engine
                if local_asr_engine.is_available():
                    logger.info("bhashini_asr_fallback_to_local_asr", lang=clean_lang)
                    local_res = await local_asr_engine.transcribe(audio_bytes, language=clean_lang)
                    if local_res and local_res.transcription:
                        return {
                            "transcription": local_res.transcription,
                            "detected_language": local_res.detected_language,
                            "confidence": local_res.confidence,
                            "provider": "local_asr_fallback",
                            "error": None,
                        }
            except Exception as e:
                logger.warning("local_asr_fallback_failed", error=str(e))

            # 4. Graceful unrecoverable response (never invent audio or text)
            return {
                "transcription": "",
                "detected_language": clean_lang,
                "confidence": 0.0,
                "provider": "none",
                "error": "No available ASR provider succeeded in transcribing audio",
            }
        except Exception as e:
            logger.error("bhashini_asr_failed", error=str(e))
            return {
                "transcription": "",
                "detected_language": clean_lang,
                "confidence": 0.0,
                "provider": "error",
                "error": str(e),
            }
        finally:
            del audio_bytes

    async def generate_tts(self, text: str, language: str = "hi") -> Optional[bytes]:
        """
        Generate TTS audio bytes using Bhashini TTS.
        Falls back seamlessly to Sarvam AI Bulbul and Local Neural VITS
        when Bhashini credentials are missing or when the API call fails.
        Key caching with Redis pattern `tts:{language}:{hash}`.
        """
        clean_text = (text or "").strip()
        if not clean_text:
            return None

        clean_lang = language[:2] if language else "hi"
        text_hash = hashlib.md5(clean_text.encode("utf-8")).hexdigest()
        cache_key = f"tts:{clean_lang}:{text_hash}"
        logger.info("bhashini_tts_generate", text_hash=text_hash, lang=clean_lang, configured=self.is_configured)

        # Check Redis cache if redis is available
        try:
            from app.core.database import redis_client
            if redis_client:
                cached = await redis_client.get(cache_key)
                if cached:
                    return cached
        except Exception:
            pass

        # 1. Attempt live Bhashini TTS if configured
        if self.is_configured:
            try:
                config = await self._get_pipeline_config("tts", clean_lang)
                if config:
                    callback_url = config.get("pipelineInferenceAPIEndPoint", {}).get("callbackUrl")
                    inference_auth = config.get("pipelineInferenceAPIEndPoint", {}).get("inferenceApiKey", {})
                    auth_name = inference_auth.get("name", "Authorization")
                    auth_val = inference_auth.get("value")

                    service_id = None
                    for task in config.get("pipelineResponseConfig", []):
                        if task.get("taskType") == "tts":
                            cfg_list = task.get("config", [])
                            if cfg_list:
                                service_id = cfg_list[0].get("serviceId")
                            break

                    if callback_url and auth_val and service_id:
                        compute_headers = {auth_name: auth_val, "Content-Type": "application/json"}
                        compute_payload = {
                            "pipelineTasks": [
                                {
                                    "taskType": "tts",
                                    "config": {
                                        "language": {"sourceLanguage": clean_lang},
                                        "serviceId": service_id,
                                        "gender": "female",
                                    },
                                }
                            ],
                            "inputData": {"input": [{"source": clean_text}]},
                        }
                        comp_resp = await self._client.post(callback_url, headers=compute_headers, json=compute_payload)
                        if comp_resp.status_code == 200:
                            out_data = comp_resp.json()
                            pipeline_resp = out_data.get("pipelineResponse", [])
                            if pipeline_resp:
                                audio_content = pipeline_resp[0].get("audio", [{}])[0].get("audioContent")
                                if audio_content:
                                    raw_audio = base64.b64decode(audio_content)
                                    # Cache in Redis if available
                                    try:
                                        from app.core.database import redis_client
                                        if redis_client:
                                            await redis_client.setex(cache_key, 86400, raw_audio)
                                    except Exception:
                                        pass
                                    return raw_audio
            except Exception as e:
                logger.warning("bhashini_tts_api_failed", error=str(e))

        # 2. Transparent Fallback to Sarvam AI Bulbul TTS
        try:
            from app.voice.sarvam import SarvamVoiceClient
            sarvam = SarvamVoiceClient()
            if sarvam.is_configured:
                logger.info("bhashini_tts_fallback_to_sarvam", lang=clean_lang)
                audio = await sarvam.generate_tts(clean_text, language=clean_lang)
                if audio and len(audio) > 100:
                    try:
                        from app.core.database import redis_client
                        if redis_client:
                            await redis_client.setex(cache_key, 86400, audio)
                    except Exception:
                        pass
                    return audio
        except Exception as e:
            logger.warning("sarvam_tts_fallback_failed", error=str(e))

        # 3. Transparent Fallback to Local Neural VITS TTS
        try:
            from app.voice.local.tts.local_tts import local_tts_engine
            if local_tts_engine.supports_language(clean_lang):
                logger.info("bhashini_tts_fallback_to_local_vits", lang=clean_lang)
                vits_res = await local_tts_engine.synthesize(clean_text, language=clean_lang)
                if vits_res and vits_res.audio_bytes and len(vits_res.audio_bytes) > 100:
                    return vits_res.audio_bytes
        except Exception as e:
            logger.warning("local_tts_fallback_failed", error=str(e))

        return None

    async def aclose(self) -> None:
        try:
            await self._client.aclose()
        except Exception:
            pass
