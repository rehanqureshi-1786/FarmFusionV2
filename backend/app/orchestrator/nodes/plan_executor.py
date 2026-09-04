"""
Plan Executor Node for LangGraph Orchestrator.
Executes planned tasks concurrently within stages and sequentially across dependencies.
"""
from typing import Any, Dict, Optional
import structlog

from app.orchestrator.state import OrchestratorState
from app.orchestrator.planner import (
    TaskPlan,
    execute_task_plan,
    TaskStatus,
    PlanStatus,
    ActionType,
)

logger = structlog.get_logger(__name__)


async def plan_executor_node(state: OrchestratorState) -> OrchestratorState:
    """LangGraph node: executes the task plan batch-by-batch through ToolRegistry."""
    next_action = state.get("next_action")
    plan_dict = state.get("task_plan")

    if not plan_dict or next_action != ActionType.EXECUTE_TOOL.value:
        logger.info("plan_executor_bypassed", next_action=next_action)
        return state

    plan = TaskPlan.model_validate(plan_dict)
    farmer_ctx = state.get("farmer_context", {}) or {}

    logger.info("plan_executor_start", plan_id=plan.plan_id, stages=len(plan.execution_batches))

    # Run controlled executor
    executed_plan = await execute_task_plan(plan, context=farmer_ctx)

    # Sync state with execution outcomes
    state["task_plan"] = executed_plan.model_dump()
    state["completed_tasks"] = [t.task_id for t in executed_plan.tasks if t.status == TaskStatus.COMPLETED]
    state["failed_tasks"] = [t.task_id for t in executed_plan.tasks if t.status == TaskStatus.FAILED]
    state["pending_tasks"] = [t.task_id for t in executed_plan.tasks if t.status == TaskStatus.PENDING]

    tool_results: Dict[str, Any] = {}
    for task in executed_plan.tasks:
        if task.output is not None:
            tool_results[task.task_id] = task.output

    state["tool_results"] = tool_results

    # Synchronize backward-compatible legacy fields
    if executed_plan.tasks:
        # Pick primary agricultural specialist task if available, rather than secondary RAG task
        primary_task = next(
            (t for t in reversed(executed_plan.tasks) if t.tool_name not in ["rag_search_tool", "rag_retrieval_tool"] and t.output is not None),
            executed_plan.tasks[-1]
        )
        state["last_tool"] = primary_task.tool_name
        state["last_tool_result"] = primary_task.output
        state["tool_output"] = primary_task.output
        state["tool_status"] = "success" if executed_plan.status == PlanStatus.COMPLETED else "partial_success"

        # Update specific session memories based on executed capabilities
        for t in executed_plan.tasks:
            if t.status != TaskStatus.COMPLETED or not t.output:
                continue

            if t.tool_name == "crop_recommendation_tool":
                recs = t.output.get("recommendations") or t.output.get("top_crops") or []
                state["last_recommendations"] = recs
                if recs:
                    state["active_crop"] = recs[0].get("crop_name")

            elif t.tool_name == "weather_tool":
                state["last_weather_result"] = t.output

            elif t.tool_name == "disaster_risk_tool":
                state["last_disaster_result"] = t.output

            elif t.tool_name in ["mandi_current_price_tool", "market_price_tool"]:
                state["last_market_result"] = t.output
                crop_entity = t.static_inputs.get("crop") or t.static_inputs.get("commodity")
                if crop_entity:
                    state["active_crop"] = crop_entity

    logger.info(
        "plan_executor_complete",
        plan_id=executed_plan.plan_id,
        completed_tasks=state["completed_tasks"],
        failed_tasks=state["failed_tasks"],
    )
    return state
