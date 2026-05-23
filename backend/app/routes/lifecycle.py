from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db import get_db
from app.services.lifecycle_service import LifecycleService
from app.schemas.lifecycle import CropCycleCreate, CropCycleResponse

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])

@router.post("/start", response_model=CropCycleResponse)
async def start_crop_cycle(
    cycle: CropCycleCreate,
    user_id: int = Query(..., description="ID of the farmer"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await LifecycleService.start_cycle(db, user_id, cycle)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-crops", response_model=List[CropCycleResponse])
async def get_my_crops(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await LifecycleService.get_user_cycles(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
