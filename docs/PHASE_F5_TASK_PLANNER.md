# Phase F5 — Task Planner & Dependency-Aware Multi-Tool Orchestration

## 1. Executive Summary

Phase F5 transitions FarmFusion from static, single-turn tool dispatching to **dependency-aware, multi-tool orchestration** on top of LangGraph. Built strictly upon the Canonical `SemanticFrame` (Phase F2/F3) and normalized `ToolContract` registry (Phase F4), the Task Planner decomposes complex farmer requests into Directed Acyclic Graphs (DAGs), validates required-input gates, batches independent tasks for concurrent execution, resolves inter-tool data dependencies, and executes workflows via a strictly controlled execution layer.

### What Phase F5 Delivers
- **TaskPlan Pydantic Schema**: Strongly typed models representing plans, individual planned tasks, input bindings, dependencies, and execution batches.
- **DAG Builder & Topological Sorter**: Kahn's algorithm-based cycle detection and stage batching separating parallel tasks from dependent serial tasks.
- **Strict Required-Input Gates**: Deterministic halting when required inputs are absent (e.g. leaf photos for crop disease diagnosis or coordinates for weather/disaster queries) without hallucinating parameters or calling models prematurely.
- **Controlled Async Execution Engine**: Executes registered tools in topologically sorted batches with `asyncio.gather` for independent tasks and dynamic runtime result piping into downstream tool parameters.
- **Fault-Tolerant Isolation**: Differentiates blocking prerequisites from non-blocking ancillary tasks, safely skipping downstream dependents if a blocking requirement fails.
- **LangGraph Integration**: Integrates `planner` and `plan_executor` nodes directly into the core `StateGraph` pipeline between semantic classification and final response synthesis.

---

## 2. Core Schemas & Data Models

All planner data models are located in [`backend/app/orchestrator/planner/schemas.py`](file:///home/rdj/FarmFusionFinal/backend/app/orchestrator/planner/schemas.py).

### Key Models

```python
class TaskDependency(BaseModel):
    task_id: str
    upstream_task_id: str
    required_field: Optional[str] = None
    target_param: Optional[str] = None

class PlannedTask(BaseModel):
    task_id: str
    capability: CapabilityType
    tool_name: str
    depends_on: List[str] = Field(default_factory=list)
    static_inputs: Dict[str, Any] = Field(default_factory=dict)
    dynamic_mappings: Dict[str, str] = Field(default_factory=dict)
    is_blocking: bool = True
    status: TaskStatus = TaskStatus.PENDING
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TaskPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    objective: str
    action_type: ActionType  # EXECUTE_TOOL, NAVIGATE, REQUEST_INPUT, CLARIFY, DIRECT_REPLY
    tasks: List[PlannedTask] = Field(default_factory=list)
    execution_batches: List[List[str]] = Field(default_factory=list)
    status: PlanStatus = PlanStatus.PENDING
    required_input: Optional[RequiredInput] = None
    unresolved_inputs: List[str] = Field(default_factory=list)
    navigation_destination: Optional[str] = None
    navigation_route: Optional[str] = None
    clarification_question: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
```

---

## 3. Dependency Model & Execution Batches

The planner analyzes dependencies among required capabilities to construct execution batches:

```
Batch 0 (Parallel Execution):
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│ mandi_current_price_tool │   │ mandi_comparison_tool   │   │ mandi_forecast_tool     │
└────────────┬────────────┘   └────────────┬────────────┘   └────────────┬────────────┘
             │                             │                             │
             └──────────────────────┬──────┴─────────────────────────────┘
                                    ↓
Batch 1 (Dependent Sequential Execution):
                      ┌─────────────────────────┐
                      │ mandi_decision_tool     │
                      └─────────────────────────┘
```

### Stage Grouping via Topological Sorter
1. In-degree of each task is calculated based on `depends_on`.
2. All tasks with in-degree 0 form Batch 0 and execute concurrently via `asyncio.gather`.
3. Upon batch completion, outgoing edges are decremented.
4. Next set of zero in-degree tasks form Batch 1, and so on.
5. Cyclic dependencies raise `DAGCycleError` before any tool is executed.

---

## 4. Required-Input Gating

The planner enforces strict safety boundaries before task construction:

| Prerequisite | Condition | Planner Action | Execution |
|---|---|---|---|
| **Leaf Photo** | `CapabilityType.DISEASE_DETECTION` requested without image | `ActionType.NAVIGATE` to destination `DISEASE_SCAN` (`crop_disease`) | **Zero ML models called**. App guided to camera. |
| **Location Coordinates** | `CapabilityType.WEATHER` requested with no coordinates or district | `ActionType.REQUEST_INPUT` for `FARM_LOCATION` | **Zero API calls**. Farmer prompted for village/district. |
| **Ambiguous Intent** | Intent classification confidence < 0.60 | `ActionType.CLARIFY` | Asks targeted clarifying question. |

---

## 5. Dynamic Result Propagation

Downstream tasks frequently require parameters produced by earlier tasks. The planner registers these bindings in `dynamic_mappings`:

### Example: Disease Detection → Treatment RAG
```json
{
  "task_id": "rag_1",
  "capability": "RAG_KNOWLEDGE",
  "tool_name": "rag_knowledge_tool",
  "depends_on": ["disease_1"],
  "dynamic_mappings": {
    "query": "disease_1.disease_name"
  }
}
```
During execution, `executor.py` intercepts `disease_1.disease_name` from the completed output and dynamically injects it into `rag_1.static_inputs["query"]` before calling `rag_knowledge_tool`.

### Example: Mandi Forecast → Mandi Decision
Forecast trajectory and prices are passed directly into the decision ensemble model.

---

## 6. Failure Handling: Blocking vs Non-Blocking

1. **Blocking Failure** (`is_blocking=True`):
   - Example: Disease detection inference fails or weather API returns unrecoverable error for irrigation.
   - Action: Dependent tasks are marked `TaskStatus.SKIPPED` with reason `Prerequisite dependency failed`. Execution halts safely without calling downstream tools on corrupt/empty data.
2. **Non-Blocking Failure** (`is_blocking=False`):
   - Example: Weather context lookup fails during Mandi price consultation.
   - Action: Mandi pricing and forecasting continue normally.

---

## 7. LangGraph Pipeline Integration

The orchestrator `StateGraph` in `app/orchestrator/graph.py` integrates the planner:

```
[START]
   ↓
intent_classification (SemanticFrame extraction & confidence check)
   ↓
[route_after_intent] ──(confidence < 0.6)──> response_synthesizer ──> [END]
   ↓ (confident)
planner (DAG generation & input gating)
   ↓
[route_after_planner] ──(NAVIGATE / CLARIFY / REQUEST_INPUT)──> response_synthesizer ──> [END]
   ↓ (EXECUTE_TOOL)
plan_executor (Controlled async execution & dynamic piping)
   ↓
response_synthesizer (Natural language formatting in farmer's language)
   ↓
[END]
```
