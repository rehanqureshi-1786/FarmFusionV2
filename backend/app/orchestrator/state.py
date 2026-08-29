"""
State definition for the LangGraph Main Multilingual Orchestrator.
Maintains structured multi-turn conversational session state, farmer context, and slot-filling.
"""
from typing import TypedDict, Optional, List, Dict, Any


class FarmerContext(TypedDict, total=False):
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    state: Optional[str]
    district: Optional[str]
    soil_type: Optional[str]
    primary_crops: List[str]


class OrchestratorState(TypedDict, total=False):
    # Core turn information
    user_id: Optional[str]
    session_id: str
    user_input: str

    # Multilingual & Voice state fields
    detected_language: str          # BCP-47 code e.g. "hi", "en", "gu"
    detected_dialect: Optional[str]    # e.g. "mewari", "marwari", None
    language_confidence: float      # 0.0 to 1.0

    # Farmer contextual profile (retained across turns)
    farmer_context: Dict[str, Any]
    active_crop: Optional[str]

    # Intent Classification & Slot Filling
    intent: str                    # weather, mandi, disease, crop_recommendation, scheme, navigation, explain_recommendation, what_if, repeat_last, speech_control, clarify, unknown
    intent_confidence: float       # 0.0 to 1.0
    filled_slots: Dict[str, Any]
    missing_slots: List[str]

    # Tool Execution & Provenance
    last_tool: Optional[str]
    last_tool_result: Optional[Dict[str, Any]]
    tool_output: Optional[Dict[str, Any]]
    tool_status: Optional[str]

    # Conversational Memory & Multi-Turn References
    last_recommendations: List[Dict[str, Any]]
    last_weather_result: Optional[Dict[str, Any]]
    last_market_result: Optional[Dict[str, Any]]
    last_navigation_destination: Optional[str]
    last_final_response: Optional[str]
    speech_rate: Optional[str]
    requires_clarification: bool
    clarification_question: Optional[str]
    pending_confirmation: Optional[str]

    # Final Synthesized Response & History
    messages: List[Dict[str, str]]
    final_response: str
    turn_history: List[Dict[str, Any]]
