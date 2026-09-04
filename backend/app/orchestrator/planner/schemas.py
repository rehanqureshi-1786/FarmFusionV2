"""
Strongly-typed Pydantic schemas for Phase F5 Task Planner.
Defines the structure for TaskPlan, PlannedTask, Dependencies, and Batches.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.schemas.semantic_frame import CapabilityType, RequiredInput


class PlanStatus(str, Enum):
    """Lifecycle status of a TaskPlan."""
    READY = "READY"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskStatus(str, Enum):
    """Execution status of an individual PlannedTask."""
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    BLOCKED = "BLOCKED"


class ActionType(str, Enum):
    """Planner decision action type."""
    EXECUTE_TOOL = "EXECUTE_TOOL"
    NAVIGATE = "NAVIGATE"
    REQUEST_INPUT = "REQUEST_INPUT"
    CLARIFY = "CLARIFY"
    ANSWER_DIRECT = "ANSWER_DIRECT"


class TaskDependency(BaseModel):
    """Dependency declaration connecting an upstream task output to a downstream task input."""
    source_task_id: str = Field(..., description="ID of the task that must complete first")
    target_task_id: str = Field(..., description="ID of the dependent task")
    required: bool = Field(default=True, description="Whether failure of source task blocks this task")
    field_mappings: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from source output path to target input field, e.g. {'disease_name': 'crop'}"
    )


class PlannedTask(BaseModel):
    """An individual tool invocation task within a plan."""
    task_id: str = Field(..., description="Unique task identifier, e.g. 'weather_1', 'irrigation_1'")
    capability: CapabilityType = Field(..., description="Canonical capability this task fulfills")
    tool_name: str = Field(..., description="Registered tool name in ToolRegistry")
    description: str = Field(default="", description="Human-readable explanation of why task is run")
    depends_on: List[str] = Field(default_factory=list, description="List of prerequisite task_ids")
    static_inputs: Dict[str, Any] = Field(default_factory=dict, description="Inputs resolved from entities and context")
    dynamic_mappings: Dict[str, str] = Field(
        default_factory=dict,
        description="Dynamic input fields populated from upstream task outputs, e.g. {'query': 'disease_1.disease_name'}"
    )
    is_blocking: bool = Field(default=True, description="If True, failure of this task stops downstream tasks")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    output: Optional[Dict[str, Any]] = Field(default=None, description="Output payload after execution")
    error: Optional[str] = Field(default=None, description="Error message if task failed")
    duration_ms: Optional[float] = Field(default=None, description="Execution runtime in milliseconds")


class ExecutionBatch(BaseModel):
    """A stage of independent tasks that can be executed concurrently."""
    batch_index: int
    task_ids: List[str] = Field(..., description="Task IDs that can run in parallel in this stage")


class TaskPlan(BaseModel):
    """Canonical dependency-aware execution plan."""
    plan_id: str = Field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:12]}")
    session_id: Optional[str] = Field(default=None)
    objective: str = Field(..., description="Summary of farmer goal")
    action_type: ActionType = Field(default=ActionType.EXECUTE_TOOL)
    tasks: List[PlannedTask] = Field(default_factory=list)
    execution_batches: List[List[str]] = Field(
        default_factory=list,
        description="Stages of parallel execution batches: [[task1, task2], [task3]]"
    )
    status: PlanStatus = Field(default=PlanStatus.READY)
    required_input: Optional[RequiredInput] = Field(default=None, description="Sensory or user input missing")
    navigation_destination: Optional[str] = Field(default=None, description="Destination screen if action is NAVIGATE")
    navigation_route: Optional[str] = Field(default=None, description="Android route string")
    clarification_message: Optional[str] = Field(default=None, description="Message to user if action is CLARIFY")
    unresolved_inputs: List[str] = Field(default_factory=list, description="Names of missing required slots")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = Field(default=None)
    errors: List[str] = Field(default_factory=list)
    execution_summary: Optional[str] = Field(default=None)

    def get_task(self, task_id: str) -> Optional[PlannedTask]:
        """Retrieve task by task_id."""
        for t in self.tasks:
            if t.task_id == task_id:
                return t
        return None
