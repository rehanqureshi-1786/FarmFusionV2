from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.marketplace import MarketListingCreate, MarketListingResponse
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.post("/listings", response_model=MarketListingResponse)
async def create_listing(request: MarketListingCreate, db: AsyncSession = Depends(get_db)):
    return await MarketplaceService.create_listing(request, db)


@router.get("/search", response_model=List[MarketListingResponse])
async def search_listings(q: str, db: AsyncSession = Depends(get_db)):
    return await MarketplaceService.search_listings(q, db)
