"""
Animal detection API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.animal import AnimalDetection
from app.models.user import User

router = APIRouter(prefix="/animals", tags=["Animal Detection"])


@router.get("/detections")
async def get_detections(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get animal detections for current user."""
    result = await db.execute(
        select(AnimalDetection)
        .where(AnimalDetection.user_id == current_user.id)
        .order_by(desc(AnimalDetection.created_at))
        .offset(skip)
        .limit(limit)
    )
    
    return {
        "items": result.scalars().all(),
        "page": skip // limit + 1,
        "limit": limit
    }


@router.post("/detect", status_code=status.HTTP_201_CREATED)
async def detect_animal(
    image: UploadFile = File(...),
    latitude: float = None,
    longitude: float = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and analyze image for animal detection."""
    # Mock AI detection
    detected_animals = [
        {"type": "wild_boar", "confidence": 0.94, "threat_level": "high"},
        {"type": "nilgai", "confidence": 0.87, "threat_level": "medium"}
    ]
    
    detections = []
    for animal in detected_animals:
        detection = AnimalDetection(
            user_id=current_user.id,
            animal_type=animal["type"],
            confidence_score=animal["confidence"],
            image_url=f"/uploads/{image.filename}",
            latitude=latitude,
            longitude=longitude,
            threat_level=animal["threat_level"]
        )
        db.add(detection)
        detections.append(detection)
    
    await db.commit()
    for d in detections:
        await db.refresh(d)
    
    return {
        "message": "Detection completed",
        "detections": detected_animals,
        "saved_detections": detections
    }


@router.get("/detections/{detection_id}")
async def get_detection(
    detection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific detection."""
    result = await db.execute(
        select(AnimalDetection).where(
            AnimalDetection.id == detection_id,
            AnimalDetection.user_id == current_user.id
        )
    )
    detection = result.scalar_one_or_none()
    
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    
    return detection
