#!/usr/bin/env python3
"""Entry point for running the FastAPI application."""
import os
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    reload_flag = os.getenv("RELOAD", str(settings.debug)).lower() in ("true", "1", "yes")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_flag,
        log_level="info"
    )

