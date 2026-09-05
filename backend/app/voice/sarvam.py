"""
Sarvam AI Voice & Language provider for the FarmFusion AI Assistant.

Role (kept intentionally thin — Sarvam is ONLY the voice/language LAYER):
  VOICE input  -> Sarvam STT  -> (text + language metadata) -> EXISTING F7 orchestrator
  F7 response  -> Sarvam TTS  -> audio -> Android/phone playback

STT returns the recognized text plus Sarvam's returned language (provenance signal).
Language detection here is NOT intent detection: the existing F7 semantic extraction
+ planner continue to pick specialist tools. When Sarvam is unavailable/unconfigured,
callers fall back to the existing Bhashini / local providers — this module never
breaks the voice pipeline.
"""
from __future__ import annotations

import base64
from typing import Any, Dict, Optional

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

SARVAM_BASE = "https://api.sarvam.ai"
# Bhashini-style ASRResult dict whose keys mirror providers.ASRResult so we stay
# schema-compatible with the existing provider abstraction.
SAMPLE_RATES = {"hi": 16000, "en": 16000, "ta": 16000, "te": 16000, "kn": 16000,
                "ml": 16000, "mr": 16000, "gu": 16000, "pa": 16000, "bn": 16000}
# Sarvam target_language_code mapping (BCP-47 -> Sarvam -IN codes).
SARVAM_LANG = {"hi": "hi-IN", "en": "en-IN", "gu": "gu-IN", "mr": "mr-IN",
               "pa": "pa-IN", "bn": "bn-IN", "ta": "ta-IN", "te": "te-IN",
               "kn": "kn-IN", "ml": "ml-IN"}


class SarvamVoiceClient:
    """Thin Sarvam STT+TTS + language-signal client with graceful fallback."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.sarvam_api_key
        self._client = httpx.AsyncClient(timeout=12.0)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def is_available(self) -> bool:
        """Availability = configured (network availability is checked at call time)."""
        return self.is_configured

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        language: str = "hi",
        with_diarization: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Sarvam Speech-to-Text (Batch) -> {text, language, confidence, provider}.
        Returns None when unavailable so callers fall through to existing providers.
        """
        if not self.is_configured or not audio_bytes:
            logger.info("sarvam_stt_unavailable", configured=self.is_configured)
            return None

        # SarvamBatch expects a WAV/MP3; map malformed/missing audio to fallback signal.
        sample_rate = SAMPLE_RATES.get(language[:2], 16000)
        url = f"{SARVAM_BASE}/v1/speech-to-text"
        headers = {"api-subscription-key": self.api_key}
        try:
            resp = await self._client.post(
                url,
                headers=headers,
                files={"file": ("input.wav", audio_bytes, "audio/wav")},
                data={
                    "language_code": language[:2],
                    "model": "saarika:v2",
                    "with_diarization": str(with_diarization),
                    "num_speakers": "1",
                },
                timeout=30.0,
            )
            if resp.status_code != 200:
                logger.warning("sarvam_stt_http_error", status=resp.status_code)
                return None
            data = resp.json()
            transcript = (data.get("transcript") or "").strip()
            if not transcript:
                return None
            return {
                "text": transcript,
                "language": data.get("language_code", language[:2]),
                "confidence": round(float(data.get("confidence") or 0.90), 4),
                "provider": "sarvam_stt",
            }
        except Exception as exc:
            logger.warning("sarvam_stt_error", error=str(exc))
            return None

    async def generate_tts(
        self,
        text: str,
        language: str = "hi",
        speaker: str = "amit",
        speech_sample_rate: int = 16000,
    ) -> Optional[bytes]:
        """
        Sarvam AI Bulbul TTS -> raw audio bytes (wav/pcm).
        Returns None when unavailable so callers fall back to existing local/Bhashini TTS.
        """
        clean = (text or "").strip()
        if not self.is_configured or not clean:
            logger.info("sarvam_tts_unavailable", configured=self.is_configured)
            return None
        target = SARVAM_LANG.get(language[:2], "hi-IN")
        url = f"{SARVAM_BASE}/text-to-speech"
        headers = {"api-subscription-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "inputs": [clean],
            "target_language_code": target,
            "speaker": "amit" if language[:2] == "hi" else "priya",
            "pace": 1.0,
            "speech_sample_rate": speech_sample_rate,
            "enable_preprocessing": True,
            "model": "bulbul:v3",
        }
        del speaker  # use deterministic speaker by language like telephony TTS
        try:
            resp = await self._client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.warning("sarvam_tts_http_error", status=resp.status_code)
                return None
            data = resp.json()
            audios = data.get("audios") or []
            if not audios:
                return None
            return base64.b64decode(audios[0])
        except Exception as exc:
            logger.warning("sarvam_tts_error", error=str(exc))
            return None

    async def aclose(self) -> None:
        try:
            await self._client.aclose()
        except Exception:
            pass