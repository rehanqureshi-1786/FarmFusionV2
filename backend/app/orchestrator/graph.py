"""
Main Multilingual Orchestrator execution pipeline.
Assembly of intent classification, tool routing, and response synthesis nodes with multi-turn session state.
"""
from typing import Any, Dict, List, Optional
import structlog

from app.orchestrator.state import OrchestratorState
from app.orchestrator.nodes.intent_classification import intent_classification_node
from app.orchestrator.nodes.tool_router import tool_router_node
from app.orchestrator.nodes.synthesizer import response_synthesizer_node

logger = structlog.get_logger(__name__)


async def run_orchestrator_pipeline(
    user_input: str,
    detected_language: str = "hi",
    detected_dialect: str | None = None,
    language_confidence: float = 1.0,
    session_id: str = "default_session",
    farmer_context: Optional[Dict[str, Any]] = None,
    last_recommendations: Optional[List[Dict[str, Any]]] = None,
    filled_slots: Optional[Dict[str, Any]] = None,
    last_final_response: Optional[str] = None,
) -> OrchestratorState:
    """
    Execute the full orchestrator graph turn:
    1. State initialization with multi-turn context
    2. Intent classification & entity extraction
    3. Tool execution via ToolRegistry
    4. Response synthesis with zero data fabrication
    """
    initial_state: OrchestratorState = {
        "user_id": None,
        "session_id": session_id,
        "user_input": user_input,
        "detected_language": detected_language,
        "detected_dialect": detected_dialect,
        "language_confidence": language_confidence,
        "farmer_context": farmer_context or {},
        "intent": "unknown",
        "intent_confidence": 0.0,
        "filled_slots": filled_slots or {},
        "missing_slots": [],
        "last_tool": None,
        "last_tool_result": None,
        "tool_output": None,
        "tool_status": None,
        "last_recommendations": last_recommendations or [],
        "last_final_response": last_final_response,
        "messages": [],
        "final_response": "",
        "requires_clarification": False,
        "clarification_question": None,
        "turn_history": [],
    }

    # Step 1: Intent Classification & Slot Extraction
    state = await intent_classification_node(initial_state)

    # Step 2: Tool Routing (if not requiring clarification)
    if not state.get("requires_clarification"):
        state = await tool_router_node(state)

    # Step 3: Response Synthesis
    state = await response_synthesizer_node(state)
    return state
