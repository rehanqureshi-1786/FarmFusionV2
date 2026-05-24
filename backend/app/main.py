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
from app.routes.weather import router as weather_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.app_name}...")
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
app.include_router(weather_router, prefix=settings.api_v1_prefix)
