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
    async def get_market_prices(db: AsyncSession) -> MarketPriceListResponse:
        result = await db.execute(select(MarketData).limit(20))
        prices = [MarketPriceResponse(commodity=row.commodity, price=row.price, mandi=row.mandi, created_at=row.created_at) for row in result.scalars().all()]
        return MarketPriceListResponse(prices=prices)

    @staticmethod
    async def get_all_mandis(db: AsyncSession) -> List[str]:
        result = await db.execute(select(MarketData.mandi).distinct())
        return [row[0] for row in result.all() if row[0]]

    @staticmethod
    async def predict_market_prices(request: MarketPredictionRequest) -> MarketPredictionResponse:
        agent = MarketAnalysisAgent()
        prediction = agent.predict(request.commodity, request.region)
        return MarketPredictionResponse(commodity=request.commodity, prediction=prediction)
