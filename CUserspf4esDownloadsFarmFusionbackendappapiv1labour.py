"""
Labour services API endpoints.
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_

from app.api.deps import get_db, get_current_user
from app.models.labour import LabourRequest, LabourStatus, LabourType
from app.models.user import User

router = APIRouter(prefix="/labour", tags=["Labour Services"])


@router.get("/requests")
async def get_labour_requests(
    status: LabourStatus = None,
    labour_type: LabourType = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get labour requests."""
    query = select(LabourRequest).where(
        or_(
            LabourRequest.requester_id == current_user.id,
            LabourRequest.assigned_to == current_user.id
        )
    )
    
    if status:
        query = query.where(LabourRequest.status == status)
    if labour_type:
        query = query.where(LabourRequest.labour_type == labour_type)
    
    query = query.order_by(desc(LabourRequest.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    
    return {
        "items": result.scalars().all(),
        "page": skip // limit + 1,
        "limit": limit
    }


@router.post("/requests", status_code=status.HTTP_201_CREATED)
async def create_labour_request(
    request_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new labour request."""
    labour_request = LabourRequest(
        requester_id=current_user.id,
        **request_data
    )
    db.add(labour_request)
    await db.commit()
    await db.refresh(labour_request)
    
    return labour_request


@router.get("/requests/{request_id}")
async def get_labour_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific labour request."""
    result = await db.execute(
        select(LabourRequest).where(LabourRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Labour request not found")
    
    return request


@router.patch("/requests/{request_id}")
async def update_labour_request(
    request_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a labour request."""
    result = await db.execute(
        select(LabourRequest).where(
            LabourRequest.id == request_id,
            LabourRequest.requester_id == current_user.id
        )
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Labour request not found")
    
    for key, value in update_data.items():
        setattr(request, key, value)
    
    await db.commit()
    await db.refresh(request)
    return request


@router.post("/requests/{request_id}/apply")
async def apply_for_labour(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply for a labour job."""
    result = await db.execute(
        select(LabourRequest).where(LabourRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Labour request not found")
    
    if request.status != LabourStatus.OPEN:
        raise HTTPException(status_code=400, detail="Job is no longer open")
    
    request.assigned_to = current_user.id
    request.status = LabourStatus.ASSIGNED
    
    await db.commit()
    await db.refresh(request)
    return request
