"""
Crop management API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.crop import Crop, SoilReport, CropStatus
from app.models.user import User
from app.schemas.crop import (
    CropCreate, CropResponse, CropUpdate,
    SoilReportCreate, SoilReportResponse,
    CropRecommendationRequest, CropRecommendationResponse
)

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.get("/", response_model=List[CropResponse])
async def get_crops(
    status: CropStatus = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all crops for current user."""
    query = select(Crop).where(Crop.owner_id == current_user.id)
    
    if status:
        query = query.where(Crop.status == status)
    
    query = query.order_by(desc(Crop.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    crops = result.scalars().all()
    
    return crops


@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(
    crop_data: CropCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new crop."""
    crop = Crop(
        **crop_data.model_dump(),
        owner_id=current_user.id
    )
    db.add(crop)
    await db.commit()
    await db.refresh(crop)
    return crop


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(
    crop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific crop by ID."""
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id, Crop.owner_id == current_user.id)
    )
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found"
        )
    return crop


@router.patch("/{crop_id}", response_model=CropResponse)
async def update_crop(
    crop_id: int,
    crop_data: CropUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a crop."""
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id, Crop.owner_id == current_user.id)
    )
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found"
        )
    
    update_data = crop_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(crop, field, value)
    
    await db.commit()
    await db.refresh(crop)
    return crop


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop(
    crop_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a crop."""
    result = await db.execute(
        select(Crop).where(Crop.id == crop_id, Crop.owner_id == current_user.id)
    )
    crop = result.scalar_one_or_none()
    
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found"
        )
    
    await db.delete(crop)
    await db.commit()
    return None


@router.post("/soil-reports", response_model=SoilReportResponse, status_code=status.HTTP_201_CREATED)
async def create_soil_report(
    report_data: SoilReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new soil report."""
    report = SoilReport(
        **report_data.model_dump(),
        user_id=current_user.id
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/soil-reports", response_model=List[SoilReportResponse])
async def get_soil_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all soil reports for current user."""
    result = await db.execute(
        select(SoilReport)
        .where(SoilReport.user_id == current_user.id)
        .order_by(desc(SoilReport.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/recommend", response_model=CropRecommendationResponse)
async def get_crop_recommendations(
    request: CropRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """Get crop recommendations based on soil and location."""
    # Mock AI recommendation logic
    recommendations = [
        {
            "crop_name": "Wheat",
            "confidence": 0.92,
            "description": "Best suited for your soil type and season",
            "expected_yield": "45-50 quintals per hectare",
            "sowing_period": "November-December",
            "harvesting_period": "March-April",
            "water_requirement": "Moderate (400-500mm)",
            "suitable_varieties": ["HD-2967", "DBW-187", "PBW-175"]
        },
        {
            "crop_name": "Mustard",
            "confidence": 0.85,
            "description": "Good alternative for rotation",
            "expected_yield": "15-18 quintals per hectare",
            "sowing_period": "October-November",
            "harvesting_period": "February-March",
            "water_requirement": "Low (250-300mm)",
            "suitable_varieties": ["Varuna", "RH-749", "CS-52"]
        }
    ]
    
    return CropRecommendationResponse(
        recommendations=recommendations,
        based_on=request.soil_type,
        soil_health_score=7.5
    )
