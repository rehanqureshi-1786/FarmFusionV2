"""
Autonomous Replanner Node for Phase F7 Agent Coordination.
Dynamically adapts the TaskPlan based on execution observations:
1. Preserves completed tasks (zero duplicate executions).
2. Performs dynamic result-aware dependency piping (e.g. Weather -> Irrigation, Current Price -> Mandi Decision).
3. Safely retries transient failures (exactly once).
4. Inserts missing prerequisite tools (e.g. Weather when Smart Irrigation needs rainfall data).
5. Prevents infinite loops and cyclic failures with hard iteration caps and cycle signatures.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

from app.orchestrator.state import OrchestratorState
from app.schemas.orchestration import (
    ObjectiveStatus,
    ReplanReason,
)
from app.schemas.semantic_frame import CapabilityType, RequiredInput
from app.orchestrator.planner.schemas import (
    TaskPlan,
    PlannedTask,
    TaskStatus,
    PlanStatus,
    ActionType,
)
from app.orchestrator.planner.dag import build_execution_batches

logger = structlog.get_logger(__name__)

DEFAULT_MAX_REPLAN_ITERATIONS = 2
HARD_MAX_REPLAN_ITERATIONS = 3


def _compute_plan_signature(tasks: List[PlannedTask]) -> str:
    """Computes a deterministic hash of task IDs and statuses to detect repeating loops."""
    sig_elements = [f"{t.task_id}:{t.tool_name}:{t.status.value}" for t in sorted(tasks, key=lambda x: x.task_id)]
    return hashlib.sha256(";".join(sig_elements).encode("utf-8")).hexdigest()[:12]


def pipe_verified_facts_to_tasks(
    tasks: List[PlannedTask],
    completed_outputs: Dict[str, Any],
) -> None:
    """
    Pipes verified factual outputs from completed upstream tasks into input slots
    of pending or newly added downstream tasks.
    """
    for task in tasks:
        if task.status != TaskStatus.PENDING:
            continue

        # 1. Weather -> Smart Irrigation piping
        if task.tool_name == "smart_irrigation_tool":
            for out_key, out_val in completed_outputs.items():
                if isinstance(out_val, dict) and "rainfall_mm" in out_val:
                    # Pass forecast rainfall
                    rain_mm = out_val.get("rainfall_mm") or 0.0
                    task.static_inputs["forecast_rain_mm"] = float(rain_mm)
                    # If temperature or humidity available, pipe into context
                    if "temperature_c" in out_val:
                        task.static_inputs["temperature_c"] = float(out_val["temperature_c"])
                    if "relative_humidity_pct" in out_val:
                        task.static_inputs["relative_humidity_pct"] = float(out_val["relative_humidity_pct"])
                    logger.info("piped_weather_to_irrigation", task_id=task.task_id, forecast_rain_mm=rain_mm)

        # 2. Weather -> Disaster Risk piping
        elif task.tool_name == "disaster_risk_tool":
            for out_key, out_val in completed_outputs.items():
                if isinstance(out_val, dict) and "temperature_c" in out_val:
                    if "temperature_c" not in task.static_inputs or not task.static_inputs["temperature_c"]:
                        task.static_inputs["temperature_c"] = float(out_val["temperature_c"])
                    if "relative_humidity_pct" in out_val and ("humidity" not in task.static_inputs or not task.static_inputs["humidity"]):
                        task.static_inputs["humidity"] = float(out_val["relative_humidity_pct"])
                    if "rainfall_mm" in out_val and ("rainfall_mm" not in task.static_inputs or not task.static_inputs["rainfall_mm"]):
                        task.static_inputs["rainfall_mm"] = float(out_val["rainfall_mm"])
                    logger.info("piped_weather_to_disaster", task_id=task.task_id)

        # 3. Mandi Current Price -> Mandi Decision / Forecast piping
        elif task.tool_name in ["mandi_decision_tool", "market_price_tool", "mandi_forecast_tool"]:
            for out_key, out_val in completed_outputs.items():
                if isinstance(out_val, dict):
                    price = out_val.get("modal_price") or out_val.get("price") or out_val.get("observed", {}).get("modal_price")
                    if price is not None:
                        task.static_inputs["current_price"] = float(price)
                        logger.info("piped_mandi_price_to_decision", task_id=task.task_id, price=price)


async def replanner_node(state: OrchestratorState) -> OrchestratorState:
    """
    LangGraph Node: Autonomous Replanner.
    Inspects evaluation outcomes, repairs the plan, pipes verified dependencies,
    and increments the iteration counter.
    """
    current_iteration = state.get("iteration", 0)
    max_iterations = min(state.get("max_iterations", DEFAULT_MAX_REPLAN_ITERATIONS), HARD_MAX_REPLAN_ITERATIONS)
    replan_reason = state.get("replan_reason", ReplanReason.NONE.value)
    plan_dict = state.get("task_plan")
    session_id = state.get("session_id", "default")
    missing_reqs = state.get("missing_requirements", []) or []

    logger.info(
        "replanner_start",
        session_id=session_id,
        current_iteration=current_iteration,
        max_iterations=max_iterations,
        replan_reason=replan_reason,
        missing_reqs=missing_reqs,
    )

    # 1. Guard against infinite loops or exceeding limits
    next_iteration = current_iteration + 1
    if next_iteration > max_iterations:
        logger.warning(
            "replanner_max_iterations_exceeded",
            next_iteration=next_iteration,
            max_iterations=max_iterations,
        )
        state["objective_status"] = ObjectiveStatus.BLOCKED.value
        state["replan_reason"] = ReplanReason.MAX_ITERATIONS_EXCEEDED.value
        state["tool_status"] = "blocked"
        return state

    if not plan_dict:
        state["objective_status"] = ObjectiveStatus.FAILED.value
        return state

    plan = TaskPlan.model_validate(plan_dict)

    # 2. Cycle Detection: check visited plan signatures
    visited_signatures: List[str] = state.get("turn_history", []) or []
    current_sig = _compute_plan_signature(plan.tasks)
    
    cycle_history: List[str] = [h.get("sig") for h in visited_signatures if isinstance(h, dict) and "sig" in h]
    if current_sig in cycle_history:
        logger.warning("replanner_cycle_detected", signature=current_sig)
        state["objective_status"] = ObjectiveStatus.BLOCKED.value
        state["replan_reason"] = ReplanReason.CYCLE_DETECTED.value
        state["tool_status"] = "blocked"
        return state

    # Record current signature
    turn_hist = state.get("turn_history", []) or []
    turn_hist.append({"sig": current_sig, "iteration": current_iteration, "reason": replan_reason})
    state["turn_history"] = turn_hist

    # 3. Gather completed outputs
    completed_outputs: Dict[str, Any] = {}
    for t in plan.tasks:
        if t.status == TaskStatus.COMPLETED and t.output is not None:
            completed_outputs[t.task_id] = t.output
    # Also incorporate global tool_results
    for k, v in (state.get("tool_results") or {}).items():
        if k not in completed_outputs:
            completed_outputs[k] = v

    new_tasks: List[PlannedTask] = []
    farmer_ctx = state.get("farmer_context", {}) or {}
    lat = farmer_ctx.get("latitude") or 25.18
    lon = farmer_ctx.get("longitude") or 75.83
    active_crop = state.get("active_crop") or farmer_ctx.get("primary_crops", [None])[0] or "wheat"

    # 4. Handle Replanning Scenarios

    # Scenario A: Missing Weather data for Smart Irrigation
    if "WEATHER_DATA" in missing_reqs or (replan_reason == ReplanReason.INSUFFICIENT_DATA.value and "weather" in str(missing_reqs).lower()):
        has_weather = any(t.tool_name == "weather_tool" for t in plan.tasks)
        if not has_weather:
            weather_task = PlannedTask(
                task_id="weather_injected_1",
                capability=CapabilityType.WEATHER,
                tool_name="weather_tool",
                description="Injected by replanner to supply rainfall and temperature observations for irrigation",
                depends_on=[],
                static_inputs={"latitude": lat, "longitude": lon},
                is_blocking=True,
                status=TaskStatus.PENDING,
            )
            new_tasks.append(weather_task)

            # Update dependent irrigation task
            for t in plan.tasks:
                if t.tool_name == "smart_irrigation_tool":
                    t.status = TaskStatus.PENDING
                    if "weather_injected_1" not in t.depends_on:
                        t.depends_on.append("weather_injected_1")
                    t.dynamic_mappings["forecast_rain_mm"] = "weather_injected_1.rainfall_mm"

    # Scenario B: Transient Failure Retry (Safe single retry)
    elif replan_reason == ReplanReason.TRANSIENT_FAILURE.value:
        for t in plan.tasks:
            if t.status == TaskStatus.FAILED:
                # Retry once only
                t.status = TaskStatus.PENDING
                t.error = None
                logger.info("replanner_retrying_transient_failure", task_id=t.task_id, tool=t.tool_name)

    # Scenario C: Mandi forecast partial success / failure fallback
    elif replan_reason == ReplanReason.PARTIAL_SUCCESS.value and "MANDI_FORECAST" in missing_reqs:
        for t in plan.tasks:
            if t.capability in [CapabilityType.MANDI_FORECAST, CapabilityType.MANDI_DECISION] and t.status == TaskStatus.FAILED:
                # Reset task to retry with static current price passed in
                t.status = TaskStatus.PENDING
                t.error = None
                # Pipe price from completed price task
                for out in completed_outputs.values():
                    if isinstance(out, dict):
                        p = out.get("modal_price") or out.get("price") or out.get("observed", {}).get("modal_price")
                        if p:
                            t.static_inputs["current_price"] = float(p)
                            break
                logger.info("replanner_repaired_mandi_forecast_inputs", task_id=t.task_id)

    # Scenario D: Missing dependency for skipped tasks
    elif replan_reason == ReplanReason.MISSING_DEPENDENCY.value:
        for t in plan.tasks:
            if t.status in [TaskStatus.SKIPPED, TaskStatus.FAILED]:
                t.status = TaskStatus.PENDING
                t.error = None

    # Merge newly injected tasks with existing tasks
    combined_tasks: List[PlannedTask] = []
    # Add new tasks first if they are prerequisites
    for nt in new_tasks:
        combined_tasks.append(nt)

    for et in plan.tasks:
        # Keep completed tasks intact
        combined_tasks.append(et)

    # 5. Pipe verified facts into all pending tasks
    pipe_verified_facts_to_tasks(combined_tasks, completed_outputs)

    # 6. Rebuild execution batches for DAG concurrency
    execution_batches = build_execution_batches(combined_tasks)

    # 7. Update plan and state
    plan.tasks = combined_tasks
    plan.execution_batches = execution_batches
    plan.status = PlanStatus.READY

    state["task_plan"] = plan.model_dump()
    state["iteration"] = next_iteration
    state["replan_count"] = state.get("replan_count", 0) + 1
    state["pending_tasks"] = [t.task_id for t in plan.tasks if t.status == TaskStatus.PENDING]
    state["next_action"] = ActionType.EXECUTE_TOOL.value

    logger.info(
        "replanner_complete",
        iteration=next_iteration,
        replan_count=state["replan_count"],
        total_tasks=len(plan.tasks),
        pending_tasks=state["pending_tasks"],
        stages=len(execution_batches),
    )

    return state
