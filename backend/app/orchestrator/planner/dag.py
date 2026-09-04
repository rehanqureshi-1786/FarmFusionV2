"""
Dependency Graph (DAG) and Topological Batching for FarmFusion Task Planner.
Validates dependencies, detects cycles, and calculates parallel execution stages.
"""
from __future__ import annotations

from typing import Dict, List, Set
from app.orchestrator.planner.schemas import PlannedTask


class DAGCycleError(ValueError):
    """Raised when a circular dependency is detected among planned tasks."""
    pass


class InvalidDependencyError(ValueError):
    """Raised when a task depends on an unknown task_id."""
    pass


def build_execution_batches(tasks: List[PlannedTask]) -> List[List[str]]:
    """
    Computes parallel execution stages (batches) using topological sort.
    Tasks within the same batch have zero dependencies on each other and can execute concurrently.
    
    Returns:
        List[List[str]]: Ordered batches of task_ids, e.g. [["weather_1", "mandi_1"], ["irrigation_1"]]
    """
    if not tasks:
        return []

    task_map: Dict[str, PlannedTask] = {t.task_id: t for t in tasks}
    all_task_ids: Set[str] = set(task_map.keys())

    # 1. Validate all dependencies exist
    for task in tasks:
        for dep in task.depends_on:
            if dep not in all_task_ids:
                raise InvalidDependencyError(
                    f"Task '{task.task_id}' depends on unknown task '{dep}'"
                )

    # 2. Track remaining incoming dependencies per task
    remaining_deps: Dict[str, Set[str]] = {
        t.task_id: set(t.depends_on) for t in tasks
    }
    completed: Set[str] = set()
    batches: List[List[str]] = []

    while len(completed) < len(tasks):
        # Find all tasks whose prerequisites are completely satisfied
        ready_in_stage: List[str] = [
            tid for tid, deps in remaining_deps.items()
            if tid not in completed and deps.issubset(completed)
        ]

        if not ready_in_stage:
            # Deadlock / cycle detected
            unresolved = [tid for tid in all_task_ids if tid not in completed]
            raise DAGCycleError(
                f"Circular dependency detected among tasks: {unresolved}"
            )

        # Deterministic sort for reproducible execution order
        ready_in_stage.sort()
        batches.append(ready_in_stage)
        completed.update(ready_in_stage)

    return batches
