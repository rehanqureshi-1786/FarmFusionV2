"""
Main Multilingual Orchestrator execution pipeline.
Assembly of intent classification, tool routing, and response synthesis nodes with multi-turn session state.
Implemented using official LangGraph StateGraph with MemorySaver checkpointer.
"""
from typing import Any, Dict, List, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
import structlog

from app.orchestrator.state import OrchestratorState
from app.orchestrator.nodes.intent_classification import intent_classification_node
from app.orchestrator.nodes.tool_router import tool_router_node
from app.orchestrator.nodes.synthesizer import response_synthesizer_node

logger = structlog.get_logger(__name__)


def _route_after_intent(state: OrchestratorState) -> str:
    """Conditional routing edge: clarification question bypasses tool execution."""
    if state.get("requires_clarification"):
        return "response_synthesizer"
    return "tool_router"


def create_orchestrator_graph():
    """Build and compile the canonical LangGraph StateGraph for FarmFusion."""
    builder = StateGraph(OrchestratorState)
    builder.add_node("intent_classification", intent_classification_node)
    builder.add_node("tool_router", tool_router_node)
    builder.add_node("response_synthesizer", response_synthesizer_node)

    builder.add_edge(START, "intent_classification")
    builder.add_conditional_edges(
        "intent_classification",
        _route_after_intent,
        {
            "response_synthesizer": "response_synthesizer",
            "tool_router": "tool_router"
        }
    )
    builder.add_edge("tool_router", "response_synthesizer")
    builder.add_edge("response_synthesizer", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


orchestrator_graph = create_orchestrator_graph()


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
    Execute the full orchestrator graph turn via LangGraph StateGraph:
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
        "tts_language": None,
        "native_tts": None,
        "fallback_used": None,
        "fallback_reason": None,
    }

    config = {"configurable": {"thread_id": session_id}}
    result_state = await orchestrator_graph.ainvoke(initial_state, config=config)
    return result_state
