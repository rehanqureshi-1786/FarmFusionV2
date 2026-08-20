"""Crop management API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.crop import Crop, CropStatus
from app.models.user import User
from app.schemas.crop import CropCreate, CropResponse, CropUpdate
from app.workflows.crop_recommendation import CropRecommendationInput, run_crop_recommendation_workflow

router = APIRouter(prefix="/crop", tags=["Crops"])


@router.get("/", response_model=List[CropResponse])
async def get_crops(
    status: CropStatus = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Crop).where(Crop.owner_id == current_user.id)
    if status:
        query = query.where(Crop.status == status)
    query = query.order_by(desc(Crop.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=CropResponse, status_code=201)
async def create_crop(
    crop_data: CropCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crop = Crop(**crop_data.model_dump(), owner_id=current_user.id)
    db.add(crop)
    await db.commit()
    await db.refresh(crop)
    return crop


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(crop_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id, Crop.owner_id == current_user.id)
    )
    crop = result.scalar_one_or_none()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop


@router.post("/recommend")
async def get_recommendations(request: CropRecommendationInput):
    """
    POST /crop/recommend
    Runs XGBoost/LightGBM ML crop recommendation pipeline with RAG agronomic advice.
    """
    result = await run_crop_recommendation_workflow(request)
    return result



@router.get("/test")
async def test_connection():
    return {"status": "ok", "message": "Crop API is reachable"}
