"""
Voice Orchestrator for FarmFusion Kisan Calling Agent.
Coordinates real-time telephone WebSocket audio, STT, LLM streaming via httpx, and TTS.
"""

import os
import time
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
from app.core.config import settings

from app.orchestrator.graph import run_orchestrator_pipeline

logger = structlog.get_logger()

def _get_llm_keys():
    openrouter_k = settings.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
    groq_k = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    return openrouter_k, groq_k

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
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        phone: Optional[str] = None,
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
        self.latitude = latitude
        self.longitude = longitude
        self.phone = phone
        self.manager = manager
        self.stream_id: Optional[str] = str(call_id) if call_id else None
        self.stream_ready_event = asyncio.Event()
        if self.stream_id:
            self.stream_ready_event.set()
        self.greeting_started = False
        self.is_speaking_outbound = False

        self.tts = TelephonyTTS(language_code=language)
        self.stt = TelephonySTT(self.on_transcript, self.on_speech_started, language=language)

        self.is_interrupted = False
        self.clarification_turns = 0
        self.messages: List[Dict[str, str]] = []
        self.transcript_history: List[Dict[str, str]] = []
        self.http_client = httpx.AsyncClient(timeout=10.0)

    def set_stream_id(self, stream_id: str):
        """Sets the Vobiz streamId from the WebSocket start event."""
        if stream_id:
            self.stream_id = str(stream_id)
            self.stream_ready_event.set()
            logger.info("telephony_stream_id_set", stream_id=self.stream_id, farmer=self.farmer_name)

    @staticmethod
    def _clean_for_telephony(text: str) -> str:
        """Cleans markdown symbols, bullet points, and emojis for spoken telephony audio."""
        if not text:
            return ""
        # Remove bold, italic, code markdown formatting
        t = re.sub(r'[*_~`#>]', '', text)
        # Remove markdown links [label](url) -> label
        t = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', t)
        # Remove bullet points and dashes
        t = re.sub(r'^\s*[-•]\s*', '', t, flags=re.MULTILINE)
        # Remove emojis
        t = re.sub(r'[\U00010000-\U0010ffff]', '', t)
        # Clean up newlines into sentence stops
        t = re.sub(r'\n+', '. ', t)
        # Collapse multiple spaces
        t = re.sub(r'\s+', ' ', t).strip()
        return t

    async def on_speech_started(self):
        """Barge-in: fired when farmer speaks while AI is actively speaking."""
        if not self.is_speaking_outbound:
            return
        self.is_interrupted = True
        logger.info("barge_in_detected", farmer=self.farmer_name)
        try:
            # Clear audio playback on telephony network immediately
            payload = {"event": "clearAudio"}
            if self.stream_id:
                payload["streamId"] = self.stream_id
            await self.websocket.send_text(json.dumps(payload))
        except Exception:
            pass

    async def start(self):
        """Starts the calling loop and sends the initial personalized greeting."""
        if self.greeting_started:
            return
        self.greeting_started = True
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

        clean_greeting = self._clean_for_telephony(greeting_text)
        self.messages.append({"role": "assistant", "content": clean_greeting})
        self.transcript_history.append({"speaker": "Kisan Mitra", "text": clean_greeting})

        # Synthesize and speak greeting
        await self.speak(clean_greeting)

    async def process_inbound_audio(self, audio_data: bytes):
        """Streams raw audio bytes from telephony WebSocket to STT."""
        await self.stt.process_audio(audio_data)

    async def on_transcript(self, transcript: str):
        """
        Fired when farmer's speech is transcribed via STT.
        Executes the FarmFusion Multilingual Orchestrator to route tools, verify facts, and synthesize grounded responses.
        """
        clean_transcript = transcript.rstrip(".").strip()
        NOISE_PHRASES = {
            "झाल", "thank you", "thanks", "bye", "you", "hello", "hi", "ok", "okay",
            "हम्म", "हम", "हां", "हाँ", "जी", "अच्छा", "अरे", "ओहो", "क", "क्या", "uh", "um", "ah", "hmm"
        }
        if not clean_transcript or len(clean_transcript) < 3 or clean_transcript.lower() in NOISE_PHRASES:
            logger.info("telephony_ignoring_short_or_filler_speech", transcript=clean_transcript)
            return

        self.is_interrupted = False
        logger.info("farmer_speech_transcribed", farmer=self.farmer_name, text=clean_transcript)

        self.messages.append({"role": "user", "content": clean_transcript})
        self.transcript_history.append({"speaker": f"Farmer ({self.farmer_name})", "text": clean_transcript})

        full_response_text = ""

        try:
            # Context passed to the LangGraph Orchestrator
            farmer_ctx = {
                "farmer_name": self.farmer_name,
                "name": self.farmer_name,
                "phone": self.phone,
                "location_name": self.location,
                "city": self.location,
                "district": self.location,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "active_crop": self.crop_name,
                "active_market": self.mandi_name,
                "current_price": self.current_price,
                "target_price": self.target_price,
                "weather_summary": self.weather_summary,
                "call_type": self.call_type,
                "session_type": "telephony",
            }

            session_id = self.call_id or f"vobiz_call_{self.farmer_name}"

            # Execute LangGraph Orchestrator pipeline with 5.0s telephony timeout
            # If the graph takes >5s, seamlessly falls back to 0.6s Groq LLM stream so the caller never hears dead silence.
            try:
                result_state = await asyncio.wait_for(
                    run_orchestrator_pipeline(
                        user_input=transcript,
                        detected_language=self.language,
                        session_id=session_id,
                        farmer_context=farmer_ctx,
                        active_crop=self.crop_name,
                    ),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning("orchestrator_pipeline_timed_out_switching_to_fast_stream", farmer=self.farmer_name)
                result_state = {}

            # Update tracked active crop/market if orchestrator resolved them
            if result_state.get("active_crop"):
                self.crop_name = result_state.get("active_crop")
            if result_state.get("active_market"):
                self.mandi_name = result_state.get("active_market")

            raw_resp = (
                result_state.get("final_response")
                or (result_state.get("response_envelope") or {}).get("response_text")
                or ""
            )

            clean_resp = self._clean_for_telephony(raw_resp)
            if clean_resp:
                full_response_text = clean_resp
            else:
                # Fallback to direct stream generator if pipeline returned empty text or timed out
                async for chunk in self._generate_stream(transcript):
                    full_response_text += chunk

        except Exception as e:
            logger.warning("orchestrator_invocation_failed_using_stream_fallback", error=str(e))
            try:
                async for chunk in self._generate_stream(transcript):
                    full_response_text += chunk
            except Exception as stream_err:
                logger.error("stream_fallback_failed", error=str(stream_err))
                full_response_text = (
                    f"जी {self.farmer_name} जी, आपकी बात समझ आ गई है।"
                    if self.language == "hi"
                    else f"Understood {self.farmer_name}. FarmFusion is here to assist you."
                )

        if not full_response_text.strip():
            return

        clean_final = self._clean_for_telephony(full_response_text)
        is_clarification = "स्पष्ट" in clean_final or "दोबारा" in clean_final or "बताइए क्या जानना चाहते हैं" in clean_final
        if is_clarification:
            self.clarification_turns += 1
            if self.clarification_turns == 1:
                pass
            elif self.clarification_turns == 2:
                clean_final = (
                    f"जी {self.farmer_name} जी, आप मुझसे मौसम का हाल या अपनी {self.crop_name or 'फसल'} के मंडी भाव के बारे में पूछ सकते हैं। बताइए क्या जानना चाहते हैं?"
                    if self.language == "hi"
                    else f"You can ask about the weather forecast or market prices for {self.crop_name or 'your crops'}."
                )
            else:
                # Prevent looping: if caller doesn't respond or keeps producing unclear audio, stay silent and wait
                logger.info("telephony_clarification_loop_silenced", farmer=self.farmer_name, turns=self.clarification_turns)
                return
        else:
            self.clarification_turns = 0

        self.messages.append({"role": "assistant", "content": clean_final})
        self.transcript_history.append({"speaker": "Kisan Mitra", "text": clean_final})

        # Reset interrupted state so newly generated answer plays completely
        self.is_interrupted = False
        # Synthesize and speak the response smoothly in one coherent delivery
        await self.speak(clean_final)

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
        openrouter_k, groq_k = _get_llm_keys()
        if groq_k or openrouter_k:
            api_url = "https://api.groq.com/openai/v1/chat/completions" if groq_k else "https://openrouter.ai/api/v1/chat/completions"
            api_key = groq_k or openrouter_k
            model_name = (settings.groq_model or "qwen/qwen3.8-27b") if groq_k else "google/gemma-3-12b-it"

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
        """Synthesizes text and streams 8kHz PCMU mulaw audio to telephony connection."""
        if self.is_interrupted or not text.strip():
            return

        # Wait briefly for Vobiz streamId if it has not arrived yet (up to 1.5 seconds)
        if not self.stream_id:
            try:
                await asyncio.wait_for(self.stream_ready_event.wait(), timeout=1.5)
            except (asyncio.TimeoutError, Exception):
                pass

        mulaw_audio = await self.tts.synthesize_for_phone(text)
        if mulaw_audio and not self.is_interrupted:
            self.is_speaking_outbound = True
            self.stt.set_outbound_speaking(True)
            try:
                # Stream into Vobiz buffer in 8000-byte blocks (~1.0s of audio, ~10.6KB base64, well within 64KB limit).
                CHUNK_SIZE = 8000
                total_len = len(mulaw_audio)

                send_start = time.time()
                for offset in range(0, total_len, CHUNK_SIZE):
                    if self.is_interrupted:
                        logger.info("telephony_playback_barge_in_interrupted", farmer=self.farmer_name)
                        break

                    chunk = mulaw_audio[offset:offset + CHUNK_SIZE]
                    b64_chunk = base64.b64encode(chunk).decode("utf-8")
                    payload = {
                        "event": "playAudio",
                        "media": {
                            "contentType": "audio/x-mulaw",
                            "sampleRate": 8000,
                            "payload": b64_chunk
                        }
                    }
                    if self.stream_id:
                        payload["streamId"] = self.stream_id

                    await self.websocket.send_text(json.dumps(payload))
                    # Micro-yield (25ms) so Vobiz fills its native RTP audio buffer without network starvation or glitches
                    await asyncio.sleep(0.025)

                logger.info(
                    "telephony_audio_played",
                    farmer=self.farmer_name,
                    stream_id=self.stream_id,
                    total_bytes=total_len
                )

                # Wait for phone speaker playback to finish before opening microphone.
                # Audio duration in seconds = total_len / 8000 samples per sec.
                # Subtract the time already spent during chunk transmission.
                duration_sec = total_len / 8000.0
                elapsed = time.time() - send_start
                remaining_playback = max(0.0, duration_sec - elapsed)
                playback_end = time.time() + remaining_playback

                while time.time() < playback_end:
                    if self.is_interrupted:
                        break
                    await asyncio.sleep(0.05)

            except Exception as e:
                logger.warning("telephony_audio_send_failed", error=str(e))
            finally:
                self.is_speaking_outbound = False
                self.stt.set_outbound_speaking(False)

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
