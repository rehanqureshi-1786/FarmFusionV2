import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.services.market_service import MarketService

async def test_market_service():
    print("Testing MarketService CSV Loading...")
    
    # Test filtering for Wheat in Gujarat
    prices = await MarketService.get_current_prices(state="Gujarat", commodity="Wheat")
    
    print(f"Found {len(prices)} rows for Wheat in Gujarat.")
    for p in prices[:3]:
        print(f"- {p['market']}: ₹{p['modal_price']} ({p['source']})")
    
    # Test fallback
    print("\nTesting AI Fallback (searching for non-existent crop 'Vibranium')...")
    fallback_prices = await MarketService.get_current_prices(commodity="Vibranium")
    if fallback_prices:
        print(f"Fallback successful! Found {len(fallback_prices)} AI estimated rows.")
        for p in fallback_prices[:2]:
            print(f"- {p['commodity']} in {p['state']}: ₹{p['modal_price']} ({p.get('source', 'AI')})")
    else:
        print("Fallback failed or returned no data.")

if __name__ == "__main__":
    asyncio.run(test_market_service())
