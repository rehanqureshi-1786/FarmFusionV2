"""
Main Multilingual Orchestrator execution pipeline.
Assembly of intent classification, tool routing, and response synthesis nodes.
"""
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
    session_id: str = "default_session"
) -> OrchestratorState:
    """
    Execute the full orchestrator graph turn:
    1. State initialization
    2. Intent classification & confidence check (<0.6 fallback to clarification)
    3. Tool execution
    4. Response synthesis
    """
    initial_state: OrchestratorState = {
        "user_id": None,
        "session_id": session_id,
        "user_input": user_input,
        "detected_language": detected_language,
        "detected_dialect": detected_dialect,
        "language_confidence": language_confidence,
        "intent": "unknown",
        "intent_confidence": 0.0,
        "tool_output": None,
        "messages": [],
        "final_response": "",
        "requires_clarification": False
    }

    # Step 1: Intent Classification
    state = await intent_classification_node(initial_state)

    # Step 2: Tool Routing (if not requiring clarification)
    if not state.get("requires_clarification"):
        state = await tool_router_node(state)

    # Step 3: Response Synthesis
    state = await response_synthesizer_node(state)
    return state
