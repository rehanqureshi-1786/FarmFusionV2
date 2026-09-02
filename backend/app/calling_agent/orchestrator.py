"""
Voice Orchestrator for FarmFusion Kisan Calling Agent.
Coordinates real-time telephone WebSocket audio, STT, LLM streaming via httpx, and TTS.
"""

import os
import json
import base64
import asyncio
import re
import structlog
import httpx
from typing import Optional, Dict, Any, List
from fastapi import WebSocket
from app.calling_agent.prompts import get_kisan_call_prompt, get_initial_kisan_greeting
from app.calling_agent.stt import TelephonySTT
from app.calling_agent.tts import TelephonyTTS

logger = structlog.get_logger()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class KisanVoiceOrchestrator:
    def __init__(
        self,
        websocket: WebSocket,
        farmer_name: str,
        call_type: str = "general_advisory",
        language: str = "hi",
        location: str = "India",
        crop_name: Optional[str] = None,
        mandi_name: Optional[str] = None,
        current_price: Optional[float] = None,
        target_price: Optional[float] = None,
        weather_summary: Optional[str] = None,
        agent_instruction: Optional[str] = None,
        callback_url: Optional[str] = None,
        call_id: Optional[str] = None,
        manager = None
    ):
        self.websocket = websocket
        self.farmer_name = farmer_name
        self.call_type = call_type
        self.language = language
        self.location = location
        self.crop_name = crop_name
        self.mandi_name = mandi_name
        self.current_price = current_price
        self.target_price = target_price
        self.weather_summary = weather_summary
        self.agent_instruction = agent_instruction
        self.callback_url = callback_url
        self.call_id = call_id
        self.manager = manager

        self.tts = TelephonyTTS(language_code=language)
        self.stt = TelephonySTT(self.on_transcript, self.on_speech_started, language=language)

        self.is_interrupted = False
        self.messages: List[Dict[str, str]] = []
        self.transcript_history: List[Dict[str, str]] = []
        self.http_client = httpx.AsyncClient(timeout=10.0)

    async def on_speech_started(self):
        """Barge-in: fired the millisecond farmer begins speaking."""
        self.is_interrupted = True
        logger.info("barge_in_detected", farmer=self.farmer_name)
        try:
            # Clear audio playback on telephony network immediately
            await self.websocket.send_text(json.dumps({"event": "clearAudio"}))
        except Exception:
            pass

    async def start(self):
        """Starts the calling loop and sends the initial personalized greeting."""
        logger.info("kisan_call_session_started", farmer=self.farmer_name, call_type=self.call_type)
        asyncio.create_task(self.stt.start())

        greeting_text = get_initial_kisan_greeting(
            farmer_name=self.farmer_name,
            call_type=self.call_type,
            language=self.language,
            crop_name=self.crop_name,
            mandi_name=self.mandi_name,
            current_price=self.current_price
        )

        self.messages.append({"role": "assistant", "content": greeting_text})
        self.transcript_history.append({"speaker": "Kisan Mitra", "text": greeting_text})

        # Synthesize and speak greeting
        await self.speak(greeting_text)

    async def process_inbound_audio(self, audio_data: bytes):
        """Streams raw audio bytes from telephony WebSocket to STT."""
        await self.stt.process_audio(audio_data)

    async def on_transcript(self, transcript: str):
        """Fired when farmer's speech is transcribed."""
        self.is_interrupted = False
        logger.info("farmer_speech_transcribed", farmer=self.farmer_name, text=transcript)

        self.messages.append({"role": "user", "content": transcript})
        self.transcript_history.append({"speaker": f"Farmer ({self.farmer_name})", "text": transcript})

        # Stream response sentence by sentence
        full_response = ""
        current_sentence = ""

        try:
            async for chunk in self._generate_stream(transcript):
                if self.is_interrupted:
                    logger.info("ai_response_interrupted", farmer=self.farmer_name)
                    break

                full_response += chunk
                current_sentence += chunk

                if re.search(r'[.!?।\n]', current_sentence) and len(current_sentence.strip()) > 10:
                    sentence_to_speak = current_sentence.strip()
                    current_sentence = ""
                    await self.speak(sentence_to_speak)
                    if self.is_interrupted:
                        break

            if not self.is_interrupted and current_sentence.strip():
                await self.speak(current_sentence.strip())

            if full_response.strip():
                self.messages.append({"role": "assistant", "content": full_response.strip()})
                self.transcript_history.append({"speaker": "Kisan Mitra", "text": full_response.strip()})

        except Exception as e:
            logger.error("calling_agent_response_error", error=str(e))

    async def _generate_stream(self, latest_input: str):
        """Generates stream chunks from LLM with agricultural persona prompt."""
        system_prompt = get_kisan_call_prompt(
            farmer_name=self.farmer_name,
            call_type=self.call_type,
            language=self.language,
            location=self.location,
            crop_name=self.crop_name,
            mandi_name=self.mandi_name,
            current_price=self.current_price,
            target_price=self.target_price,
            weather_summary=self.weather_summary,
            custom_instruction=self.agent_instruction
        )

        all_msgs = [{"role": "system", "content": system_prompt}] + self.messages

        # 1. Try Groq or OpenRouter if available
        if GROQ_API_KEY or OPENROUTER_API_KEY:
            api_url = "https://api.groq.com/openai/v1/chat/completions" if GROQ_API_KEY else "https://openrouter.ai/api/v1/chat/completions"
            api_key = GROQ_API_KEY or OPENROUTER_API_KEY
            model_name = "llama-3.3-70b-versatile" if GROQ_API_KEY else "google/gemma-3-12b-it"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": all_msgs,
                "temperature": 0.3,
                "max_tokens": 160,
                "stream": True
            }

            try:
                async with self.http_client.stream("POST", api_url, headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: ") and line != "data: [DONE]":
                            try:
                                chunk_json = json.loads(line[6:])
                                delta = chunk_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                pass
                return
            except Exception as e:
                logger.warning("llm_stream_error", error=str(e))

        # Fallback natural language response
        if self.language == "hi":
            yield f"जी {self.farmer_name} जी, आपकी बात समझ आ गई है। फार्मफ्यूजन आपकी पूरी सहायता करेगा।"
        else:
            yield f"Understood {self.farmer_name}. FarmFusion is here to assist you."

    async def speak(self, text: str):
        """Synthesizes text and streams 8kHz PCM audio to telephony connection."""
        if self.is_interrupted or not text.strip():
            return

        pcm_audio = await self.tts.synthesize_for_phone(text)
        if pcm_audio and not self.is_interrupted:
            try:
                b64_audio = base64.b64encode(pcm_audio).decode("utf-8")
                # Official current Vobiz streaming protocol uses event="playAudio"
                payload = {
                    "event": "playAudio",
                    "media": {
                        "payload": b64_audio
                    }
                }
                await self.websocket.send_text(json.dumps(payload))
            except Exception as e:
                logger.warning("telephony_audio_send_failed", error=str(e))

    async def generate_call_summary(self) -> str:
        """Generates concise call summary for database logging and webhook."""
        if not self.transcript_history:
            return f"Call completed with {self.farmer_name} regarding {self.call_type}."

        formatted_transcript = "\n".join([f"{t['speaker']}: {t['text']}" for t in self.transcript_history])
        return f"Completed telephone call with farmer {self.farmer_name} regarding {self.call_type}. Discussed agricultural advisory and next steps."

    async def stop(self):
        """Cleans up STT and audio sockets."""
        await self.stt.stop()
        await self.http_client.aclose()
