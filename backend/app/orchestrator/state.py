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
    detected_dialect: Optional[str]    # e.g. "mew", "rwr", None
    language_confidence: float      # 0.0 to 1.0
    farmer_preferred_language: Optional[str]
    farmer_preferred_dialect: Optional[str]
    response_language: Optional[str]
    response_dialect: Optional[str]
    tts_language: Optional[str]
    native_tts: Optional[bool]
    fallback_used: Optional[bool]
    fallback_reason: Optional[str]

    # Farmer contextual profile (retained across turns)
    farmer_context: Dict[str, Any]
    active_crop: Optional[str]

    # Intent Classification, Slot Filling & Safety Classification
    intent: str                    # weather, mandi, disease, crop_recommendation, scheme, navigation, explain_recommendation, what_if, repeat_last, speech_control, language_preference, dialect_preference, consequential_action, clarify, unknown
    intent_confidence: float       # 0.0 to 1.0
    filled_slots: Dict[str, Any]
    missing_slots: List[str]
    safety_classification: Optional[str] # READ_ONLY, NAVIGATION, REVERSIBLE, CONSEQUENTIAL
    requires_consequential_confirmation: bool
    semantic_frame: Optional[Dict[str, Any]] # Phase F2 Canonical SemanticFrame representation
    image_bytes: Optional[bytes]
    image_path: Optional[str]

    # Phase F5: Task Planner & Dependency-Aware Orchestration
    task_plan: Optional[Dict[str, Any]]
    pending_tasks: List[str]
    completed_tasks: List[str]
    failed_tasks: List[str]
    tool_results: Dict[str, Any]
    unresolved_inputs: List[str]
    next_action: Optional[str]

    # Tool Execution & Provenance
    last_tool: Optional[str]
    last_tool_result: Optional[Dict[str, Any]]
    tool_output: Optional[Dict[str, Any]]
    tool_status: Optional[str]


    # Conversational Memory & Multi-Turn References
    last_recommendations: List[Dict[str, Any]]
    last_weather_result: Optional[Dict[str, Any]]
    last_disaster_result: Optional[Dict[str, Any]]
    last_market_result: Optional[Dict[str, Any]]
    last_navigation_destination: Optional[str]
    last_final_response: Optional[str]
    speech_rate: Optional[str]
    requires_clarification: bool
    clarification_question: Optional[str]
    pending_confirmation: Optional[str]

    # Phase F6: Grounded RAG + Validation + Response Envelope
    rag_grounding: Optional[Dict[str, Any]]
    rag_citations: Optional[List[Dict[str, Any]]]
    validation_result: Optional[Dict[str, Any]]
    verified_facts: Optional[List[Dict[str, Any]]]
    confidence_tier: Optional[str]
    response_envelope: Optional[Dict[str, Any]]

    # Phase F7: Autonomous Replanning & Agent Coordination
    iteration: int
    max_iterations: int
    replan_count: int
    objective_status: Optional[str]        # OBJECTIVE_COMPLETE, NEEDS_REPLAN, NEEDS_USER_INPUT, BLOCKED, FAILED
    replan_reason: Optional[str]
    completed_capabilities: List[str]
    failed_capabilities: List[str]
    missing_requirements: List[str]
    orchestration_traces: List[Dict[str, Any]]

    # Final Synthesized Response & History
    messages: List[Dict[str, str]]
    final_response: str
    turn_history: List[Dict[str, Any]]

