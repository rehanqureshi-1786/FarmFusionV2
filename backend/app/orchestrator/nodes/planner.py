"""
Task Planner Node for LangGraph Orchestrator.
Translates canonical SemanticFrame into a dependency-aware TaskPlan.
"""
from typing import Any, Dict, Optional
import structlog

from app.orchestrator.state import OrchestratorState
from app.schemas.semantic_frame import SemanticFrame
from app.orchestrator.planner import (
    generate_task_plan,
    ActionType,
    TaskStatus,
)

logger = structlog.get_logger(__name__)


async def planner_node(state: OrchestratorState) -> OrchestratorState:
    """LangGraph node: generates execution plan from semantic frame and context."""
    sf_dict = state.get("semantic_frame")
    farmer_ctx = state.get("farmer_context", {}) or {}

    logger.info("planner_node_start", session_id=state.get("session_id"))

    if not sf_dict:
        # Fallback if semantic frame missing: direct clarification
        logger.warning("planner_node_missing_semantic_frame")
        state["requires_clarification"] = True
        state["clarification_question"] = "कृपया अपना प्रश्न पुनः कहें।"
        state["next_action"] = "CLARIFY"
        return state

    semantic_frame = SemanticFrame.model_validate(sf_dict)

    # Generate plan
    plan = generate_task_plan(
        semantic_frame=semantic_frame,
        farmer_context=farmer_ctx,
        session_state=state,
        image_bytes=state.get("image_bytes"),
        image_path=state.get("image_path"),
    )

    # Populate OrchestratorState fields
    state["task_plan"] = plan.model_dump()
    state["pending_tasks"] = [t.task_id for t in plan.tasks if t.status == TaskStatus.PENDING]
    state["completed_tasks"] = []
    state["failed_tasks"] = []
    state["unresolved_inputs"] = plan.unresolved_inputs
    state["next_action"] = plan.action_type.value

    if plan.action_type == ActionType.NAVIGATE:
        state["last_navigation_destination"] = plan.navigation_destination
        state["tool_output"] = {
            "action": "NAVIGATE",
            "destination": plan.navigation_destination,
            "android_route": plan.navigation_route,
            "required_input": plan.required_input.value if plan.required_input else None,
            "message": plan.clarification_message or f"Navigating to {plan.navigation_destination}.",
        }
        state["tool_status"] = "requires_photo" if plan.navigation_destination == "DISEASE_SCAN" else "success"

    elif plan.action_type in [ActionType.CLARIFY, ActionType.REQUEST_INPUT]:
        state["requires_clarification"] = True
        state["clarification_question"] = plan.clarification_message

    logger.info(
        "planner_node_complete",
        plan_id=plan.plan_id,
        action=plan.action_type.value,
        task_count=len(plan.tasks),
        batches=len(plan.execution_batches),
    )
    return state
