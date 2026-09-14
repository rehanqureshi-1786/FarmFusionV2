#!/usr/bin/env python3
"""Root runner for FarmFusion backend."""
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if os.path.exists(backend_dir):
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    reload_flag = os.getenv("RELOAD", str(settings.debug)).lower() in ("true", "1", "yes")

    print(f"Starting FarmFusion Backend on port {port}...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_flag,
        log_level="info",
        workers=1,
    )
