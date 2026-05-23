#!/usr/bin/env python3
"""Entry point for running the FastAPI application."""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Use root main:app so weather, alerts, disease, legacy crop/market, etc. match the Android app.
    # app.main:app is a slimmer API-only app and will 404 many mobile paths.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
