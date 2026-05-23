from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db import get_db
from app.services.marketplace_service import MarketplaceService
from app.schemas.marketplace import MarketListingCreate, MarketListingResponse, MarketListingSearch

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@router.post("/listings", response_model=MarketListingResponse)
async def create_listing(
    listing: MarketListingCreate,
    user_id: int = Query(..., description="ID of the seller"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await MarketplaceService.create_listing(db, user_id, listing)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/listings", response_model=List[MarketListingResponse])
async def search_listings(
    crop: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    radius: float = Query(50.0),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await MarketplaceService.get_listings(db, crop, lat, lon, radius)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
