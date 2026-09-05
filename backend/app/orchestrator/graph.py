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
from app.orchestrator.nodes.planner import planner_node
from app.orchestrator.nodes.plan_executor import plan_executor_node
from app.orchestrator.nodes.rag_grounding import rag_grounding_node, should_trigger_rag_grounding
from app.orchestrator.nodes.validation import validation_node
from app.orchestrator.nodes.synthesizer import response_synthesizer_node
from app.orchestrator.nodes.evaluator import objective_evaluator_node
from app.orchestrator.nodes.replanner import replanner_node

logger = structlog.get_logger(__name__)


def _route_after_intent(state: OrchestratorState) -> str:
    """Conditional routing edge: clarification question bypasses planning."""
    if state.get("requires_clarification"):
        return "validation"
    return "planner"


def _route_after_planner(state: OrchestratorState) -> str:
    """Conditional routing edge: non-tool actions (NAVIGATE, CLARIFY) bypass execution."""
    next_action = state.get("next_action")
    if state.get("requires_clarification") or next_action in ["NAVIGATE", "CLARIFY", "REQUEST_INPUT", "ANSWER_DIRECT"]:
        return "objective_evaluator"
    return "plan_executor"


def _route_after_evaluator(state: OrchestratorState) -> str:
    """
    Conditional routing edge for Phase F7 Autonomous Replanning:
    - NEEDS_REPLAN: Cycles back to replanner -> plan_executor.
    - NEEDS_USER_INPUT / BLOCKED / FAILED: Routes to validation & synthesis.
    - OBJECTIVE_COMPLETE: Runs conditional RAG grounding or proceeds to validation.
    """
    status = state.get("objective_status", "OBJECTIVE_COMPLETE")
    if status == "NEEDS_REPLAN":
        return "replanner"
    elif status in ["NEEDS_USER_INPUT", "BLOCKED", "FAILED"]:
        return "validation"

    should_rag, _ = should_trigger_rag_grounding(state)
    if should_rag:
        return "rag_grounding"
    return "validation"


def create_orchestrator_graph():
    """Build and compile the canonical LangGraph StateGraph for FarmFusion (Phase F7)."""
    builder = StateGraph(OrchestratorState)
    builder.add_node("intent_classification", intent_classification_node)
    builder.add_node("planner", planner_node)
    builder.add_node("plan_executor", plan_executor_node)
    builder.add_node("objective_evaluator", objective_evaluator_node)
    builder.add_node("replanner", replanner_node)
    builder.add_node("rag_grounding", rag_grounding_node)
    builder.add_node("validation", validation_node)
    builder.add_node("response_synthesizer", response_synthesizer_node)

    # Entry edge
    builder.add_edge(START, "intent_classification")
    builder.add_conditional_edges(
        "intent_classification",
        _route_after_intent,
        {
            "validation": "validation",
            "planner": "planner",
        }
    )
    builder.add_conditional_edges(
        "planner",
        _route_after_planner,
        {
            "objective_evaluator": "objective_evaluator",
            "plan_executor": "plan_executor",
        }
    )

    # Execution -> Evaluation
    builder.add_edge("plan_executor", "objective_evaluator")

    # Observation / Evaluation -> Decision Router (Cycle or Complete)
    builder.add_conditional_edges(
        "objective_evaluator",
        _route_after_evaluator,
        {
            "replanner": "replanner",
            "rag_grounding": "rag_grounding",
            "validation": "validation",
        }
    )

    # Replan cycle edge: replanner re-invokes plan_executor
    builder.add_edge("replanner", "plan_executor")

    # RAG -> Validation -> Synthesizer -> END
    builder.add_edge("rag_grounding", "validation")
    builder.add_edge("validation", "response_synthesizer")
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
    image_bytes: Optional[bytes] = None,
    image_path: Optional[str] = None,
) -> OrchestratorState:
    """
    Execute the full orchestrator graph turn via LangGraph StateGraph:
    1. State initialization with multi-turn context
    2. Intent classification & semantic extraction
    3. Task planning with dependency resolution & input gates
    4. Parallel/sequential execution via ToolRegistry
    5. Response synthesis with zero data fabrication
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
        "image_bytes": image_bytes,
        "image_path": image_path,
        "task_plan": None,
        "pending_tasks": [],
        "completed_tasks": [],
        "failed_tasks": [],
        "tool_results": {},
        "unresolved_inputs": [],
        "next_action": None,
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
        "iteration": 0,
        "max_iterations": 2,
        "replan_count": 0,
        "objective_status": None,
        "replan_reason": None,
        "completed_capabilities": [],
        "failed_capabilities": [],
        "missing_requirements": [],
        "orchestration_traces": [],
    }



    config = {"configurable": {"thread_id": session_id}}
    result_state = await orchestrator_graph.ainvoke(initial_state, config=config)
    return result_state
