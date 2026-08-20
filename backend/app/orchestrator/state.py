"""
State definition for the LangGraph Main Multilingual Orchestrator.
"""
from typing import TypedDict, Optional, List, Dict, Any


class OrchestratorState(TypedDict):
    # Core turn information
    user_id: Optional[str]
    session_id: str
    user_input: str
    
    # Multilingual & Voice state fields
    detected_language: str        # BCP-47 code e.g. "hi", "en", "gu"
    detected_dialect: Optional[str]  # e.g. "mewari", "marwari", None
    language_confidence: float    # 0.0 to 1.0
    
    # Intent Classification
    intent: str                  # weather, mandi, disease, crop_recommendation, scheme, navigation, clarify, unknown
    intent_confidence: float     # 0.0 to 1.0
    
    # Tool output payload
    tool_output: Optional[Dict[str, Any]]
    
    # History & Final Response
    messages: List[Dict[str, str]]
    final_response: str
    requires_clarification: bool
