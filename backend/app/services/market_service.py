import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import MarketData, PricePrediction
from app.agents.market_agent import market_agent


class MarketService:
    """Service layer for market prices using Hybrid CSV + AI approach"""
    
    # Path to the CSV dataset (located in project root)
    CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / "commodity_price.csv"

    @staticmethod
    async def get_current_prices(
        state: Optional[str] = None,
        district: Optional[str] = None,
        commodity: Optional[str] = None,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get current market prices from CSV, with AI fallback.
        """
        # Always start with simulated "Live" data as a baseline
        csv_data = [
            {
                "state": "Rajasthan", "district": "Udaipur", "market": "Fatehnagar",
                "commodity": "Wheat", "variety": "Common", "grade": "FAQ",
                "arrival_date": datetime.now().strftime("%Y-%m-%d"),
                "min_price": 2400, "max_price": 2600, "modal_price": 2500,
                "source": "Live Simulated"
            },
            {
                "state": "Rajasthan", "district": "Udaipur", "market": "Fatehnagar",
                "commodity": "Maize", "variety": "Yellow", "grade": "FAQ",
                "arrival_date": datetime.now().strftime("%Y-%m-%d"),
                "min_price": 2100, "max_price": 2300, "modal_price": 2200,
                "source": "Live Simulated"
            },
            {
                "state": "Rajasthan", "district": "Chittorgarh", "market": "Nimbahera",
                "commodity": "Mustard", "variety": "Mustard", "grade": "FAQ",
                "arrival_date": datetime.now().strftime("%Y-%m-%d"),
                "min_price": 5400, "max_price": 5800, "modal_price": 5600,
                "source": "Live Simulated"
            },
            {
                "state": "Rajasthan", "district": "Rajsamand", "market": "Rajsamand",
                "commodity": "Soybean", "variety": "Yellow", "grade": "FAQ",
                "arrival_date": datetime.now().strftime("%Y-%m-%d"),
                "min_price": 4500, "max_price": 4800, "modal_price": 4650,
                "source": "Live Simulated"
            }
        ]
        
        # 1. Try to read and AGGREGATE from CSV
        if os.path.exists(MarketService.CSV_PATH):
            try:
                with open(MarketService.CSV_PATH, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Apply filters
                        if state and state.lower() not in row["State"].lower():
                            continue
                        if district and district.lower() not in row["District"].lower():
                            continue
                        if commodity and commodity.lower() not in row["Commodity"].lower():
                            continue
                        if market and market.lower() not in row["Market"].lower():
                            continue
                        
                        csv_data.append({
                            "state": row["State"],
                            "district": row["District"],
                            "market": row["Market"],
                            "commodity": row["Commodity"],
                            "variety": row["Variety"],
                            "grade": row["Grade"],
                            "arrival_date": row["Arrival_Date"],
                            "min_price": float(row["Min_x0020_Price"] or 0),
                            "max_price": float(row["Max_x0020_Price"] or 0),
                            "modal_price": float(row["Modal_x0020_Price"] or 0),
                            "source": "CSV Dataset"
                        })
            except Exception as e:
                print(f"Error reading market CSV: {e}")

        # 2. Filtering baseline: Only keep simulated data if it matches requested filters
        final_data = []
        for item in csv_data:
            if state and state.lower() not in item["state"].lower(): continue
            if district and district.lower() not in item["district"].lower(): continue
            if commodity and commodity.lower() not in item["commodity"].lower(): continue
            final_data.append(item)

        # 3. Hybrid/Fallback: If no data remains, Use AI to generate estimates
        if not final_data:
            region = f"{district or ''} {state or 'India'}".strip()
            return await market_agent.get_current_prices_from_ai(region=region, crop=commodity)

        # Return the first 200 items (simulated items will be at the front)
        return final_data[:200]

    @staticmethod
    async def get_all_mandis() -> List[Dict[str, str]]:
        """
        Extract unique list of Mandis (Market + District + State)
        """
        mandis = set()
        
        if os.path.exists(MarketService.CSV_PATH):
            try:
                with open(MarketService.CSV_PATH, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        mandi_key = (row["Market"], row["District"], row["State"])
                        mandis.add(mandi_key)
            except Exception as e:
                print(f"Error reading mandis from CSV: {e}")

        # Convert set to list of dicts and sort
        mandi_list = [
            {"market": m, "district": d, "state": s} 
            for m, d, s in mandis
        ]
        return sorted(mandi_list, key=lambda x: (x["state"], x["market"]))

    @staticmethod
    async def predict_prices(
        crop_name: str,
        region: str,
        current_price: Optional[float] = None,
        prediction_months: int = 3,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Predict future prices using AI augmented with CSV historical data.
        """
        # Fetch historical data points from CSV for context
        historical_context = []
        if os.path.exists(MarketService.CSV_PATH):
            try:
                with open(MarketService.CSV_PATH, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if crop_name.lower() in row["Commodity"].lower():
                            historical_context.append({
                                "date": row["Arrival_Date"],
                                "price": row["Modal_x0020_Price"],
                                "district": row["District"]
                            })
                            if len(historical_context) >= 10: break
            except: pass

        # Generate prediction via Agent (now supports context)
        result = await market_agent.predict_prices(
            crop_name=crop_name,
            region=region,
            current_price=current_price or 25.0, # Default if not provided
            prediction_months=prediction_months,
            historical_data=historical_context
        )

        # Save prediction if db available
        if db:
            await MarketService._save_prediction(crop_name, region, result, db)

        return result

    @staticmethod
    async def _save_prediction(
        crop_name: str,
        region: str,
        result: Dict[str, Any],
        db: AsyncSession
    ):
        """Save prediction to database"""
        for pred in result.get("predictions", []):
            try:
                # Handle potential date parsing issues
                date_str = pred["month"]
                try:
                    p_date = datetime.strptime(date_str, "%B %Y")
                except:
                    p_date = datetime.now()

                prediction = PricePrediction(
                    crop_name=crop_name,
                    region=region,
                    prediction_for_date=p_date,
                    predicted_price_per_kg=pred["predicted_price"],
                    confidence=pred.get("confidence", 0.7),
                    trend=pred.get("trend", "stable"),
                    ai_analysis=result.get("ai_analysis", "")
                )
                db.add(prediction)
            except Exception as e:
                print(f"Error saving prediction row: {e}")

        await db.commit()

    @staticmethod
    async def get_price_trends(
        crop_name: str,
        region: str,
        months: int = 6,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Get price trends for a crop"""
        # Logic remains similar but could be enhanced with CSV trend analysis
        if db:
            result = await db.execute(
                select(PricePrediction)
                .where(PricePrediction.crop_name == crop_name)
                .where(PricePrediction.region == region)
                .order_by(PricePrediction.prediction_for_date.desc())
                .limit(months)
            )
            predictions = result.scalars().all()

            if predictions:
                return {
                    "crop_name": crop_name,
                    "region": region,
                    "trend_data": [
                        {
                            "date": p.prediction_for_date.strftime("%Y-%m"),
                            "predicted_price": p.predicted_price_per_kg,
                            "confidence": p.confidence,
                            "trend": p.trend
                        }
                        for p in predictions
                    ]
                }

        return await MarketService._get_mock_trends(crop_name, region, months)

    @staticmethod
    async def _get_mock_trends(
        crop_name: str,
        region: str,
        months: int
    ) -> Dict[str, Any]:
        """Generate mock trend data (fallback)"""
        from datetime import datetime, timedelta

        base_price = 25  # Base price
        trend_data = []

        for i in range(months):
            date = datetime.now() - timedelta(days=30 * i)
            price = base_price + (i % 3) * 2 - 1
            trend_data.append({
                "date": date.strftime("%Y-%m"),
                "predicted_price": price,
                "trend": "rising" if i < 2 else "stable"
            })

        return {
            "crop_name": crop_name,
            "region": region,
            "source": "simulated",
            "trend_data": trend_data
        }
