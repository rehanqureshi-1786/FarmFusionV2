"""
Disease Detection API Routes
POST /disease/detect - Upload image and detect disease
GET /disease/history - Get user's detection history
GET /disease/info/{name} - Get disease details
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.disease_service import DiseaseService
from app.services.user_service import UserService

router = APIRouter(prefix="/disease", tags=["disease"])

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/*"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/detect")
async def detect_disease(
    crop_type: Optional[str] = Query(None, description="Type of crop being checked (e.g., 'tomato', 'rice')"),
    image: UploadFile = File(..., description="Disease image to analyze (JPEG/PNG)"),
    firebase_token: Optional[str] = Query(None, description="Firebase ID token (optional for now)"),
    response_language: str = Query(
        "en",
        description="Language for description/treatment text: en, hi, mr, te, etc.",
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    POST /disease/detect

    Upload an image of a crop disease and get AI diagnosis using Gemini Vision API.

    - **crop_type**: Optional hint about the crop (e.g., "tomato", "rice", "wheat")
    - **image**: Image file (JPG/PNG, max 10MB)
    - **firebase_token**: Optional Firebase authentication token

    Returns:
    - **disease_name**: Name of detected disease or "Healthy"
    - **confidence**: Confidence score (0.0 to 1.0)
    - **severity**: Disease severity (low/medium/high/critical)
    - **description**: Detailed disease description
    - **treatment_suggestions**: List of treatment options
    - **prevention_tips**: List of prevention strategies

    Example Response:
    ```json
    {
        "success": true,
        "data": {
            "disease_name": "Early Blight",
            "confidence": 0.92,
            "severity": "high",
            "description": "Fungal disease causing concentric ring patterns...",
            "treatment_suggestions": ["Apply copper fungicide...", "Remove infected leaves..."],
            "prevention_tips": ["Rotate crops...", "Space plants properly..."]
        }
    }
    ```
    """
    try:
        # Validate image file is provided
        if not image or not image.filename:
            raise HTTPException(
                status_code=400,
                detail="No image file provided. Please upload a JPEG or PNG image."
            )

        # Validate MIME type
        content_type = (image.content_type or "").lower()
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image format. Supported formats: JPEG, PNG. Received: {image.content_type}"
            )

        # Read image data
        image_data = await image.read()

        # Validate file size
        if len(image_data) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Image file too large. Maximum size: 10MB. Received: {len(image_data) / (1024*1024):.2f}MB"
            )

        # Validate image is not empty
        if len(image_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image file is empty."
            )

        user = None
        if firebase_token:
            try:
                from app.models.user import User
                from sqlalchemy import select
                phone_cand = firebase_token.replace("user_", "")
                if phone_cand.isdigit():
                    res = await db.execute(select(User).where(User.phone == phone_cand))
                    user = res.scalar_one_or_none()
                if not user:
                    user = await UserService.get_user_by_firebase_uid(firebase_token, db)
            except Exception:
                user = None

        # Detect disease using service
        result = await DiseaseService.detect_disease(
            image_bytes=image_data,
            db=db,
            user_id=user.id if user else None,
            crop_type=crop_type,
            response_language=response_language,
            image_filename=image.filename,
        )

        return {
            "success": True,
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Disease detection failed: {str(e)}"
        )


@router.get("/history")
async def get_disease_history(
    firebase_token: Optional[str] = Query(None, description="User auth or phone token"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /disease/history

    Get user's disease detection history
    """
    try:
        if not firebase_token:
            return {"success": True, "data": []}

        user = None
        try:
            from app.models.user import User
            from sqlalchemy import select
            phone_cand = firebase_token.replace("user_", "")
            if phone_cand.isdigit():
                res = await db.execute(select(User).where(User.phone == phone_cand))
                user = res.scalar_one_or_none()
            if not user:
                user = await UserService.get_user_by_firebase_uid(firebase_token, db)
        except Exception:
            user = None

        if not user:
            return {"success": True, "data": []}

        history = await DiseaseService.get_user_disease_history(user.id, db, limit)

        return {
            "success": True,
            "data": history
        }

    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}


@router.get("/info/{disease_name}")
async def get_disease_info(disease_name: str):
    """
    GET /disease/info/{disease_name}

    Get detailed information about a specific disease

    - **disease_name**: Name of the disease
    """
    try:
        info = DiseaseService.get_disease_info(disease_name)
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get disease info: {str(e)}")


@router.get("/test")
async def test_disease_api():
    """
    GET /disease/test

    Test endpoint to verify disease API is working
    """
    return {
        "success": True,
        "message": "Disease detection API is working!",
        "endpoints": {
            "detect": "POST /disease/detect",
            "history": "GET /disease/history",
            "info": "GET /disease/info/{name}"
        }
    }
