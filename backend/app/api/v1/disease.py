"""
Disease detection API endpoints with strict validation, confidence tiers, and structured treatment retrieval.
"""
import io
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.api.deps import get_db
from app.services.disease_service import DiseaseService
from app.services.disease_knowledge_service import DiseaseKnowledgeService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/disease", tags=["disease"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/webp",
    "image/bmp",
    "application/octet-stream",
}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/detect")
async def detect_disease(
    crop_type: Optional[str] = Query(None, description="Optional target crop type (e.g. Wheat, Tomato, Cotton)"),
    image: UploadFile = File(..., description="Disease image (JPEG/PNG/WEBP)"),
    firebase_token: Optional[str] = Query(None, description="Firebase user auth token"),
    response_language: str = Query("en", description="Response language (en, hi, etc.)"),
    db: AsyncSession = Depends(get_db),
):
    """
    POST /api/v1/disease/detect
    
    Upload a leaf photograph to classify plant disease using Vision ML (EfficientNet-B3),
    retrieve structured ICAR-aligned treatment guidance (biological/cultural/chemical),
    calculate safety confidence tiers, and get Amazon affiliate product recommendations.
    """
    try:
        if not image or not image.filename:
            raise HTTPException(status_code=400, detail="No image file provided")

        content_type = (image.content_type or "").lower()
        if content_type and not any(ct in content_type for ct in ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp", "octet-stream"]):
            raise HTTPException(status_code=400, detail=f"Invalid image format: {image.content_type}. Please upload JPEG, PNG, or WEBP.")

        image_bytes = await image.read()
        if not image_bytes or len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded image file is empty (0 bytes).")

        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image exceeds maximum file size limit (10MB).")

        # Validate image integrity with PIL
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.verify()
        except Exception as img_err:
            logger.warning("corrupt_image_uploaded", error=str(img_err), filename=image.filename)
            raise HTTPException(status_code=400, detail="Corrupted or invalid image file. Please upload a valid photograph.")

        # Execute Disease Detection Pipeline
        result = await DiseaseService.detect_disease(
            image_bytes=image_bytes,
            db=db,
            firebase_uid=firebase_token,
            image_filename=image.filename,
            crop_type=crop_type,
            response_language=response_language,
        )

        if not result:
            return {
                "success": True,
                "data": {
                    "disease_name": "Could not analyze",
                    "crop_type": crop_type,
                    "confidence": 0.0,
                    "confidence_tier": "unclear",
                    "diagnosis_status": "uncertain",
                    "severity": "unknown",
                    "description": "Unable to analyze image. Please upload a clearer photograph.",
                    "treatment_suggestions": [],
                    "prevention_tips": [],
                    "ai_analyzed": False,
                    "store_recommendations": [],
                    "message": "Please upload a clear photograph of the affected leaf in daylight.",
                },
            }

        return {
            "success": True,
            "data": result,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("disease_detection_api_error", error=str(e))
        return {
            "success": False,
            "data": {
                "disease_name": "Error",
                "confidence": 0.0,
                "confidence_tier": "unclear",
                "diagnosis_status": "error",
                "severity": "unknown",
                "description": f"Processing error: {str(e)}",
                "treatment_suggestions": [],
                "prevention_tips": [],
                "ai_analyzed": False,
                "store_recommendations": [],
                "message": "An error occurred during image diagnosis. Please try again.",
            },
            "error": str(e),
        }


@router.get("/history")
async def get_disease_history(
    firebase_token: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get user's disease detection history."""
    try:
        if not firebase_token:
            return {"success": True, "data": []}

        history = await DiseaseService.get_user_disease_history(
            firebase_uid=firebase_token,
            db=db,
            limit=limit,
        )

        return {
            "success": True,
            "data": [
                {
                    "id": h.get("id", 0),
                    "crop_type": h.get("crop_type"),
                    "disease_name": h.get("disease_name"),
                    "confidence": h.get("confidence", 0.0),
                    "severity": h.get("severity", "unknown"),
                    "created_at": h.get("created_at"),
                }
                for h in history
            ],
        }
    except Exception as e:
        logger.error("disease_history_api_error", error=str(e))
        return {"success": False, "data": [], "error": str(e)}


@router.get("/info/{disease_name}")
async def get_disease_info(disease_name: str, crop_type: Optional[str] = Query(None)):
    """Get verified agronomic disease information and ICAR management guidelines by name."""
    try:
        knowledge = DiseaseKnowledgeService.lookup(disease_name, crop_type)
        return {
            "success": True,
            "data": knowledge,
        }
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
