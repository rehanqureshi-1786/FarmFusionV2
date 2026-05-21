from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.crop import CropRecommendRequest, CropRecommendResponse
from app.services.crop_service import CropService

router = APIRouter(prefix="/crop", tags=["crop"])


@router.get("/")
async def crop_index():
    return {
        "success": True,
        "available": ["/recommend (POST)", "/history", "/test"],
        "note": "POST /api/v1/crop/recommend with JSON body matching CropRecommendRequest",
    }


@router.post("/recommend", response_model=CropRecommendResponse)
async def recommend_crop(request: CropRecommendRequest, db: AsyncSession = Depends(get_db)):
    return await CropService.get_recommendations(request, db)


@router.get("/history")
async def get_crop_history(firebase_token: Optional[str] = Query(None), limit: int = Query(10)):
    return {
        "success": True,
        "data": [],
    }


@router.get("/test")
async def test_crop_connection():
    return {"success": True}
