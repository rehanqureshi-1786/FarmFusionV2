"""FastAPI application entry point."""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings

logger = logging.getLogger(__name__)
from app.api.v1.auth import router as auth_router
from app.api.v1.crops import router as crops_router
from app.api.v1.market import router as market_router
from app.api.v1.voice import router as voice_router
from app.api.v1.marketplace import router as marketplace_router
from app.api.v1.labour import router as labour_router
from app.api.v1.store import router as store_router
from app.api.v1.lifecycle import router as lifecycle_router
from app.api.v1.disease import router as disease_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.crop_recommendation import router as crop_recommendation_router
from app.api.v1.calling import router as calling_router
from app.routes.crop import router as legacy_crop_router
from app.routes.weather import router as weather_router
from app.routes.diagnostics import router as diagnostics_router



from app.services.disease_ml_service import DiseaseMLService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.app_name}...")
    # Initialize all SQLAlchemy tables
    from app.core.database import engine, Base
    import app.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize Disease Detection ML Model singleton at startup
    DiseaseMLService.initialize()
    yield
    print(f"Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered agriculture platform API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def language_context_middleware(request: Request, call_next):
    from app.core.language import resolve_language_code, set_current_language
    user_lang = request.headers.get("x-user-language") or request.headers.get("accept-language")
    if not user_lang:
        user_lang = request.query_params.get("language") or request.query_params.get("preferred_language")
    ctx = resolve_language_code(user_lang)
    set_current_language(ctx.canonical_code, ctx.dialect_name if ctx.is_dialect else None)
    response = await call_next(request)
    response.headers["X-Resolved-Language"] = ctx.canonical_code
    return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception in {request.method} {request.url.path}: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500, 
        content={"detail": f"Internal server error: {str(exc)[:200]}" if settings.debug else "Internal server error"}
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "app_name": settings.app_name}


@app.get("/")
async def root():
    return {"name": settings.app_name, "version": "1.0.0", "docs": "/docs" if settings.debug else None}


# Include API routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(crops_router, prefix=settings.api_v1_prefix)
app.include_router(market_router, prefix=settings.api_v1_prefix)
app.include_router(voice_router, prefix=settings.api_v1_prefix)
app.include_router(marketplace_router, prefix=settings.api_v1_prefix)
app.include_router(labour_router, prefix=settings.api_v1_prefix)
app.include_router(store_router, prefix=settings.api_v1_prefix)
app.include_router(lifecycle_router, prefix=settings.api_v1_prefix)
app.include_router(disease_router, prefix=settings.api_v1_prefix)
app.include_router(knowledge_router, prefix=settings.api_v1_prefix)
app.include_router(crop_recommendation_router, prefix=settings.api_v1_prefix)
app.include_router(calling_router, prefix=settings.api_v1_prefix)
# Direct root mount for Vobiz telephony audio stream
from app.api.v1.calling import telephony_audio_stream_endpoint
app.websocket("/ws/calling/stream")(telephony_audio_stream_endpoint)

app.include_router(weather_router, prefix=settings.api_v1_prefix)
app.include_router(diagnostics_router, prefix=settings.api_v1_prefix)
app.include_router(legacy_crop_router)

# IoT Animal Intrusion Detection Routers
from app.animal_detection import animal_detection_router, ws_router
app.include_router(animal_detection_router)
app.include_router(ws_router)

# Mount IoT Dashboard at /dashboard (without overwriting API root /)
import os
from fastapi.staticfiles import StaticFiles

# Resolve dashboard path from repository root or backend root
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_dashboard_dir = os.path.join(_repo_root, "dashboard")
if not os.path.exists(_dashboard_dir):
    _dashboard_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard")

if os.path.exists(_dashboard_dir):
    app.mount("/dashboard", StaticFiles(directory=_dashboard_dir, html=True), name="dashboard")


