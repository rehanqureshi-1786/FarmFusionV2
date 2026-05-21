from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.labour import LabourJobCreate, LabourJobResponse
from app.services.labour_service import LabourService

router = APIRouter(prefix="/labour", tags=["labour"])


@router.post("/jobs", response_model=LabourJobResponse)
async def post_job(job: LabourJobCreate, db: AsyncSession = Depends(get_db)):
    return await LabourService.post_job(job, db)


@router.get("/jobs", response_model=List[LabourJobResponse])
async def get_nearby_jobs(location: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    return await LabourService.get_nearby_jobs(location, db)
