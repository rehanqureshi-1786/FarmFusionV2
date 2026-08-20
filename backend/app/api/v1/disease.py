"""Disease detection API endpoints."""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.disease_service import DiseaseService
from app.services.store_recommendation_service import StoreRecommendationService

router = APIRouter(prefix="/disease", tags=["disease"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


@router.post("/detect")
async def detect_disease(
    crop_type: Optional[str] = Query(None, description="Type of crop"),
    image: UploadFile = File(..., description="Disease image (JPEG/PNG)"),
    firebase_token: Optional[str] = Query(None, description="Firebase token"),
    response_language: str = Query("en", description="Response language"),
    db: AsyncSession = Depends(get_db)
):
    """
    POST /disease/detect
    
    Upload an image to detect crop diseases using AI.
    Returns disease name, confidence, severity, and treatment suggestions.
    """
    try:
        if not image or not image.filename:
            raise HTTPException(status_code=400, detail="No image file provided")

        content_type = (image.content_type or "").lower()
        if not any(ct in content_type for ct in ["image/jpeg", "image/png", "image/jpg"]):
            raise HTTPException(status_code=400, detail=f"Invalid image format: {image.content_type}")

        # Read image bytes
        image_bytes = await image.read()
        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

        # Detect disease
        result = await DiseaseService.detect_disease(
            image_bytes=image_bytes,
            db=db,
            firebase_uid=None,
            image_filename=image.filename,
            crop_type=crop_type,
            response_language=response_language,
        )

        if result:
            disease_name = result.get("disease", "").strip()
            disease_norm = (disease_name or "").lower()
            # Consider AI analysis successful only when model returned a meaningful diagnosis
            ai_analyzed = (
                disease_norm not in ("unknown", "", "unable to determine", "could not analyze")
                and float(result.get("confidence", 0.0)) > 0.0
            )

            conf = float(result.get("confidence", 0.0))
            if conf >= 0.75:
                conf_tier = "high"
            elif conf >= 0.45:
                conf_tier = "medium"
            elif conf >= 0.30:
                conf_tier = "low"
            else:
                conf_tier = "unclear"

            resp = {
                "success": True,
                "data": {
                    "disease_name": disease_name or "Unknown",
                    "confidence": conf,
                    "confidence_tier": conf_tier,
                    "severity": result.get("severity", "unknown"),
                    "description": result.get("description", ""),
                    "treatment_suggestions": result.get("treatment", []),
                    "prevention_tips": result.get("prevention", []),
                    "crop_type": crop_type,
                    "timestamp": result.get("timestamp"),
                    "ai_analyzed": ai_analyzed,
                    "store_recommendations": [],
                }
            }


            # Add store recommendations when AI provided a meaningful problem (not a healthy plant)
            try:
                if ai_analyzed and disease_norm != "healthy plant":
                    stores = StoreRecommendationService.build("disease", disease_name=disease_name, crop_hint=crop_type)
                    resp["data"]["store_recommendations"] = stores.get("items", [])
            except Exception:
                # Non-fatal: if store recommendations fail, continue without them
                resp["data"]["store_recommendations"] = []

            return resp
        else:
            return {
                "success": True,
                "data": {
                    "disease_name": "Could not analyze",
                    "confidence": 0.0,
                    "severity": "unknown",
                    "description": "Unable to analyze image",
                    "treatment_suggestions": [],
                    "prevention_tips": [],
                    "crop_type": crop_type,
                    "ai_analyzed": False,
                    "store_recommendations": [],
                }
            }

    except HTTPException as e:
        raise e
    except Exception as e:
        return {
            "success": False,
            "data": {
                "disease_name": "Error",
                "confidence": 0.0,
                "severity": "unknown",
                "description": str(e),
                "treatment_suggestions": [],
                "prevention_tips": [],
                "ai_analyzed": False,
                "store_recommendations": [],
            }
        }


@router.get("/history")
async def get_disease_history(
    firebase_token: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get user's disease detection history."""
    try:
        if not firebase_token:
            return {"success": True, "data": []}

        history = await DiseaseService.get_user_disease_history(
            firebase_uid=firebase_token,
            db=db,
            limit=limit
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
                    "created_at": h.get("detected_at")
                }
                for h in history
            ]
        }
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}


@router.get("/info/{disease_name}")
async def get_disease_info(disease_name: str):
    """Get disease information by name."""
    try:
        disease_data = {
            "found": True,
            "name": disease_name,
            "description": f"Information about {disease_name}",
            "treatment": [
                "Consult local agricultural expert",
                "Apply appropriate fungicide or pesticide",
                "Practice crop rotation"
            ],
            "prevention": [
                "Maintain proper spacing",
                "Ensure good drainage",
                "Monitor plants regularly",
                "Use disease-resistant varieties"
            ],
            "severity": "medium"
        }
        return {"success": True, "data": disease_data}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}
