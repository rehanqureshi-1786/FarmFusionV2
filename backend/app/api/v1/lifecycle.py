from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.lifecycle import CropCycleCreate, CropCycleResponse
from app.services.lifecycle_service import LifecycleService

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])


@router.post("/crop-cycles", response_model=CropCycleResponse)
async def start_crop_cycle(request: CropCycleCreate, db: AsyncSession = Depends(get_db)):
    return await LifecycleService.start_crop_cycle(request, db)


@router.get("/crop-cycles", response_model=List[CropCycleResponse])
async def get_my_crops(db: AsyncSession = Depends(get_db)):
    return await LifecycleService.get_my_crops(db)
