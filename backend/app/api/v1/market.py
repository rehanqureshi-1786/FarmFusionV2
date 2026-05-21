from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.market import MarketPriceListResponse, MarketPredictionRequest, MarketPredictionResponse
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/prices", response_model=MarketPriceListResponse)
async def get_market_prices(db: AsyncSession = Depends(get_db)):
    return await MarketService.get_market_prices(db)


@router.get("/mandis", response_model=List[str])
async def get_all_mandis(db: AsyncSession = Depends(get_db)):
    return await MarketService.get_all_mandis(db)


@router.post("/predict", response_model=MarketPredictionResponse)
async def predict_market_prices(request: MarketPredictionRequest):
    return await MarketService.predict_market_prices(request)
