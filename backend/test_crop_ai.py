
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.core.config import get_settings
from app.agents.groq_client import groq_client
from app.agents.crop_agent import crop_agent

async def test_groq():
    settings = get_settings()
    print(f"DEBUG: App Name: {settings.app_name}")
    print(f"DEBUG: Groq API Key set: {bool(settings.groq_api_key)}")
    if settings.groq_api_key:
        print(f"DEBUG: Key length: {len(settings.groq_api_key)}")
        print(f"DEBUG: Key preview: {settings.groq_api_key[:10]}...")
    
    print(f"DEBUG: Groq available: {groq_client.is_available()}")
    
    # Debug raw completion
    raw_res = await groq_client.chat_completion(
        system_prompt="Test",
        user_prompt="Say hi in JSON format: {\"msg\": \"hi\"}"
    )
    print(f"DEBUG: Raw Test Result: {raw_res}")
    
    try:
        recommendations, insights = await crop_agent.get_recommendations(
            location="Test Region, India",
            soil_type="loamy",
            rainfall_mm=800,
            temperature_c=25,
            farm_size_acres=2.5,
            budget_usd=500
        )
        print("\n[SUCCESS] AI Agent returned recommendations:")
        for rec in recommendations[:2]:
            print(f" - {rec.crop_name}: Confidence {rec.confidence_score}")
        print(f"\nAI Insights: {insights[:100]}...")
    except Exception as e:
        print(f"\n[FAIL] AI Agent failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_groq())
