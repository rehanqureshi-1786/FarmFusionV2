"""
Real-time telephone Text-to-Speech (TTS) for Kisan Calling Agent.
Converts generated sentences into 8kHz PCM audio for phone lines.
Supports Sarvam AI Bulbul, Bhashini, and local FarmFusion Neural VITS.
"""

import os
import io
import base64
import asyncio
import subprocess
import httpx
import structlog
from app.voice.local.tts.local_tts import local_tts_engine

logger = structlog.get_logger()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

class TelephonyTTS:
    def __init__(self, language_code: str = "hi"):
        self.language_code = language_code
        self.sarvam_lang = "hi-IN" if language_code.startswith("hi") else f"{language_code}-IN"
        self.speaker = "amit" if language_code == "hi" else "priya"
        self.client = httpx.AsyncClient(timeout=8.0)

    async def synthesize_for_phone(self, text: str) -> bytes:
        """
        Synthesizes text into 8000Hz mono 16-bit linear PCM audio for telephony streaming.
        """
        clean_text = text.strip()
        if not clean_text:
            return b""

        # 1. Try Sarvam AI Bulbul V3 if API key available
        if SARVAM_API_KEY:
            try:
                url = "https://api.sarvam.ai/text-to-speech"
                headers = {
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": "application/json"
                }
                payload = {
                    "inputs": [clean_text],
                    "target_language_code": self.sarvam_lang,
                    "speaker": self.speaker,
                    "pace": 1.0,
                    "speech_sample_rate": 8000,
                    "enable_preprocessing": True,
                    "model": "bulbul:v3"
                }
                res = await self.client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    audios = data.get("audios", [])
                    if audios:
                        raw_bytes = base64.b64decode(audios[0])
                        return self._convert_to_8khz_pcm(raw_bytes)
            except Exception as e:
                logger.warning("sarvam_tts_phone_failed", error=str(e), fallback="local_neural_vits")

        # 2. FarmFusion Local Neural VITS Fallback (Zero cost, offline self-hosted)
        try:
            vits_res = await local_tts_engine.synthesize(clean_text, language=self.language_code[:2])
            if vits_res and vits_res.audio_bytes:
                return self._convert_to_8khz_pcm(vits_res.audio_bytes)
        except Exception as e:
            logger.error("local_vits_phone_synthesis_failed", error=str(e))

        return b""

    def _convert_to_8khz_pcm(self, input_audio_bytes: bytes) -> bytes:
        """Converts any wav/mp3/pcm byte stream into 8kHz mono 16-bit PCM for telephony WebSocket."""
        try:
            process = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", "pipe:0",
                    "-f", "s16le",
                    "-acodec", "pcm_s16le",
                    "-ar", "8000",
                    "-ac", "1",
                    "pipe:1"
                ],
                input=input_audio_bytes,
                capture_output=True,
                check=False
            )
            return process.stdout
        except Exception as e:
            logger.error("ffmpeg_telephony_pcm_conversion_error", error=str(e))
            return input_audio_bytes
