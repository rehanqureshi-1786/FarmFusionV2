from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.market import (
    MarketPriceListResponse, 
    MarketPredictionRequest, 
    MarketPredictionResponse
)
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/prices", response_model=MarketPriceListResponse)
async def get_market_prices(
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    market: Optional[str] = Query(None, description="Filter by specific market/mandi"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current mandi prices from CSV dataset with AI fallback.
    """
    try:
        prices = await MarketService.get_current_prices(
            state=state,
            district=district,
            commodity=commodity,
            market=market
        )
        region = f"{district or ''} {state or 'India'}".strip()
        return MarketPriceListResponse(
            data=prices,
            count=len(prices),
            region=region
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market prices: {str(e)}")

@router.get("/mandis", response_model=List[dict])
async def get_all_mandis():
    """
    Get a list of all distinct mandis/markets available in the system.
    """
    try:
        return await MarketService.get_all_mandis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mandis list: {str(e)}")

@router.post("/predict", response_model=MarketPredictionResponse)
async def predict_market_prices(
    request: MarketPredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Predict future market prices using CSV historical context and Groq AI.
    """
    try:
        prediction = await MarketService.predict_prices(
            crop_name=request.commodity,
            region=f"{request.district or ''} {request.state}".strip(),
            current_price=request.current_price,
            prediction_months=request.prediction_months,
            db=db
        )
        return MarketPredictionResponse(**prediction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")
