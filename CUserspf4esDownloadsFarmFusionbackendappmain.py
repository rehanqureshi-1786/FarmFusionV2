"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import os

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.crops import router as crops_router
from app.api.v1.mandi import router as mandi_router
from app.api.v1.labour import router as labour_router
from app.api.v1.products import router as products_router
from app.api.v1.animals import router as animals_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name}...")
    
    # Create upload directory if it doesn't exist
    upload_dir = settings.upload_dir
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    yield
    
    # Shutdown
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


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "app_name": settings.app_name
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else None,
        "health": "/health"
    }


# Include API routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(crops_router, prefix=settings.api_v1_prefix)
app.include_router(mandi_router, prefix=settings.api_v1_prefix)
app.include_router(labour_router, prefix=settings.api_v1_prefix)
app.include_router(products_router, prefix=settings.api_v1_prefix)
app.include_router(animals_router, prefix=settings.api_v1_prefix)
