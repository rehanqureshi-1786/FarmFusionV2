from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.market import MarketPriceListResponse, MarketPredictionRequest, MarketPredictionResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/prices", response_model=MarketPriceListResponse)
async def get_market_prices(
    state: str | None = Query(None),
    district: str | None = Query(None),
    crop: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await MarketService.get_market_prices(state, district, crop, db)


@router.get("/mandis", response_model=List[str])
async def get_all_mandis(db: AsyncSession = Depends(get_db)):
    return await MarketService.get_all_mandis(db)


@router.post("/predict", response_model=MarketPredictionResponse)
async def predict_market_prices(request: MarketPredictionRequest):
    return await MarketService.predict_market_prices(request)


@router.get("/trends")
async def get_price_trends(
    crop: str = Query(...),
    region: str = Query("India"),
    months: int = Query(6),
    db: AsyncSession = Depends(get_db),
):
    result = await MarketService.get_price_trends(crop, region, months, db)
    return {"success": True, "data": result}
