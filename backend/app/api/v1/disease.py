from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.disease_service import DiseaseService

router = APIRouter(prefix="/disease", tags=["disease"])


@router.post("/detect")
async def detect_disease(
    image: UploadFile = File(...),
    crop_type: Optional[str] = Query(None),
    firebase_token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # Call the service — let errors propagate so the client sees a failure
    # when the external Groq API denies access or fails.
    result = await DiseaseService.detect_disease(image.filename, db)
    disease_name = result.get("disease") if result else "unknown"
    confidence = float(result.get("confidence")) if result else 0.0

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
            "ai_analyzed": True,
        },
    }


@router.get("/history")
async def get_disease_history(firebase_token: Optional[str] = Query(None), limit: int = Query(10)):
    return {
        "success": True,
        "data": [],
    }


@router.get("/info/{disease_name}")
async def get_disease_info(disease_name: str):
    lookup = {
        "rice_blast": {
            "found": True,
            "name": "Rice Blast",
            "description": "A fungal disease that causes lesions on leaves and grains.",
            "treatment": ["Apply fungicide", "Improve drainage"],
            "prevention": ["Use disease-resistant varieties", "Avoid excess nitrogen"],
            "severity": "moderate",
            "message": "Monitor crops and treat early to reduce yield loss.",
        },
        "late_blight": {
            "found": True,
            "name": "Late Blight",
            "description": "A destructive disease in potato and tomato crops.",
            "treatment": ["Remove infected plants", "Use copper-based sprays"],
            "prevention": ["Plant resistant varieties", "Ensure good airflow"],
            "severity": "high",
            "message": "Start treatment right away if symptoms are visible.",
        },
    }
    info = lookup.get(disease_name.lower(), {
        "found": False,
        "name": disease_name,
        "description": "No specific information found for this disease.",
        "treatment": [],
        "prevention": [],
        "severity": "unknown",
        "message": "Try another disease name or contact support.",
    })
    return {"success": True, "data": info}
