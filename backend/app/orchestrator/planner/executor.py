"""
Controlled Execution Engine for FarmFusion Task Plans.
Executes planned tasks batch-by-batch: concurrent execution within stages,
sequential synchronization across stages, dynamic result propagation, and graceful failure handling.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import structlog

from app.tools.registry import tool_registry, ToolStatus
from app.orchestrator.planner.schemas import (
    TaskPlan,
    PlannedTask,
    PlanStatus,
    TaskStatus,
    ActionType,
)

logger = structlog.get_logger(__name__)


def _extract_nested_value(data: Dict[str, Any], path: str) -> Any:
    """Extract a value from a nested dictionary given a dot-separated path."""
    parts = path.split(".")
    curr = data
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return None
    return curr


async def _execute_single_task(
    task: PlannedTask,
    context: Dict[str, Any]
) -> None:
    """Executes a single tool task through ToolRegistry and records output in-place."""
    task.status = TaskStatus.RUNNING
    start_time = time.perf_counter()
    logger.info("executing_planned_task", task_id=task.task_id, tool=task.tool_name, inputs=task.static_inputs)

    try:
        res = await tool_registry.execute(task.tool_name, task.static_inputs, context)
        task.duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        if res.status in [ToolStatus.SUCCESS, ToolStatus.REQUIRES_PHOTO]:
            task.status = TaskStatus.COMPLETED
            task.output = res.data or {}
            logger.info("planned_task_completed", task_id=task.task_id, status=res.status.value, duration_ms=task.duration_ms)
        else:
            task.status = TaskStatus.FAILED
            task.error = res.message
            task.output = res.data
            logger.warning("planned_task_failed", task_id=task.task_id, status=res.status.value, error=res.message)

    except Exception as exc:
        task.duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        task.status = TaskStatus.FAILED
        task.error = str(exc)
        logger.error("planned_task_exception", task_id=task.task_id, error=str(exc))


async def execute_task_plan(
    plan: TaskPlan,
    context: Optional[Dict[str, Any]] = None
) -> TaskPlan:
    """
    Executes a TaskPlan batch-by-batch:
    1. Propagates outputs from completed tasks to dependent downstream inputs
    2. Runs tasks in each execution batch in parallel via asyncio.gather
    3. Handles blocking vs non-blocking failures gracefully
    """
    ctx = context or {}
    plan.status = PlanStatus.EXECUTING

    # If action is non-tool (NAVIGATE, CLARIFY, etc.), return immediately
    if plan.action_type != ActionType.EXECUTE_TOOL:
        plan.status = PlanStatus.COMPLETED
        plan.completed_at = datetime.now(timezone.utc).isoformat()
        return plan

    task_map: Dict[str, PlannedTask] = {t.task_id: t for t in plan.tasks}
    any_blocking_failed = False

    for batch_idx, batch in enumerate(plan.execution_batches):
        tasks_to_run: List[PlannedTask] = []

        for task_id in batch:
            task = task_map[task_id]

            # Skip tasks that are already completed in earlier iterations
            if task.status == TaskStatus.COMPLETED:
                continue

            # Check upstream dependencies
            deps_failed = False
            for dep_id in task.depends_on:
                dep_task = task_map.get(dep_id)
                if dep_task and dep_task.status == TaskStatus.FAILED:
                    deps_failed = True
                    break

            if deps_failed:
                task.status = TaskStatus.SKIPPED
                task.error = "Prerequisite dependency failed."
                logger.warning("task_skipped_due_to_dependency_failure", task_id=task.task_id)
                continue

            # Resolve dynamic result dependencies from completed upstream tasks
            for target_field, source_path in task.dynamic_mappings.items():
                parts = source_path.split(".", 1)
                src_task_id = parts[0]
                field_path = parts[1] if len(parts) > 1 else None

                src_task = task_map.get(src_task_id)
                if src_task and src_task.output and field_path:
                    val = _extract_nested_value(src_task.output, field_path)
                    if val is not None:
                        # If value is a list (e.g. active hazards), format as string
                        if isinstance(val, list):
                            val = ", ".join(str(v) for v in val)
                        task.static_inputs[target_field] = str(val)

            tasks_to_run.append(task)

        # Execute all tasks in this batch concurrently
        if tasks_to_run:
            coroutines = [_execute_single_task(t, ctx) for t in tasks_to_run]
            await asyncio.gather(*coroutines)

        # Check if any blocking task in this batch failed
        for task in tasks_to_run:
            if task.status == TaskStatus.FAILED and task.is_blocking:
                any_blocking_failed = True
                plan.errors.append(f"Blocking task '{task.task_id}' failed: {task.error}")

        if any_blocking_failed:
            logger.warning("blocking_task_failure_halting_plan", batch_index=batch_idx)
            # Mark remaining tasks in subsequent batches as SKIPPED
            for rem_batch in plan.execution_batches[batch_idx + 1:]:
                for rem_id in rem_batch:
                    rem_task = task_map.get(rem_id)
                    if rem_task and rem_task.status == TaskStatus.PENDING:
                        rem_task.status = TaskStatus.SKIPPED
                        rem_task.error = "Execution halted due to upstream blocking failure."
            break

    # Final plan status
    completed_count = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
    total_count = len(plan.tasks)

    if any_blocking_failed:
        plan.status = PlanStatus.FAILED if completed_count == 0 else PlanStatus.PARTIAL_SUCCESS
    elif completed_count == total_count:
        plan.status = PlanStatus.COMPLETED
    else:
        plan.status = PlanStatus.PARTIAL_SUCCESS

    plan.completed_at = datetime.now(timezone.utc).isoformat()
    plan.execution_summary = f"Executed {completed_count}/{total_count} tasks successfully across {len(plan.execution_batches)} stages."
    logger.info("task_plan_execution_complete", plan_id=plan.plan_id, status=plan.status.value, summary=plan.execution_summary)
    return plan
