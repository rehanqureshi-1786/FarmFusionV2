from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db import get_db
from app.services.marketplace_service import MarketplaceService
from app.schemas.marketplace import MarketListingCreate, MarketListingResponse

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@router.post("/listings", response_model=MarketListingResponse)
async def create_listing(
    listing: MarketListingCreate,
    user_id: Optional[int] = Query(None, description="ID of the seller"),
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
    radius: float = Query(5000.0),
    user_id: Optional[int] = Query(None, description="Filter listings by seller"),
    active_only: bool = Query(False, description="If true, return only active listings"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await MarketplaceService.get_listings(db, crop, lat, lon, radius, user_id, active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/listings/{listing_id}")
async def delete_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        success = await MarketplaceService.delete_listing(db, listing_id)
        if not success:
            raise HTTPException(status_code=404, detail="Listing not found")
        return {"status": "success", "message": "Listing deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/listings/{listing_id}/status", response_model=MarketListingResponse)
async def update_listing_status(
    listing_id: int,
    is_active: bool = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        updated = await MarketplaceService.toggle_listing_status(db, listing_id, is_active)
        if not updated:
            raise HTTPException(status_code=404, detail="Listing not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
