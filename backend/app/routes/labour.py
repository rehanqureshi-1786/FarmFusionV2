from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db import get_db
from app.services.labour_service import LabourService
from app.schemas.labour import LabourJobCreate, LabourJobResponse

router = APIRouter(prefix="/labour", tags=["labour"])

@router.post("/jobs", response_model=LabourJobResponse)
async def post_job(
    job: LabourJobCreate,
    user_id: int = Query(..., description="ID of the farmer hiring"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await LabourService.post_job(db, user_id, job)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(get_db))

@router.get("/jobs/nearby", response_model=List[LabourJobResponse])
async def get_nearby_jobs(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(25.0),
    job_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await LabourService.find_nearby_jobs(db, lat, lon, radius, job_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
