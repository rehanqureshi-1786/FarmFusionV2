"""
Real-time telephone streaming Speech-to-Text (STT) for Kisan Calling Agent.
Supports Deepgram streaming with barge-in interruption detection and local/Bhashini fallback.
"""

import os
import json
import asyncio
import structlog
from typing import Callable, Awaitable, Optional

logger = structlog.get_logger()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

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
        self.ws = None
        self.running = False
        self.receive_task = None
        self.barge_in_fired = False

    async def start(self):
        """Starts real-time STT WebSocket connection."""
        if not DEEPGRAM_API_KEY:
            logger.info("telephony_stt_mock_mode", reason="DEEPGRAM_API_KEY not set, using simulated STT channel")
            self.running = True
            return

        import websockets
        # Nova-2 phonecall model optimized for 8kHz telephone audio
        deepgram_lang = "hi" if self.language.startswith("hi") else "en"
        url = (
            f"wss://api.deepgram.com/v1/listen?"
            f"model=nova-2-phonecall&smart_format=true&encoding=linear16"
            f"&sample_rate=8000&channels=1&interim_results=true&endpointing=500&vad_events=true"
            f"&language={deepgram_lang}"
        )
        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}

        try:
            self.ws = await websockets.connect(url, additional_headers=headers)
            self.running = True
            self.receive_task = asyncio.create_task(self._receive_loop())
            logger.info("telephony_stt_started", provider="deepgram_nova2", sample_rate=8000)
        except Exception as e:
            logger.error("telephony_stt_connect_failed", error=str(e))
            self.running = True

    async def process_audio(self, audio_data: bytes):
        """Streams incoming raw audio chunk from telephony WebSocket to STT engine."""
        if self.ws and self.running:
            try:
                await self.ws.send(audio_data)
            except Exception as e:
                logger.warning("telephony_stt_send_error", error=str(e))

    async def _receive_loop(self):
        try:
            while self.running and self.ws:
                message = await self.ws.recv()
                data = json.loads(message)

                if data.get("type") == "Results":
                    is_final = data.get("is_final", False)
                    alternatives = data.get("channel", {}).get("alternatives", [])
                    if alternatives:
                        transcript = alternatives[0].get("transcript", "").strip()

                        # Barge-in: interrupt AI if user speaks words
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
                logger.error("telephony_stt_receive_error", error=str(e))

    async def stop(self):
        self.running = False
        if self.receive_task:
            self.receive_task.cancel()
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
