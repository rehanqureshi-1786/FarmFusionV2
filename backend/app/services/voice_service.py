import logging
from app.agents.openai_client import OpenAIClient
from app.models.voice import VoiceQueryRequest, VoiceQueryResponse

logger = logging.getLogger(__name__)


class VoiceService:
    @staticmethod
    async def process_voice_query(request: VoiceQueryRequest) -> VoiceQueryResponse:
        logger.info("Processing voice query")
        client = OpenAIClient()
        response = client.complete(f"Answer this voice query: {request.text}")
        return VoiceQueryResponse(success=True, response=response)

    @staticmethod
    async def process_text_query(request: VoiceQueryRequest) -> VoiceQueryResponse:
        logger.info("Processing text query")
        client = OpenAIClient()
        response = client.complete(f"Answer this text query: {request.text}")
        return VoiceQueryResponse(success=True, response=response)
