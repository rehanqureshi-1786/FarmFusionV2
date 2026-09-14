#!/usr/bin/env python3
"""Entry point for running the FastAPI application."""
import os
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    reload_flag = os.getenv("RELOAD", "false").lower() in ("true", "1", "yes")

    # Use root main:app so weather, alerts, disease, legacy crop/market, etc. match the Android app.
    # app.main:app is a slimmer API-only app and will 404 many mobile paths.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_flag,
        log_level="info",
        workers=1,
    )
