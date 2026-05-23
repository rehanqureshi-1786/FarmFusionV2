from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db import get_db
from app.services.store_service import StoreService
from app.services.store_recommendation_service import StoreRecommendationService
from app.schemas.store import (
    StoreProductResponse,
    StoreOrderCreate,
    StoreOrderResponse,
    StoreRecommendationsResponse,
)

router = APIRouter(prefix="/store", tags=["store"])

@router.get("/recommendations", response_model=StoreRecommendationsResponse)
async def get_store_recommendations(
    source: str = Query("browse", description="browse | crop | disease"),
    crop: Optional[str] = Query(None),
    disease_name: Optional[str] = Query(None),
    crop_hint: Optional[str] = Query(None),
):
    """Curated items with Amazon India search URLs — personalized when source=crop|disease."""
    s = (source or "browse").lower().strip()
    if s not in ("browse", "crop", "disease"):
        s = "browse"
    raw = StoreRecommendationService.build(s, crop=crop, disease_name=disease_name, crop_hint=crop_hint)
    return StoreRecommendationsResponse(**raw)


@router.get("/products", response_model=List[StoreProductResponse])
async def get_products(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await StoreService.get_products(db, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed")
async def seed_store(db: AsyncSession = Depends(get_db)):
    """Seed the store with initial stock"""
    try:
        await StoreService.populate_initial_stock(db)
        return {"success": True, "message": "Initial stock added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
