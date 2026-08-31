from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.market import (
    MarketPriceListResponse, 
    MarketPredictionRequest, 
    MarketPredictionResponse,
    BestMandiResponse,
    MandiComparisonResponse,
    MandiAdvisoryResponse,
    ForecastExplanationResponse,
    PriceAlertCreate,
    PriceAlertResponse,
    PriceAlertListResponse
)
from app.services.market_service import MarketService
from app.services.mandi_intelligence import MandiIntelligenceService
from app.workflows.market_forecasting import MandiForecastRequest, run_mandi_forecasting_pipeline

router = APIRouter(prefix="/market", tags=["Market & Mandi Intelligence"])


@router.get("/prices", response_model=MarketPriceListResponse)
async def get_market_prices(
    state: Optional[str] = Query(None, description="Filter by state"),
    district: Optional[str] = Query(None, description="Filter by district"),
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    crop: Optional[str] = Query(None, description="Filter by crop (alias)"),
    market: Optional[str] = Query(None, description="Filter by specific market/mandi"),
    db: AsyncSession = Depends(get_db)
):
    """Get current mandi prices from CSV dataset with live fallback."""
    try:
        target_commodity = commodity or crop
        prices = await MarketService.get_current_prices(
            state=state,
            district=district,
            commodity=target_commodity,
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
    """Get a list of all distinct mandis/markets available in the system."""
    try:
        return await MarketService.get_all_mandis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mandis list: {str(e)}")


@router.get("/commodities", response_model=List[str])
async def get_all_commodities():
    """Get a list of all unique supported crops and commodities from Agmarknet dataset."""
    try:
        return await MarketService.get_all_commodities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching commodities list: {str(e)}")


@router.get("/best-nearby", response_model=BestMandiResponse, summary="Feature 1: Best Practical & Nearby Mandis")
@router.get("/best-practical", response_model=BestMandiResponse, summary="Feature 1: Best Practical Mandi Ranking")
async def get_best_nearby_mandis(
    commodity: str = Query(..., description="Commodity or crop name e.g. Wheat, Groundnut, Mustard"),
    latitude: Optional[float] = Query(None, description="GPS Latitude"),
    longitude: Optional[float] = Query(None, description="GPS Longitude"),
    district: Optional[str] = Query(None, description="District name"),
    state: Optional[str] = Query(None, description="State name"),
    max_distance_km: float = Query(300.0, description="Max geodesic search radius in KM"),
    limit: int = Query(5, ge=1, le=20, description="Max top mandis to return")
):
    """
    Ranks nearby mandis by practical scoring (combining modal price, distance, and freshness),
    while preserving and distinguishing the highest recorded price.
    """
    try:
        return await MandiIntelligenceService.get_best_nearby_mandis(
            commodity=commodity,
            latitude=latitude,
            longitude=longitude,
            district=district,
            state=state,
            max_distance_km=max_distance_km,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding best practical mandis: {str(e)}")


@router.get("/compare", response_model=MandiComparisonResponse, summary="Feature 2: Mandi Comparison")
async def compare_mandis(
    commodity: str = Query(..., description="Crop or commodity to compare"),
    market_a: str = Query(..., description="First mandi / district name e.g. Udaipur"),
    market_b: str = Query(..., description="Second mandi / district name e.g. Jaipur")
):
    """
    Calculates exact price difference and percentage spread between two markets.
    """
    try:
        return await MandiIntelligenceService.compare_mandis(
            commodity=commodity,
            market_a=market_a,
            market_b=market_b
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing mandis: {str(e)}")


@router.get("/advisory", response_model=MandiAdvisoryResponse, summary="Feature 4 & 6: Sell-Now vs Wait Advisory")
async def get_sell_wait_advisory(
    commodity: str = Query(..., description="Crop or commodity name"),
    market: str = Query("Jaipur Mandi", description="Target market location"),
    days: int = Query(7, ge=1, le=30, description="Forecast horizon in days")
):
    """
    Deterministic decision support (FAVORABLE_TO_SELL, POSSIBLE_UPSIDE, STABLE, INSUFFICIENT_EVIDENCE).
    """
    try:
        return await MandiIntelligenceService.get_sell_wait_advisory(
            commodity=commodity,
            market=market,
            days=days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating mandi advisory: {str(e)}")


@router.get("/forecast-explanation", response_model=ForecastExplanationResponse, summary="Feature 5: Forecast Explanation")
async def get_forecast_explanation(
    commodity: str = Query(..., description="Crop or commodity name"),
    market: str = Query("Jaipur Mandi", description="Target market location")
):
    """
    Returns genuine data & time-series signals explaining the price forecast direction.
    """
    try:
        return await MandiIntelligenceService.get_forecast_explanation(
            commodity=commodity,
            market=market
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining forecast: {str(e)}")


@router.post("/alerts", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED, summary="Feature 3: Create Price Opportunity Alert")
async def create_price_alert(
    payload: PriceAlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Stores user-defined price trigger alert condition.
    """
    try:
        return await MandiIntelligenceService.create_price_alert(db=db, payload=payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating price alert: {str(e)}")


@router.get("/alerts", response_model=PriceAlertListResponse, summary="Feature 3: Get Active Price Alerts")
async def get_price_alerts(
    user_id: str = Query("default_user", description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists active price alerts for user.
    """
    try:
        return await MandiIntelligenceService.get_user_alerts(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price alerts: {str(e)}")


@router.post("/predict", response_model=MarketPredictionResponse)
async def predict_market_prices(
    request: MarketPredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Predict future market prices using CSV historical context and ML/AI."""
    try:
        return await MarketService.predict_prices(
            crop_name=request.commodity,
            region=f"{request.district or ''} {request.state}".strip(),
            current_price=request.current_price,
            prediction_months=request.prediction_months,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prediction: {str(e)}")


@router.get("/forecast")
async def get_mandi_price_forecast(
    commodity: str = Query(..., description="Crop or commodity name e.g. Wheat"),
    mandi: str = Query("Jaipur Mandi", description="Target market/mandi location"),
    days: int = Query(7, ge=1, le=30, description="Forecast horizon in days")
):
    """Prophet + LightGBM ML ensemble model price forecast with 95% confidence intervals."""
    req = MandiForecastRequest(commodity=commodity, mandi=mandi, days=days)
    return await run_mandi_forecasting_pipeline(req)
