"""
Strongly-typed Pydantic schemas for Phase F7 Autonomous Replanning & Agent Coordination.
Defines ObjectiveStatus, ReplanReason, OrchestrationState, and ExecutionTrace contracts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.semantic_frame import SemanticFrame, CapabilityType, RequiredInput, ActionIntent
from app.orchestrator.planner.schemas import TaskPlan
from app.schemas.validation import VerifiedFact


class ObjectiveStatus(str, Enum):
    """Evaluation of goal fulfillment after an execution stage."""
    OBJECTIVE_COMPLETE = "OBJECTIVE_COMPLETE"
    NEEDS_REPLAN = "NEEDS_REPLAN"
    NEEDS_USER_INPUT = "NEEDS_USER_INPUT"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class ReplanReason(str, Enum):
    """Deterministic reason triggering plan adaptation."""
    NONE = "NONE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    MAX_ITERATIONS_EXCEEDED = "MAX_ITERATIONS_EXCEEDED"
    UNRESOLVABLE_TOOL_ERROR = "UNRESOLVABLE_TOOL_ERROR"
    SAFETY_BLOCK = "SAFETY_BLOCK"


class ExecutionTrace(BaseModel):
    """Structured audit record of a single execution/replanning iteration."""
    model_config = ConfigDict(extra="forbid")

    trace_id: str = Field(default_factory=lambda: f"trace-{uuid.uuid4().hex[:8]}")
    iteration: int = Field(..., ge=0, description="Iteration sequence number (0-indexed)")
    plan_id: str = Field(..., description="ID of TaskPlan evaluated")
    tasks_executed: List[str] = Field(default_factory=list, description="IDs of tasks executed in this iteration")
    successful_tasks: List[str] = Field(default_factory=list)
    failed_tasks: List[str] = Field(default_factory=list)
    objective_status: ObjectiveStatus
    replan_reason: ReplanReason = ReplanReason.NONE
    replan_details: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    latency_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OrchestrationState(BaseModel):
    """
    Complete state envelope tracking autonomous multi-step agent coordination,
    dynamic replanning, verified facts, and iteration bounds.
    """
    model_config = ConfigDict(extra="allow")

    request_id: str = Field(default_factory=lambda: f"req-{uuid.uuid4().hex[:10]}")
    request: str = Field(..., description="Original user utterance")
    semantic_frame: Optional[SemanticFrame] = Field(None, description="F2 Canonical SemanticFrame")
    task_plan: Optional[TaskPlan] = Field(None, description="Current or latest TaskPlan")
    execution_results: Dict[str, Any] = Field(default_factory=dict, description="Outputs mapped by task_id")
    verified_facts: List[VerifiedFact] = Field(default_factory=list, description="Extracted immutable facts")
    missing_requirements: List[str] = Field(default_factory=list, description="Prerequisite inputs or capabilities missing")
    objective_status: ObjectiveStatus = Field(default=ObjectiveStatus.NEEDS_REPLAN)
    replan_reason: ReplanReason = Field(default=ReplanReason.NONE)
    iteration: int = Field(default=0, ge=0, description="Current orchestration loop iteration")
    max_iterations: int = Field(default=2, ge=1, le=3, description="Hard cap on replanning loops (default: 2, max: 3)")
    completed_capabilities: List[str] = Field(default_factory=list, description="Capabilities successfully satisfied")
    failed_capabilities: List[str] = Field(default_factory=list, description="Capabilities that failed execution")
    final_action: Optional[str] = Field(None, description="ANSWER, NAVIGATE, REQUEST_INPUT, CALL, NOTIFY, CLARIFY")
    execution_traces: List[ExecutionTrace] = Field(default_factory=list, description="Chronological audit history")
