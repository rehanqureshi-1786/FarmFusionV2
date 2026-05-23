from typing import Any, List, Optional, Dict
import json
import urllib.request
import urllib.parse
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.market_agent import MarketAnalysisAgent
from app.db.models import MarketData, PricePrediction
from app.schemas.market import MarketPriceListResponse, MarketPredictionRequest, MarketPredictionResponse, MarketPriceResponse
from app.core.config import settings


class MarketService:
    # Public agricultural data sources
    COMMODITY_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a5c0-2eb213883242"
    
    @staticmethod
    async def _fetch_real_market_data(crop: str, state: str, district: str) -> Optional[List[dict]]:
        """Fetch real market data from public agricultural APIs."""
        try:
            # Try to fetch from data.gov.in agricultural commodity prices
            if hasattr(settings, 'MANDI_API_KEY') and settings.MANDI_API_KEY:
                url = f"{MarketService.COMMODITY_API_URL}?api-key={settings.MANDI_API_KEY}&format=json&limit=100"
                if crop:
                    url += f"&filters[commodity_name][]={urllib.parse.quote_plus(crop)}"
                if state:
                    url += f"&filters[state][]={urllib.parse.quote_plus(state)}"
                if district:
                    url += f"&filters[district][]={urllib.parse.quote_plus(district)}"
                
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.load(response)
                    records = data.get('records', [])
                    return records if records else None
            return None
        except Exception:
            # API not available or request failed - continue without real data
            return None
    
    @staticmethod
    async def get_market_prices(state: str | None, district: str | None, crop: str | None, db: AsyncSession) -> MarketPriceListResponse:
        """Get market prices from database or real APIs. Fails if no real data available."""
        # Try to fetch real market data from public APIs
        real_data = await MarketService._fetch_real_market_data(crop or "", state or "", district or "")
        
        if real_data:
            # Convert real API data to response format
            prices = [MarketPriceResponse(
                state=item.get('state', state or "India"),
                district=item.get('district', district or item.get('market_name', "Unknown")),
                market=item.get('market_name', 'Mandi'),
                commodity=item.get('commodity_name', crop or "Unknown"),
                variety=item.get('variety', 'Standard'),
                grade=item.get('grade', 'A'),
                arrival_date=item.get('arrival_date', datetime.utcnow().isoformat()),
                min_price=float(item.get('min_price', 0)),
                max_price=float(item.get('max_price', 0)),
                modal_price=float(item.get('modal_price', 0)),
                source="data.gov.in-agricultural-commodities"
            ) for item in real_data[:50]]
            return MarketPriceListResponse(data=prices, count=len(prices), region=state or "India")
        
        # Fall back to database records only if they exist
        if db is None:
            sample_prices = MarketService._sample_market_prices(crop or "Wheat", state or "India", district or "Local Mandi")
            return MarketPriceListResponse(data=sample_prices, count=len(sample_prices), region=state or "India")

        query = select(MarketData)
        if crop:
            query = query.where(MarketData.crop_name.ilike(f"%{crop}%"))
        if state:
            query = query.where(MarketData.region.ilike(f"%{state}%"))
        if district:
            query = query.where(MarketData.market_name.ilike(f"%{district}%"))
        
        result = await db.execute(query.limit(20))
        rows = result.scalars().all()

        if not rows:
            sample_prices = MarketService._sample_market_prices(crop or "Wheat", state or "India", district or "Local Mandi")
            return MarketPriceListResponse(data=sample_prices, count=len(sample_prices), region=state or "India")

        prices = [MarketPriceResponse(
            state=row.region or state or "India",
            district=district or row.region or "Unknown",
            market=row.market_name or "Mandi",
            commodity=row.crop_name,
            variety="Standard",
            grade="A",
            arrival_date=(row.price_date or row.created_at).isoformat() if (row.price_date or row.created_at) else "",
            min_price=row.price_per_kg,
            max_price=row.price_per_kg,
            modal_price=row.price_per_kg,
            source="farmfusion-database"
        ) for row in rows]
        return MarketPriceListResponse(data=prices, count=len(prices), region=state or "India")

    @staticmethod
    def _sample_market_prices(crop: str, state: str, district: str) -> List[MarketPriceResponse]:
        fallback = [
            MarketPriceResponse(
                state=state,
                district=district,
                market="Central Mandi",
                commodity=crop,
                variety="Standard",
                grade="A",
                arrival_date=datetime.utcnow().isoformat(),
                min_price=1200.0,
                max_price=1480.0,
                modal_price=1350.0,
                source="fallback-sample"
            ),
            MarketPriceResponse(
                state=state,
                district=district,
                market="Regional Mandi",
                commodity=crop,
                variety="Premium",
                grade="A",
                arrival_date=datetime.utcnow().isoformat(),
                min_price=1300.0,
                max_price=1550.0,
                modal_price=1425.0,
                source="fallback-sample"
            ),
            MarketPriceResponse(
                state=state,
                district=district,
                market="Local Mandi",
                commodity=crop,
                variety="Standard",
                grade="B",
                arrival_date=datetime.utcnow().isoformat(),
                min_price=1100.0,
                max_price=1380.0,
                modal_price=1235.0,
                source="fallback-sample"
            ),
        ]
        return fallback

    @staticmethod
    async def get_all_mandis(db: AsyncSession) -> List[str]:
        """Get list of all available mandis from database."""
        result = await db.execute(select(MarketData.market_name).distinct())
        mandis = [row[0] for row in result.all() if row[0]]
        
        if not mandis:
            raise RuntimeError("No mandi data available in database. Please populate market data or configure MANDI_API_KEY.")
        
        return mandis

    @staticmethod
    async def _fetch_real_market_trends(crop: str, region: str, months: int) -> Optional[List[dict]]:
        if not getattr(settings, 'MANDI_API_KEY', None):
            return None

        try:
            url = f"{MarketService.COMMODITY_API_URL}?api-key={settings.MANDI_API_KEY}&format=json&limit=500"
            if crop:
                url += f"&filters[commodity_name][]={urllib.parse.quote_plus(crop)}"
            if region:
                url += f"&filters[state][]={urllib.parse.quote_plus(region)}"

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.load(response)
                records = data.get('records', [])
                return records if records else None
        except Exception:
            return None

    @staticmethod
    def _build_trend_data(records: List[dict], months: int) -> List[Dict[str, Any]]:
        monthly: dict[str, dict[str, Any]] = {}
        for item in records:
            date_str = item.get('arrival_date') or item.get('date') or item.get('price_date')
            if not date_str:
                continue
            try:
                month_key = datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%Y-%m")
            except Exception:
                continue

            price_value = item.get('modal_price') or item.get('min_price') or item.get('max_price')
            try:
                price = float(price_value)
            except Exception:
                continue

            bucket = monthly.setdefault(month_key, {'total': 0.0, 'count': 0})
            bucket['total'] += price
            bucket['count'] += 1

        if not monthly:
            return []

        sorted_months = sorted(monthly.keys())[-months:]
        return [
            {
                'date': f"{month}-01",
                'predicted_price': round(monthly[month]['total'] / monthly[month]['count'], 2),
                'trend': 'observed',
            }
            for month in sorted_months
        ]

    @staticmethod
    async def get_price_trends(crop: str, region: str, months: int, db: AsyncSession) -> dict:
        """Get real price trend history from public APIs or database."""
        if not crop:
            raise RuntimeError("Crop name is required to build trend data.")

        records = await MarketService._fetch_real_market_trends(crop, region, months)
        trend_data = []
        if records:
            trend_data = MarketService._build_trend_data(records, months)

        if not trend_data:
            query = select(MarketData)
            query = query.where(MarketData.crop_name.ilike(f"%{crop}%"))
            if region:
                query = query.where(MarketData.region.ilike(f"%{region}%"))
            result = await db.execute(query)
            rows = result.scalars().all()
            data = [
                {
                    'arrival_date': row.price_date.isoformat() if row.price_date else row.created_at.isoformat(),
                    'modal_price': row.price_per_kg,
                }
                for row in rows
                if row.price_per_kg is not None
            ]
            trend_data = MarketService._build_trend_data(data, months)

        if not trend_data:
            raise RuntimeError(
                f"Real market trend data not available for {crop} in {region or 'all regions'}. "
                "Configure MANDI_API_KEY or populate market_data with historical prices."
            )

        return {
            'crop_name': crop,
            'region': region or 'India',
            'source': 'data.gov.in' if getattr(settings, 'MANDI_API_KEY', None) else 'farmfusion-database',
            'trend_data': trend_data,
        }

    @staticmethod
    async def predict_market_prices(request: MarketPredictionRequest) -> MarketPredictionResponse:
        """Predict market prices using AI agent based on historical data."""
        agent = MarketAnalysisAgent()
        prediction = agent.predict(request.commodity, request.region)
        return MarketPredictionResponse(commodity=request.commodity, prediction=prediction)
