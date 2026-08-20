---
name: build-farmfusion-tool
description: Workflow to build a new single-call deterministic tool in FarmFusion for the LangGraph orchestrator.
---

# Workflow: Build a New FarmFusion Tool

A "tool" in FarmFusion is a single-call, deterministic async Python function that the orchestrator can invoke. Examples: weather_tool, mandi_tool, navigation_tool, rag_search_tool, scheme_tool.

## Step 1 — Clarify the tool

Ask the user these questions before writing any code:
- What is the tool's name (snake_case)?
- What inputs does it take? (list field names and types)
- What does it return? (list field names and types)
- What external API, database, or model does it call?
- Can it fail silently, or must it surface errors to the farmer?

Do not proceed until you have answers to all of the above.

## Step 2 — Check the architecture document

Read the "2. Architectural Classification" section of `farmfusion-architecture.md`.
Confirm this feature is correctly classified as a tool (single-call, deterministic) and not a workflow or agent. If it should be a workflow, stop and tell the user.

## Step 3 — Check for existing similar tools

Search `backend/app/tools/` for any existing file that already covers this function. If one exists, extend it rather than creating a new file.

## Step 4 — Create the tool file

Create `backend/app/tools/{tool_name}_tool.py` containing:

```python
import structlog
from pydantic import BaseModel

logger = structlog.get_logger()

class {ToolName}Input(BaseModel):
    # fields here

class {ToolName}Output(BaseModel):
    # fields here
    error: str | None = None  # None means success

async def {tool_name}(input: {ToolName}Input) -> {ToolName}Output:
    """
    Purpose: [one line]
    Inputs: [describe]
    Outputs: [describe]
    Side effects: [none / logs / Redis cache writes]
    Error cases: [describe how errors are handled]
    """
    try:
        # implementation here
        logger.info("{tool_name}_called", input=input.model_dump())
        # ... 
        return {ToolName}Output(...)
    except Exception as e:
        logger.error("{tool_name}_failed", error=str(e))
        return {ToolName}Output(error=str(e))
```

Never raise unhandled exceptions. Always return the output model with error field set.

## Step 5 — Register the tool in the orchestrator router

Open `backend/app/orchestrator/nodes/tool_router.py`.
Add the import for the new tool.
Add an entry to the `TOOL_REGISTRY` dictionary:

```python
TOOL_REGISTRY = {
    "existing_intent": existing_tool,
    "{new_intent_name}": {tool_name},  # ← add this line
}
```

## Step 6 — Add the intent to the intent classifier

Open `backend/app/orchestrator/nodes/intent_classification.py`.
Add the new intent string to the Literal union in the Intent Pydantic model.
Add 4-6 example farmer phrases (2-3 in Hindi, 2-3 in English) to the examples list for this intent. Hindi examples must use Devanagari script.

## Step 7 — Create a FastAPI endpoint if this tool is directly callable

If the Kotlin app can call this tool directly (not just via the voice orchestrator):
- Create or update `backend/app/api/{feature}.py` with the endpoint
- Add the router to `backend/app/main.py`
- Add request/response schemas to `backend/app/schemas/{feature}.py`

## Step 8 — Write tests

Create `backend/tests/test_{tool_name}_tool.py` with:
- One happy-path test with mocked external API/model calls
- One test for the error case (external call fails)
- One test for edge case input (empty, None, out-of-range values)

Run: `pytest backend/tests/test_{tool_name}_tool.py -v`
All tests must pass before finishing.

## Step 9 — Update architecture document

Append one line to the Tools section of `farmfusion-architecture.md`:
`- {tool_name}: [one-line description of what it does]`
