"""
Objective Evaluator Node for Phase F7 Autonomous Replanning.
Deterministically evaluates execution outcomes against the farmer's goal:
- OBJECTIVE_COMPLETE: All planned capabilities succeeded with sufficient evidence.
- NEEDS_REPLAN: Partial success, recoverable tool failure, or missing dynamic dependency.
- NEEDS_USER_INPUT: Prerequisite sensory or farm input required (e.g. leaf photo).
- BLOCKED: Safety violation, unresolvable contradiction, or maximum iteration limit reached.
- FAILED: Unrecoverable tool failure with no alternative execution path.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
import structlog

from app.orchestrator.state import OrchestratorState
from app.schemas.orchestration import (
    ObjectiveStatus,
    ReplanReason,
    ExecutionTrace,
)
from app.schemas.semantic_frame import CapabilityType, RequiredInput
from app.orchestrator.planner.schemas import (
    TaskPlan,
    PlannedTask,
    TaskStatus,
    PlanStatus,
    ActionType,
)

logger = structlog.get_logger(__name__)

# Capability dependencies and alternative tool providers
CAPABILITY_ALTERNATIVES: Dict[str, List[str]] = {
    "SMART_IRRIGATION": ["weather_tool", "soil_service"],
    "MANDI_FORECAST": ["mandi_history_tool", "mandi_forecast_tool"],
    "CROP_RECOMMENDATION": ["no_soil_crop_service", "crop_recommendation_tool"],
    "WEATHER": ["weather_tool"],
}


def _evaluate_task_execution(
    plan: TaskPlan,
    state: OrchestratorState,
) -> Tuple[ObjectiveStatus, ReplanReason, List[str], Optional[str]]:
    """
    Deterministically evaluates executed tasks in the plan.
    Returns (ObjectiveStatus, ReplanReason, missing_requirements, details).
    """
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 2)
    next_action = state.get("next_action")

    # 1. Non-tool execution plans (NAVIGATE, CLARIFY, REQUEST_INPUT)
    if plan.action_type == ActionType.NAVIGATE:
        if plan.required_input == RequiredInput.LEAF_IMAGE or plan.navigation_destination == "DISEASE_SCAN":
            return (
                ObjectiveStatus.NEEDS_USER_INPUT,
                ReplanReason.NONE,
                ["LEAF_IMAGE"],
                "Leaf image required for plant disease scanning.",
            )
        return ObjectiveStatus.OBJECTIVE_COMPLETE, ReplanReason.NONE, [], "Navigation plan completed."

    if plan.action_type in [ActionType.CLARIFY, ActionType.REQUEST_INPUT]:
        req_inputs = [plan.required_input.value] if plan.required_input else plan.unresolved_inputs
        return (
            ObjectiveStatus.NEEDS_USER_INPUT,
            ReplanReason.NONE,
            req_inputs,
            plan.clarification_message or "Missing required farmer input.",
        )

    # 2. Check empty tasks
    if not plan.tasks:
        if plan.required_input and plan.required_input != RequiredInput.NONE:
            return (
                ObjectiveStatus.NEEDS_USER_INPUT,
                ReplanReason.NONE,
                [plan.required_input.value],
                f"Missing sensory or farmer input: {plan.required_input.value}",
            )
        return ObjectiveStatus.OBJECTIVE_COMPLETE, ReplanReason.NONE, [], "Empty plan completed."

    # 3. Check hard iteration limit
    if iteration >= max_iterations:
        logger.warning(
            "replan_maximum_iterations_exceeded",
            iteration=iteration,
            max_iterations=max_iterations,
        )
        return (
            ObjectiveStatus.BLOCKED,
            ReplanReason.MAX_ITERATIONS_EXCEEDED,
            [],
            f"Maximum replan iteration limit ({max_iterations}) reached without complete resolution.",
        )

    # 4. Analyze task outcomes
    completed_tasks = [t for t in plan.tasks if t.status == TaskStatus.COMPLETED]
    failed_tasks = [t for t in plan.tasks if t.status == TaskStatus.FAILED]
    skipped_tasks = [t for t in plan.tasks if t.status == TaskStatus.SKIPPED]

    # Check for missing user input errors from executed tools (e.g. requires photo)
    for t in failed_tasks + completed_tasks:
        output_data = t.output or {}
        # Case: Tool reports requires photo or missing leaf image
        if (
            output_data.get("action") == "NAVIGATE" and output_data.get("destination") == "DISEASE_SCAN"
        ) or output_data.get("required_input") == "LEAF_IMAGE":
            return (
                ObjectiveStatus.NEEDS_USER_INPUT,
                ReplanReason.NONE,
                ["LEAF_IMAGE"],
                "Tool execution determined leaf photo is required.",
            )

    # 5. Check failed tasks for recoverable vs unrecoverable errors
    if failed_tasks:
        # Check if any failure is due to missing data that can be fetched by another tool
        for ft in failed_tasks:
            err_msg = (ft.error or "").lower()
            cap = ft.capability.value if hasattr(ft.capability, "value") else str(ft.capability)

            # Smart irrigation reports insufficient data (e.g. needs rainfall or soil moisture)
            if "insufficient_data" in err_msg or "missing" in err_msg or "data" in err_msg:
                # If weather hasn't run yet or rainfall wasn't passed, replan to run weather first
                has_weather_run = any(
                    t.tool_name == "weather_tool" and t.status == TaskStatus.COMPLETED
                    for t in plan.tasks
                )
                if not has_weather_run and cap in ["SMART_IRRIGATION", "IRRIGATION_ADVISORY"]:
                    return (
                        ObjectiveStatus.NEEDS_REPLAN,
                        ReplanReason.INSUFFICIENT_DATA,
                        ["WEATHER_DATA"],
                        f"Task '{ft.task_id}' needs weather/rainfall data. Replanning to execute weather tool.",
                    )

            # Transient network/timeout failure: safe to retry once
            if any(term in err_msg for term in ["timeout", "network", "temporary", "connection", "503", "504"]):
                return (
                    ObjectiveStatus.NEEDS_REPLAN,
                    ReplanReason.TRANSIENT_FAILURE,
                    [],
                    f"Transient failure on task '{ft.task_id}': {ft.error}. Safe to retry.",
                )

            # Mandi Forecast failure during Mandi Decision
            if cap in ["MANDI_FORECAST", "MANDI_DECISION"]:
                # Check if we have current price
                has_price = any(
                    t.capability in [CapabilityType.CURRENT_PRICE, CapabilityType.MANDI_CURRENT_PRICE]
                    and t.status == TaskStatus.COMPLETED
                    for t in plan.tasks
                )
                if has_price and iteration < max_iterations:
                    return (
                        ObjectiveStatus.NEEDS_REPLAN,
                        ReplanReason.PARTIAL_SUCCESS,
                        ["MANDI_FORECAST"],
                        "Current price obtained but forecast failed. Replanning forecast with adaptive fallback.",
                    )
                elif not has_price:
                    return (
                        ObjectiveStatus.BLOCKED,
                        ReplanReason.UNRESOLVABLE_TOOL_ERROR,
                        [],
                        "Cannot synthesize Mandi decision without verified price data.",
                    )

        # Non-recoverable failure on a blocking task
        blocking_failures = [t for t in failed_tasks if t.is_blocking]
        if blocking_failures:
            first_fail = blocking_failures[0]
            return (
                ObjectiveStatus.FAILED,
                ReplanReason.UNRESOLVABLE_TOOL_ERROR,
                [],
                f"Blocking task '{first_fail.task_id}' failed unrecoverably: {first_fail.error}",
            )

    # 6. Compound Intent Incompleteness Checks
    # E.g. Mandi Decision requested: must have current price + forecast/decision
    intent = state.get("intent", "")
    if intent in ["mandi_decision", "sell_hold"]:
        has_price = any(
            t.status == TaskStatus.COMPLETED
            and t.capability in [CapabilityType.CURRENT_PRICE, CapabilityType.MANDI_CURRENT_PRICE, CapabilityType.MANDI_DECISION]
            for t in plan.tasks
        )
        if not has_price:
            if iteration < max_iterations:
                return (
                    ObjectiveStatus.NEEDS_REPLAN,
                    ReplanReason.MISSING_DEPENDENCY,
                    ["CURRENT_PRICE"],
                    "Mandi decision compound intent requires verified current price.",
                )
            return (
                ObjectiveStatus.BLOCKED,
                ReplanReason.UNRESOLVABLE_TOOL_ERROR,
                [],
                "Mandi decision missing mandatory price evidence.",
            )

    # 7. Check if all planned tasks completed successfully
    if len(completed_tasks) == len(plan.tasks):
        return (
            ObjectiveStatus.OBJECTIVE_COMPLETE,
            ReplanReason.NONE,
            [],
            f"All {len(completed_tasks)} tasks completed successfully with verified evidence.",
        )

    # 8. If some tasks are still pending or skipped without fatal errors
    if skipped_tasks and iteration < max_iterations:
        return (
            ObjectiveStatus.NEEDS_REPLAN,
            ReplanReason.MISSING_DEPENDENCY,
            [t.task_id for t in skipped_tasks],
            f"Dependent tasks were skipped due to upstream gaps. Replanning to repair dependencies.",
        )

    return (
        ObjectiveStatus.OBJECTIVE_COMPLETE,
        ReplanReason.NONE,
        [],
        "Objective fulfilled with current execution results.",
    )


async def objective_evaluator_node(state: OrchestratorState) -> OrchestratorState:
    """
    LangGraph Node: Deterministic Objective Evaluator.
    Evaluates actual execution outcomes, manages iteration counter, and records ExecutionTrace.
    """
    start_time = time.perf_counter()
    session_id = state.get("session_id", "default")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 2)
    plan_dict = state.get("task_plan")

    logger.info(
        "objective_evaluator_start",
        session_id=session_id,
        iteration=iteration,
        max_iterations=max_iterations,
    )

    if not plan_dict:
        # No plan present (e.g. direct clarify)
        state["objective_status"] = ObjectiveStatus.OBJECTIVE_COMPLETE.value
        state["replan_reason"] = ReplanReason.NONE.value
        return state

    plan = TaskPlan.model_validate(plan_dict)

    # Run deterministic evaluation
    status, reason, missing_reqs, details = _evaluate_task_execution(plan, state)

    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    # Extract completed and failed capabilities
    completed_caps = [
        t.capability.value if hasattr(t.capability, "value") else str(t.capability)
        for t in plan.tasks
        if t.status == TaskStatus.COMPLETED
    ]
    failed_caps = [
        t.capability.value if hasattr(t.capability, "value") else str(t.capability)
        for t in plan.tasks
        if t.status == TaskStatus.FAILED
    ]

    # Create structured ExecutionTrace for observability
    trace = ExecutionTrace(
        iteration=iteration,
        plan_id=plan.plan_id,
        tasks_executed=[t.task_id for t in plan.tasks if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]],
        successful_tasks=[t.task_id for t in plan.tasks if t.status == TaskStatus.COMPLETED],
        failed_tasks=[t.task_id for t in plan.tasks if t.status == TaskStatus.FAILED],
        objective_status=status,
        replan_reason=reason,
        replan_details=details,
        retry_count=state.get("replan_count", 0),
        latency_ms=duration_ms,
    )

    # Sync state
    traces = state.get("orchestration_traces", []) or []
    traces.append(trace.model_dump())

    state["objective_status"] = status.value
    state["replan_reason"] = reason.value
    state["missing_requirements"] = missing_reqs
    state["completed_capabilities"] = completed_caps
    state["failed_capabilities"] = failed_caps
    state["orchestration_traces"] = traces

    if status == ObjectiveStatus.NEEDS_USER_INPUT:
        state["next_action"] = "REQUEST_INPUT"
        if "LEAF_IMAGE" in missing_reqs:
            state["last_navigation_destination"] = "DISEASE_SCAN"
            state["tool_output"] = {
                "action": "NAVIGATE",
                "destination": "DISEASE_SCAN",
                "android_route": "disease_scan",
                "required_input": "LEAF_IMAGE",
                "message": "फसल की बीमारी की जांच के लिए पत्ती की साफ फोटो आवश्यक है।",
            }
            state["tool_status"] = "requires_photo"

    elif status == ObjectiveStatus.BLOCKED:
        state["next_action"] = "ANSWER"
        state["tool_status"] = "blocked"

    logger.info(
        "objective_evaluator_complete",
        session_id=session_id,
        iteration=iteration,
        objective_status=status.value,
        replan_reason=reason.value,
        completed_caps=completed_caps,
        failed_caps=failed_caps,
        duration_ms=duration_ms,
    )

    return state
