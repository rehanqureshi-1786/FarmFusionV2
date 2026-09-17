"""
Real-time telephone Text-to-Speech (TTS) for Kisan Calling Agent.
Converts generated sentences into 8kHz mono G.711 mu-law (PCMU) audio for phone lines.
Supports Sarvam AI Bulbul V3, Google TTS fallback, and local FarmFusion Neural VITS.
"""

import os
import base64
import asyncio
import subprocess
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class TelephonyTTS:
    def __init__(self, language_code: str = "hi"):
        self.language_code = language_code
        self.sarvam_lang = "hi-IN" if language_code.startswith("hi") else f"{language_code}-IN"
        self.speaker = "amit" if language_code == "hi" else "priya"
        self.client = httpx.AsyncClient(timeout=8.0)

    async def synthesize_for_phone(self, text: str) -> bytes:
        """
        Synthesizes text into 8000Hz mono G.711 mu-law (PCMU) raw audio bytes for Vobiz telephony streaming.
        """
        clean_text = text.strip()
        if not clean_text:
            return b""

        # 1. Try Sarvam AI Bulbul V3 if API key available
        sarvam_key = settings.sarvam_api_key or os.getenv("SARVAM_API_KEY")
        if sarvam_key:
            try:
                url = "https://api.sarvam.ai/text-to-speech"
                headers = {
                    "api-subscription-key": sarvam_key,
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
                        mulaw_bytes = await self._convert_to_8khz_mulaw(raw_bytes)
                        if mulaw_bytes:
                            return mulaw_bytes
                else:
                    logger.warning("sarvam_tts_non_200", status_code=res.status_code, body=res.text[:100])
            except Exception as e:
                logger.warning("sarvam_tts_phone_failed", error=str(e), fallback="google_translate_tts")

        # 2. High-speed Google Translate TTS Fallback (Zero cost, cloud-reliable, no API key required)
        try:
            lang_code = self.language_code[:2] if self.language_code else "hi"
            url = "https://translate.google.com/translate_tts"
            params = {
                "ie": "UTF-8",
                "q": clean_text[:200],
                "tl": lang_code,
                "client": "tw-ob"
            }
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = await self.client.get(url, params=params, headers=headers, timeout=6.0)
            if res.status_code == 200 and len(res.content) > 100:
                mulaw_bytes = await self._convert_to_8khz_mulaw(res.content)
                if mulaw_bytes:
                    return mulaw_bytes
        except Exception as e:
            logger.warning("google_tts_fallback_failed", error=str(e))

        # 3. FarmFusion Local Neural VITS Fallback
        try:
            from app.voice.local.tts.local_tts import local_tts_engine
            vits_res = await local_tts_engine.synthesize(clean_text, language=self.language_code[:2])
            if vits_res and vits_res.audio_bytes:
                return await self._convert_to_8khz_mulaw(vits_res.audio_bytes)
        except Exception as e:
            logger.error("local_vits_phone_synthesis_failed", error=str(e))

        return b""

    async def _convert_to_8khz_mulaw(self, input_audio_bytes: bytes) -> bytes:
        """Converts any audio byte stream (WAV, MP3, PCM) into raw 8000Hz mono G.711 mu-law for Vobiz PCMU."""
        def _run_ffmpeg():
            return subprocess.run(
                [
                    "ffmpeg", "-y", "-i", "pipe:0",
                    "-f", "mulaw",
                    "-acodec", "pcm_mulaw",
                    "-ar", "8000",
                    "-ac", "1",
                    "pipe:1"
                ],
                input=input_audio_bytes,
                capture_output=True,
                check=False
            )
        try:
            process = await asyncio.to_thread(_run_ffmpeg)
            if process.returncode == 0 and process.stdout:
                return process.stdout
            logger.warning("ffmpeg_mulaw_conversion_nonzero", returncode=process.returncode, stderr=process.stderr.decode(errors="ignore")[:150])
            return process.stdout or b""
        except Exception as e:
            logger.error("ffmpeg_telephony_mulaw_conversion_error", error=str(e))
            return b""

    # Backward compatibility alias
    def _convert_to_8khz_pcm(self, input_audio_bytes: bytes) -> bytes:
        return self._convert_to_8khz_mulaw(input_audio_bytes)

