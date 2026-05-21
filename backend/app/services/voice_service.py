import logging
from typing import Dict, Any

from app.agents.groq_client import GroqClient
from app.agents.openai_client import OpenAIClient
from app.models.voice import VoiceQueryRequest, VoiceQueryResponse
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


class VoiceService:
    @staticmethod
    async def process_voice_query(request: VoiceQueryRequest) -> VoiceQueryResponse:
        logger.info("Processing voice query")
        return VoiceQueryResponse(success=True, response=f"Received voice query: {request.text}")

    @staticmethod
    async def process_text_query(request: VoiceQueryRequest) -> VoiceQueryResponse:
        logger.info("Processing text query")
        return VoiceQueryResponse(success=True, response=f"Received text query: {request.text}")
