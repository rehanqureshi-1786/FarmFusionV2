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


from app.models.schemas import CropRecommendRequest, CropRecommendResponse
from app.services.crop_service import CropService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from datetime import datetime
from typing import Optional


@router.post("/recommend", response_model=CropRecommendResponse)
async def get_recommendations(
    request: CropRecommendRequest,
    firebase_token: Optional[str] = Query(None, description="Firebase ID token (optional)"),
    db: AsyncSession = Depends(get_db)
) -> CropRecommendResponse:
    """
    POST /api/v1/crop/recommend

    Get AI/ML-powered crop recommendations using Local Crop Agent V2.
    """
    try:
        user_id = None
        if firebase_token:
            user_data = await AuthService.verify_token(firebase_token)
            if user_data:
                user = await UserService.get_or_create_user(
                    firebase_uid=user_data["uid"],
                    phone_number=user_data.get("phone_number"),
                    db=db
                )
                user_id = user.id

        response = await CropService.get_recommendations(
            request=request,
            user_id=user_id,
            db=db
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate crop recommendations: {str(e)}"
        )


@router.get("/history")
async def get_recommendation_history(
    firebase_token: str = Query(..., description="Firebase ID token"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /api/v1/crop/history
    """
    try:
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            return {"success": True, "data": []}

        history = await CropService.get_user_history(user.id, db, limit)
        return {
            "success": True,
            "data": history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch history: {str(e)}"
        )


@router.get("/test")
async def test_connection():
    return {
        "success": True,
        "message": "Crop API is working!",
        "endpoints": {
            "recommend": "POST /api/v1/crop/recommend",
            "no_soil_report": "POST /api/v1/crop-recommendation/no-soil-report",
            "history": "GET /api/v1/crop/history",
            "test": "GET /api/v1/crop/test"
        },
        "ai_provider": "FarmFusion Local Crop Agent V2 (ICAR/CRIDA + XGBoost)",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/{crop_id:int}", response_model=CropResponse)
async def get_crop(crop_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id, Crop.owner_id == current_user.id)
    )
    crop = result.scalar_one_or_none()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop

