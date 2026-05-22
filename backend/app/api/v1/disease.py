import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.disease_service import DiseaseService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/disease", tags=["disease"])


@router.post("/detect")
async def detect_disease(
    image: UploadFile = File(...),
    crop_type: Optional[str] = Query(None),
    firebase_token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    image_ref = image.filename or "uploaded_image.jpg"
    ai_analyzed = True

    try:
        result = await DiseaseService.detect_disease(image_ref, db)
    except Exception as exc:
        logger.exception("Disease detection failed for %s", image_ref)
        result = {"disease": "unknown", "confidence": 0.0}
        ai_analyzed = False

    disease_name = result.get("disease") if result else "unknown"
    try:
        confidence = float(result.get("confidence")) if result else 0.0
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    if disease_name == "unknown" and confidence == 0.0:
        ai_analyzed = False

    return {
        "success": True,
        "data": {
            "disease_name": disease_name,
            "confidence": confidence,
            "severity": "low",
            "description": f"Detected {disease_name} in the provided image.",
            "treatment_suggestions": [
                "Ensure proper irrigation and crop hygiene.",
                "Apply a suitable fungicide or pesticide as needed.",
            ],
            "prevention_tips": [
                "Use clean seeds and rotate crops.",
                "Monitor fields regularly for early signs of disease.",
            ],
            "crop_type": crop_type,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "farmfusion-ai",
            "is_plant_image": True,
            "can_analyze": True,
            "invalid_image_reason": None,
            "ai_analyzed": ai_analyzed,
        },
    }
