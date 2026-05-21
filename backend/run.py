#!/usr/bin/env python3
"""Minimal entrypoint so `python backend/run.py` launches the FastAPI app.

Place this at `backend/run.py` and run it from the repo root after activating
the virtualenv. It ensures the `backend` package directory is on `sys.path`
so `app.main:app` can be imported.
"""
import os
import sys
from pathlib import Path

# Ensure backend (this file's parent) is on sys.path when run from repo root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import uvicorn


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RELOAD", "0") in ("1", "true", "True")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
