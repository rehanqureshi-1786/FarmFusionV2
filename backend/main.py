"""
FarmFusion Backend - Main Application Entry Point
Run this file to start your backend server

Features:
- Crop Recommendations (Groq AI / Rule-based fallback)
- Disease Detection (Image analysis)
- Market Price Predictions (AI-powered)
- Weather Data (OpenWeatherMap integration)
- Firebase Authentication
- User Management & Farms

Start: python main.py
API Docs: http://localhost:8000/docs
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import init_db
from app.routes import (
    alerts_router,
    auth_router,
    crop_router,
    diagnostics_router,
    disease_router,
    market_router,
    store_router,
    user_router,
    voice_router,
    weather_router,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI-powered farming assistant backend API for FarmFusion",
    version=settings.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()
    print("FarmFusion Backend Started")
    print("API Documentation: http://localhost:8000/docs")
    print(f"Debug Mode: {settings.debug}")
    print("AI Provider: Groq API (fallback to rule-based)")
    print("Disease AI: Gemini Vision API when configured")
    print("Voice Assistant: /api/v1/voice")


app.include_router(crop_router, prefix="/api/v1")
app.include_router(disease_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(weather_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(store_router, prefix="/api/v1")

# IoT Animal Detection
from app.animal_detection import animal_detection_router, ws_router
app.include_router(animal_detection_router)
app.include_router(ws_router)

# Mount IoT Dashboard
import os
from fastapi.staticfiles import StaticFiles
_dash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard")
if os.path.exists(_dash_path):
    app.mount("/dashboard", StaticFiles(directory=_dash_path, html=True), name="dashboard")


@app.get("/")
async def root():
    """Root endpoint for a quick server health check."""
    return {
        "message": "Welcome to FarmFusion API!",
        "version": settings.version,
        "docs": "/docs",
        "endpoints": {
            "crop": "/api/v1/crop",
            "disease": "/api/v1/disease",
            "market": "/api/v1/market",
            "weather": "/api/v1/weather",
            "auth": "/api/v1/auth",
            "user": "/api/v1/users",
            "voice": "/api/v1/voice",
            "diagnostics": "/api/v1/diagnostics",
            "alerts": "/api/v1/alerts/urgent",
        },
        "features": [
            "Multilingual Voice Assistant",
            "Crop Recommendations",
            "Disease Detection",
            "Market Prices",
            "Weather Data",
            "Firebase Auth",
        ],
        "health": "OK",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "farmfusion-api",
        "version": settings.version,
        "features": {
            "crop_recommendations": True,
            "disease_detection": True,
            "market_predictions": True,
            "weather_data": True,
            "authentication": True,
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting FarmFusion Backend...")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
