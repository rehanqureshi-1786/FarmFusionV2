"""
Crop Recommendation API Routes
POST /crop/recommend - Get crop recommendations
GET /crop/history - Get user's recommendation history
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.schemas import CropRecommendRequest, CropRecommendResponse
from app.services.crop_service import CropService
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/crop", tags=["crop"])


@router.post("/recommend", response_model=CropRecommendResponse)
async def recommend_crops(
    request: CropRecommendRequest,
    firebase_token: Optional[str] = Query(None, description="Firebase ID token (optional)"),
    db: AsyncSession = Depends(get_db)
):
    """
    POST /crop/recommend

    Get AI-powered crop recommendations based on farm conditions.

    - **request**: Farm data (location, soil_type, rainfall, temperature, farm_size)
    - **firebase_token**: Optional - if provided, saves to user's history

    Returns list of recommended crops with confidence scores, expected yield,
    market demand, profit estimates, and AI insights.
    """
    try:
        # If token provided, verify and get user ID
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

        # Get recommendations
        response = await CropService.get_recommendations(
            request=request,
            user_id=user_id,
            db=db
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/history")
async def get_recommendation_history(
    firebase_token: str = Query(..., description="Firebase ID token"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /crop/history

    Get user's crop recommendation history

    - **firebase_token**: Firebase authentication token
    - **limit**: Number of records to return (1-50, default 10)

    Returns list of previous recommendations with timestamps
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


@router.get("/history/farm/{farm_id}")
async def get_farm_recommendations(
    farm_id: int,
    firebase_token: str = Query(..., description="Firebase ID token"),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /crop/history/farm/{farm_id}

    Get recommendation history for a specific farm

    - **farm_id**: Farm ID
    - **firebase_token**: Firebase authentication token
    """
    try:
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        history = await CropService.get_farm_recommendations(farm_id, user.id, db)

        return {
            "success": True,
            "data": history
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch farm recommendations: {str(e)}"
        )


@router.get("/test")
async def test_endpoint():
    """
    GET /crop/test

    Simple test endpoint to verify your Android app can connect
    """
    return {
        "success": True,
        "message": "Crop API is working!",
        "endpoints": {
            "recommend": "POST /crop/recommend",
            "history": "GET /crop/history",
            "test": "GET /crop/test"
        },
        "ai_provider": "Groq API (Llama 3.3) or rule-based fallback",
        "timestamp": datetime.now().isoformat()
    }
