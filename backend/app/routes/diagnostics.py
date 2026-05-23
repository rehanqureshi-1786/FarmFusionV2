"""
Diagnostics Routes - For debugging and health checks

These endpoints help verify that the backend services are properly configured
and working.
"""
from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from app.agents.weather_agent import weather_agent
from app.agents.groq_client import groq_client
from app.agents.gemini_client import gemini_client

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/config")
async def check_configuration():
    """
    # Check Backend Configuration

    Verifies that all required API keys and services are configured.
    """
    settings = get_settings()

    return {
        "weather_api": {
            "configured": True,
            "provider": "open-meteo",
            "note": "Open-Meteo does not require an API key"
        },
        "openweather_api": {
            "configured": bool(settings.openweather_api_key and len(settings.openweather_api_key) > 10),
            "key_length": len(settings.openweather_api_key) if settings.openweather_api_key else 0,
            "key_prefix": settings.openweather_api_key[:6] + "..." if settings.openweather_api_key else None
        },
        "groq_api": {
            "configured": bool(settings.groq_api_key and len(settings.groq_api_key) > 10),
            "key_length": len(settings.groq_api_key) if settings.groq_api_key else 0,
            "key_prefix": settings.groq_api_key[:6] + "..." if settings.groq_api_key else None,
            "model": settings.groq_model
        },
        "openai_api": {
            "configured": bool(settings.openai_api_key and len(settings.openai_api_key) > 10),
            "key_length": len(settings.openai_api_key) if settings.openai_api_key else 0,
            "key_prefix": settings.openai_api_key[:10] + "..." if settings.openai_api_key else None,
            "model": settings.openai_model
        },
        "gemini_api": {
            "configured": bool(settings.gemini_api_key and len(settings.gemini_api_key) > 10),
            "key_length": len(settings.gemini_api_key) if settings.gemini_api_key else 0
        },
        "cors_origins": settings.allowed_origins,
        "database_url": settings.database_url[:30] + "..." if settings.database_url else None
    }


@router.get("/weather-agent")
async def check_weather_agent():
    """
    # Check Weather Agent

    Tests if the weather agent is properly configured and can fetch data.
    """
    try:
        is_available = weather_agent.is_available()

        if is_available:
            weather = await weather_agent.get_current_weather(24.5854, 73.7125)
            return {
                "status": "available",
                "provider": "open-meteo",
                "test_weather": weather
            }
        else:
            return {
                "status": "unavailable",
                "provider": "open-meteo",
                "message": "Weather service is unavailable"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Weather agent encountered an error"
        }


@router.get("/ai-agents")
async def check_ai_agents():
    """
    # Check AI Agents

    Verifies that Groq and Gemini AI clients are configured.
    """
    return {
        "groq": {
            "available": groq_client.is_available(),
            "model": get_settings().groq_model if groq_client.is_available() else None
        },
        "openai": {
            "configured": bool(get_settings().openai_api_key and len(get_settings().openai_api_key) > 10),
            "model": get_settings().openai_model
        },
        "gemini": {
            "available": gemini_client.is_available(),
            "model": gemini_client.model_name if gemini_client.is_available() else gemini_client.model_name,
            "configured": bool(get_settings().gemini_api_key and len(get_settings().gemini_api_key) > 10)
        },
        "note": "Groq is preferred for voice responses and intents, OpenAI is fallback, Gemini is used for crop disease image analysis"
    }


@router.get("/gemini")
async def check_gemini_agent():
    """
    # Check Gemini Agent

    Verifies that Gemini is configured for disease image analysis.
    """
    settings = get_settings()
    gemini_configured = bool(settings.gemini_api_key and len(settings.gemini_api_key) > 10)

    return {
        "status": "available" if gemini_client.is_available() else "unavailable",
        "configured": gemini_configured,
        "model": gemini_client.model_name,
        "use_case": "crop disease image analysis",
        "message": (
            "Gemini is ready for disease detection."
            if gemini_client.is_available()
            else "Gemini is not ready. Add GEMINI_API_KEY and install google-generativeai."
        )
    }


@router.get("/all")
async def full_diagnostics():
    """
    # Full System Diagnostics

    Comprehensive check of all backend services.
    """
    settings = get_settings()

    diagnostics = {
        "services": {
            "weather_api": True,
            "groq_ai": bool(settings.groq_api_key and len(settings.groq_api_key) > 10),
            "openai_ai": bool(settings.openai_api_key and len(settings.openai_api_key) > 10),
            "gemini_ai": bool(settings.gemini_api_key and len(settings.gemini_api_key) > 10),
        },
        "configuration": {
            "cors_origins_count": len(settings.allowed_origins),
            "debug_mode": settings.debug,
            "database_configured": bool(settings.database_url)
        },
        "recommendations": []
    }

    # Add recommendations based on status
    if not diagnostics["services"]["groq_ai"]:
        diagnostics["recommendations"].append(
            "Groq API key not configured. Add GROQ_API_KEY to .env file for voice assistant"
        )

    if not diagnostics["services"]["openai_ai"]:
        diagnostics["recommendations"].append(
            "OpenAI API key not configured. Add OPENAI_API_KEY to .env file for voice assistant responses"
        )

    if not diagnostics["services"]["gemini_ai"]:
        diagnostics["recommendations"].append(
            "Gemini API key not configured (optional)"
        )

    return diagnostics
