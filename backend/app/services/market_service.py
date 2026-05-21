from typing import Any, List, Optional

import csv
import os
from pathlib import Path
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.market_agent import MarketAnalysisAgent
from app.db.models import MarketData, PricePrediction
from app.schemas.market import MarketPriceListResponse, MarketPredictionRequest, MarketPredictionResponse, MarketPriceResponse


class MarketService:
    @staticmethod
    async def get_market_prices(state: str | None, district: str | None, crop: str | None, db: AsyncSession) -> MarketPriceListResponse:
        result = await db.execute(select(MarketData).limit(20))
        rows = result.scalars().all()
        prices = [MarketPriceResponse(
            state=state or "India",
            district=district or "Unknown",
            market=row.mandi or "Local Mandi",
            commodity=row.commodity,
            variety="Standard",
            grade="A",
            arrival_date=row.created_at.isoformat() if row.created_at else "",
            min_price=row.price,
            max_price=row.price,
            modal_price=row.price,
            source="farmfusion-ai"
        ) for row in rows]
        return MarketPriceListResponse(data=prices, count=len(prices), region=state or "India")

    @staticmethod
    async def get_all_mandis(db: AsyncSession) -> List[str]:
        result = await db.execute(select(MarketData.mandi).distinct())
        return [row[0] for row in result.all() if row[0]]

    @staticmethod
    async def predict_market_prices(request: MarketPredictionRequest) -> MarketPredictionResponse:
        agent = MarketAnalysisAgent()
        prediction = agent.predict(request.commodity, request.region)
        return MarketPredictionResponse(commodity=request.commodity, prediction=prediction)
