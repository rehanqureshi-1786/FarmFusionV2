from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

from app.schemas.voice import VoiceQueryRequest, VoiceQueryResponse
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/query", response_model=VoiceQueryResponse)
async def process_voice_query(request: VoiceQueryRequest):
    return await VoiceService.process_voice_query(request)


@router.post("/text-query", response_model=VoiceQueryResponse)
async def process_text_query(request: VoiceQueryRequest):
    return await VoiceService.process_text_query(request)
