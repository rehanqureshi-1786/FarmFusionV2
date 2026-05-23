"""
Mandi prices API endpoints.
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.api.deps import get_db, get_current_user
from app.models.mandi import MandiPrice
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/mandi", tags=["Mandi Prices"])


@router.get("/prices")
async def get_mandi_prices(
    commodity: str = Query(None, description="Filter by commodity"),
    state: str = Query(None, description="Filter by state"),
    district: str = Query(None, description="Filter by district"),
    market: str = Query(None, description="Filter by market"),
    date_from: datetime = Query(None, description="Start date"),
    date_to: datetime = Query(None, description="End date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get mandi prices with filters."""
    query = select(MandiPrice)
    
    if commodity:
        query = query.where(MandiPrice.commodity.ilike(f"%{commodity}%"))
    if state:
        query = query.where(MandiPrice.state.ilike(f"%{state}%"))
    if district:
        query = query.where(MandiPrice.district.ilike(f"%{district}%"))
    if market:
        query = query.where(MandiPrice.market.ilike(f"%{market}%"))
    if date_from:
        query = query.where(MandiPrice.price_date >= date_from)
    if date_to:
        query = query.where(MandiPrice.price_date <= date_to)
    
    query = query.order_by(desc(MandiPrice.price_date)).offset(skip).limit(limit)
    result = await db.execute(query)
    prices = result.scalars().all()
    
    return {
        "items": prices,
        "total": len(prices),
        "page": skip // limit + 1,
        "limit": limit
    }


@router.get("/prices/trend/{commodity}")
async def get_price_trend(
    commodity: str,
    days: int = Query(30, ge=1, le=365),
    state: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price trend for a commodity."""
    from_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(MandiPrice).where(
        and_(
            MandiPrice.commodity.ilike(f"%{commodity}%"),
            MandiPrice.price_date >= from_date
        )
    ).order_by(MandiPrice.price_date)
    
    if state:
        query = query.where(MandiPrice.state.ilike(f"%{state}%"))
    
    result = await db.execute(query)
    prices = result.scalars().all()
    
    return {
        "commodity": commodity,
        "days": days,
        "data": [
            {
                "date": p.price_date,
                "min_price": p.min_price,
                "max_price": p.max_price,
                "modal_price": p.modal_price,
                "market": p.market,
                "district": p.district
            }
            for p in prices
        ]
    }


@router.get("/commodities")
async def get_commodities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of available commodities."""
    result = await db.execute(
        select(MandiPrice.commodity)
        .distinct()
        .order_by(MandiPrice.commodity)
    )
    commodities = [r[0] for r in result.all()]
    
    return {"commodities": commodities}


@router.get("/markets")
async def get_markets(
    state: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of markets."""
    query = select(MandiPrice.market, MandiPrice.state).distinct()
    
    if state:
        query = query.where(MandiPrice.state.ilike(f"%{state}%"))
    
    query = query.order_by(MandiPrice.state, MandiPrice.market)
    result = await db.execute(query)
    markets = [{"market": r[0], "state": r[1]} for r in result.all()]
    
    return {"markets": markets}
