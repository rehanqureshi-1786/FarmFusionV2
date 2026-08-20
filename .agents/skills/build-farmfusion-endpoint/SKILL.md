---
name: build-farmfusion-endpoint
description: Workflow to build a new FastAPI REST endpoint in FarmFusion.
---

# Workflow: Build a New FarmFusion FastAPI Endpoint

## Step 1 — Clarify the endpoint

Ask the user:
- What is the HTTP method and path? (e.g. POST /disease/detect)
- Who calls it? (Kotlin app via Retrofit, or internal service only)
- What does the request body / query params look like?
- What does the response look like?
- Does it require farmer authentication?
- Does it write to the database?

Do not proceed until all of the above are confirmed.

## Step 2 — Check for existing schemas

Search `backend/app/schemas/` for any existing Pydantic model that covers this data. Reuse if possible. Create a new schema file only if the domain is genuinely new.

## Step 3 — Create or update the schema file

In `backend/app/schemas/{feature}.py`, add:

```python
from pydantic import BaseModel, ConfigDict

class {Feature}Request(BaseModel):
    # request fields with types and validation

class {Feature}Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # response fields
```

Use Python native types. Add `Field(description="...")` for all fields.

## Step 4 — Implement the router

In `backend/app/api/{feature}.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_farmer
from app.schemas.{feature} import {Feature}Request, {Feature}Response

router = APIRouter(prefix="/{feature}", tags=["{Feature}"])

@router.post("/", response_model={Feature}Response)
async def {endpoint_name}(
    request: {Feature}Request,
    db: AsyncSession = Depends(get_db),
    farmer = Depends(get_current_farmer),
):
    # call service / tool / workflow — no business logic here
    result = await {feature}_service.{method}(request, farmer, db)
    return result
```

No business logic belongs in the router. Delegate to services, tools, or workflows.

## Step 5 — Register the router in main.py

Open `backend/app/main.py`.
Add:
```python
from app.api.{feature} import router as {feature}_router
app.include_router({feature}_router, prefix="/api/v1")
```

## Step 6 — Run Alembic migration if new DB tables are needed

If the endpoint requires new tables or columns:
```bash
alembic revision --autogenerate -m "add_{feature}_table"
# Review the generated file in migrations/versions/
alembic upgrade head
```
Always review the auto-generated migration before running it.

## Step 7 — Verify in browser

Use the Antigravity browser agent to:
1. Open http://localhost:8000/docs
2. Find the new endpoint
3. Click "Try it out"
4. Send a valid test request
5. Confirm the response matches the expected schema
6. Send an invalid request and confirm validation error is returned

## Step 8 — Write tests

Create `backend/tests/test_{feature}_api.py`:

```python
import pytest
import httpx
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_{endpoint_name}_success(client: AsyncClient):
    response = await client.post("/api/v1/{feature}/", json={...})
    assert response.status_code == 200
    data = response.json()
    assert "{expected_field}" in data

@pytest.mark.asyncio
async def test_{endpoint_name}_unauthorized(client: AsyncClient):
    response = await client.post("/api/v1/{feature}/", json={...})
    # without auth header
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_{endpoint_name}_validation_error(client: AsyncClient):
    response = await client.post("/api/v1/{feature}/", json={"bad": "data"})
    assert response.status_code == 422
```

Run: `pytest backend/tests/test_{feature}_api.py -v`
All tests must pass.
