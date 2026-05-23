"""
Market Prices API Routes
GET /market/prices - Get current prices
POST /market/predict - Predict future prices
GET /market/trends - Get price trends
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["market"])


from app.schemas.market import MarketPriceListResponse, MarketPredictionRequest, MarketPredictionResponse

@router.get("/prices", response_model=MarketPriceListResponse)
async def get_current_prices(
    state: str = Query(None, description="Filter by state"),
    district: str = Query(None, description="Filter by district"),
    commodity: str = Query(None, description="Filter by commodity"),
):
    """
    Get current market prices with flexible filtering.
    """
    try:
        prices = await MarketService.get_current_prices(
            state=state,
            district=district,
            commodity=commodity
        )
        return MarketPriceListResponse(
            data=prices,
            count=len(prices),
            region=district or state or "India"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get prices: {str(e)}")


@router.post("/predict", response_model=MarketPredictionResponse)
async def predict_prices(
    request: MarketPredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Predict market prices using AI (JSON Body supported)
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
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/trends")
async def get_price_trends(
    crop: str = Query(..., description="Crop name"),
    region: str = Query("India", description="Market region"),
    months: int = Query(6, ge=3, le=12, description="Number of months"),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /market/trends

    Get price trend analysis

    - **crop**: Crop name
    - **region**: Market region
    - **months**: Trend period (3-12 months)

    Returns historical and predicted trends
    """
    try:
        trends = await MarketService.get_price_trends(crop, region, months, db)
        return {
            "success": True,
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@router.get("/test")
async def test_market_api():
    """
    GET /market/test

    Test endpoint for market API
    """
    return {
        "success": True,
        "message": "Market API is working!",
        "endpoints": {
            "prices": "GET /market/prices",
            "predict": "POST /market/predict",
            "trends": "GET /market/trends"
        }
    }
