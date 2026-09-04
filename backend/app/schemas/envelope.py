"""
Typed Response Envelope contract for Phase F6 Grounded LLM Response Synthesis.
Provides a structured contract returning response text, citations, verified facts,
confidence tiers, and Android / telephony action directives.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.rag import RAGCitation
from app.schemas.validation import VerifiedFact
from app.schemas.semantic_frame import ActionIntent, NavigationDestination, RequiredInput


class StructuredActionPayload(BaseModel):
    """Action directive payload for client (Android, Voice, Telephony)."""
    model_config = ConfigDict(extra="forbid")

    action: str = Field(default="ANSWER", description="ANSWER, CLARIFY, NAVIGATE, REQUEST_INPUT, CALL, NOTIFY")
    destination: Optional[str] = Field(None, description="Navigation destination if action=NAVIGATE")
    android_route: Optional[str] = Field(None, description="Android navController route")
    required_input: Optional[str] = Field(None, description="Input prerequisite e.g. LEAF_IMAGE, FARM_LOCATION")
    target_phone: Optional[str] = Field(None, description="Phone number for automated telephony call")
    call_reason: Optional[str] = Field(None, description="Reason for telephony outreach")
    notification_title: Optional[str] = None
    notification_body: Optional[str] = None


class ResponseEnvelope(BaseModel):
    """
    Final canonical response envelope emitted by the LangGraph orchestrator.
    Consumable by Android UI, TTS service, Calling Agent, and API clients.
    """
    model_config = ConfigDict(extra="forbid")

    response_text: str = Field(..., description="Localized, grounded farmer-friendly explanation")
    action_payload: StructuredActionPayload = Field(default_factory=StructuredActionPayload)
    citations: List[RAGCitation] = Field(default_factory=list, description="Verified ICAR document references")
    verified_facts: List[VerifiedFact] = Field(default_factory=list, description="Immutable factual fact set")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Composite answer confidence")
    confidence_tier: str = Field(default="high", description="high, medium, low, unclear")
    warnings: List[str] = Field(default_factory=list, description="Agronomic safety caveats or warnings")
    language: str = Field(default="hi", description="BCP-47 output language code")
    dialect: Optional[str] = Field(None, description="Regional dialect code (e.g. rwr, mew)")
    tts_language: str = Field(default="hi", description="Voice TTS synthesis language")
    native_tts: bool = Field(default=True, description="True if native voice model is available")
    fallback_used: bool = Field(default=False, description="True if language or voice fallback was applied")
    fallback_reason: Optional[str] = Field(None, description="Explanation for TTS or language fallback")
