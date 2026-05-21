from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.crop import Crop, CropStatus, SoilType
from app.models.user import User
from app.schemas.crop import CropRecommendRequest, CropRecommendationResponse
from app.services.crop_service import CropService

router = APIRouter(prefix="/crops", tags=["crops"])


@router.get("/", response_model=List[CropRecommendationResponse])
async def get_crops(db: AsyncSession = Depends(get_db)):
    crops = await CropService.list_crops(db)
    return crops


@router.post("/recommendations", response_model=CropRecommendationResponse)
async def get_recommendations(request: CropRecommendRequest, db: AsyncSession = Depends(get_db)):
    return await CropService.get_recommendations(request, db)


@router.get("/{crop_id}")
async def get_crop(crop_id: int, db: AsyncSession = Depends(get_db)):
    crop = await CropService.get_crop(crop_id, db)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop


@router.get("/test")
async def test_connection():
    return {"success": True}
