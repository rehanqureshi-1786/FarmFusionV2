"""
Real-time telephone streaming Speech-to-Text (STT) for Kisan Calling Agent.
Supports Deepgram streaming, Groq Whisper (Whisper-Large-V3), and Sarvam STT (Saaras:v3)
with sub-second VAD barge-in interruption detection.
"""

import os
import io
import json
import time
import asyncio
import subprocess
import structlog
import httpx
from typing import Callable, Awaitable, Optional
from app.core.config import settings

logger = structlog.get_logger()

# Precompute 256-byte G.711 mu-law decoding table for zero-latency linear PCM energy computation
def _build_mulaw_table():
    table = []
    for b in range(256):
        b_inv = ~b & 0xFF
        sign = -1 if (b_inv & 0x80) else 1
        exponent = (b_inv >> 4) & 0x07
        mantissa = b_inv & 0x0F
        sample = sign * ((mantissa << 3) + 0x84) << exponent
        sample -= sign * 0x84
        table.append(sample)
    return table

MULAW_DECODE_TABLE = _build_mulaw_table()

class TelephonySTT:
    def __init__(
        self,
        on_transcript_callback: Callable[[str], Awaitable[None]],
        on_speech_started_callback: Optional[Callable[[], Awaitable[None]]] = None,
        language: str = "hi"
    ):
        self.on_transcript_callback = on_transcript_callback
        self.on_speech_started_callback = on_speech_started_callback
        self.language = language
        self.running = False
        self.deepgram_ws = None
        self.receive_task = None
        self.barge_in_fired = False

        # VAD & Audio Buffer for Groq Whisper / Sarvam
        self.audio_buffer = bytearray()
        self.is_speaking = False
        self.last_speech_time = 0.0
        self.speech_start_time = 0.0
        self.vad_task = None
        self.http_client = httpx.AsyncClient(timeout=10.0)

        # Keys
        self.deepgram_key = settings.deepgram_api_key or os.getenv("DEEPGRAM_API_KEY")
        self.groq_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        self.sarvam_key = settings.sarvam_api_key or os.getenv("SARVAM_API_KEY")

    async def start(self):
        """Starts real-time STT engine."""
        self.running = True

        if self.deepgram_key:
            try:
                import websockets
                deepgram_lang = "hi" if self.language.startswith("hi") else "en"
                url = (
                    f"wss://api.deepgram.com/v1/listen?"
                    f"model=nova-2-phonecall&smart_format=true&encoding=mulaw"
                    f"&sample_rate=8000&channels=1&interim_results=true&endpointing=500&vad_events=true"
                    f"&language={deepgram_lang}"
                )
                headers = {"Authorization": f"Token {self.deepgram_key}"}
                self.deepgram_ws = await websockets.connect(url, additional_headers=headers)
                self.receive_task = asyncio.create_task(self._deepgram_receive_loop())
                logger.info("telephony_stt_started", provider="deepgram_nova2")
                return
            except Exception as e:
                logger.warning("deepgram_connect_failed_using_whisper_vad", error=str(e))

        # Start VAD silence watchdog for chunked ASR (Groq Whisper / Sarvam)
        self.vad_task = asyncio.create_task(self._vad_silence_monitor())
        logger.info("telephony_stt_vad_started", groq=bool(self.groq_key), sarvam=bool(self.sarvam_key))

    async def process_audio(self, audio_data: bytes):
        """Processes incoming 8kHz mu-law audio chunk from telephony stream."""
        if not self.running or not audio_data:
            return

        # 1. Forward to Deepgram WebSocket if active
        if self.deepgram_ws:
            try:
                await self.deepgram_ws.send(audio_data)
                return
            except Exception:
                pass

        # 2. Local VAD energy computation
        total_energy = 0
        for b in audio_data:
            total_energy += abs(MULAW_DECODE_TABLE[b])
        avg_energy = total_energy / max(len(audio_data), 1)

        now = time.time()
        # Energy threshold for speech vs background telephone line noise
        is_speech_chunk = avg_energy > 1200

        if is_speech_chunk:
            self.last_speech_time = now
            if not self.is_speaking:
                self.is_speaking = True
                self.speech_start_time = now
                # Barge-in: immediately notify orchestrator to stop talking
                if not self.barge_in_fired and self.on_speech_started_callback:
                    self.barge_in_fired = True
                    asyncio.create_task(self.on_speech_started_callback())

            self.audio_buffer.extend(audio_data)
        elif self.is_speaking:
            # Add short trailing silence
            self.audio_buffer.extend(audio_data)

    async def _vad_silence_monitor(self):
        """Monitors for end-of-utterance pauses (800ms silence) to trigger transcription."""
        while self.running:
            await asyncio.sleep(0.1)
            now = time.time()
            if self.is_speaking and self.last_speech_time > 0:
                silence_duration = now - self.last_speech_time
                speech_duration = self.last_speech_time - self.speech_start_time

                # End of speech detected if silence >= 0.8s and at least 0.4s of speech was spoken
                if silence_duration >= 0.8:
                    if speech_duration >= 0.4 and len(self.audio_buffer) >= 3200:
                        chunk_to_transcribe = bytes(self.audio_buffer)
                        self.audio_buffer.clear()
                        self.is_speaking = False
                        self.barge_in_fired = False
                        asyncio.create_task(self._transcribe_audio_buffer(chunk_to_transcribe))
                    else:
                        # Too short (noise / click), reset buffer
                        self.audio_buffer.clear()
                        self.is_speaking = False
                        self.barge_in_fired = False

    async def _transcribe_audio_buffer(self, mulaw_bytes: bytes):
        """Transcribes accumulated mu-law audio via Groq Whisper or Sarvam STT."""
        try:
            # Convert 8kHz mu-law to 16kHz WAV in memory using ffmpeg
            process = subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-f", "mulaw", "-ar", "8000", "-i", "pipe:0",
                    "-ar", "16000", "-ac", "1",
                    "-f", "wav", "pipe:1"
                ],
                input=mulaw_bytes,
                capture_output=True,
                check=False
            )
            wav_bytes = process.stdout
            if not wav_bytes or process.returncode != 0:
                return

            transcript = ""

            # 1. Groq Whisper Large V3 (fastest response, ~300ms)
            if self.groq_key:
                try:
                    url = "https://api.groq.com/openai/v1/audio/transcriptions"
                    headers = {"Authorization": f"Bearer {self.groq_key}"}
                    files = {"file": ("speech.wav", wav_bytes, "audio/wav")}
                    lang_code = self.language[:2] if self.language else "hi"
                    data = {"model": "whisper-large-v3", "language": lang_code}
                    res = await self.http_client.post(url, headers=headers, files=files, data=data)
                    if res.status_code == 200:
                        transcript = res.json().get("text", "").strip()
                except Exception as ex:
                    logger.warning("groq_whisper_failed", error=str(ex))

            # 2. Sarvam Saaras V3 fallback
            if not transcript and self.sarvam_key:
                try:
                    url = "https://api.sarvam.ai/speech-to-text"
                    headers = {"api-subscription-key": self.sarvam_key}
                    files = {"file": ("speech.wav", wav_bytes, "audio/wav")}
                    sarvam_lang = f"{self.language[:2]}-IN" if self.language else "hi-IN"
                    data = {"language_code": sarvam_lang, "model": "saaras:v3"}
                    res = await self.http_client.post(url, headers=headers, files=files, data=data)
                    if res.status_code == 200:
                        transcript = res.json().get("transcript", "").strip()
                except Exception as ex:
                    logger.warning("sarvam_stt_failed", error=str(ex))

            if transcript:
                logger.info("telephony_caller_utterance_transcribed", transcript=transcript)
                await self.on_transcript_callback(transcript)

        except Exception as e:
            logger.error("telephony_stt_transcription_error", error=str(e))

    async def _deepgram_receive_loop(self):
        try:
            while self.running and self.deepgram_ws:
                message = await self.deepgram_ws.recv()
                data = json.loads(message)
                if data.get("type") == "Results":
                    is_final = data.get("is_final", False)
                    alternatives = data.get("channel", {}).get("alternatives", [])
                    if alternatives:
                        transcript = alternatives[0].get("transcript", "").strip()
                        if transcript and not is_final and len(transcript) >= 3 and not self.barge_in_fired:
                            self.barge_in_fired = True
                            if self.on_speech_started_callback:
                                asyncio.create_task(self.on_speech_started_callback())
                        if transcript and is_final:
                            self.barge_in_fired = False
                            asyncio.create_task(self.on_transcript_callback(transcript))
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self.running:
                logger.error("deepgram_receive_error", error=str(e))

    async def stop(self):
        self.running = False
        if self.vad_task:
            self.vad_task.cancel()
        if self.receive_task:
            self.receive_task.cancel()
        if self.deepgram_ws:
            try:
                await self.deepgram_ws.close()
            except Exception:
                pass
        await self.http_client.aclose()

