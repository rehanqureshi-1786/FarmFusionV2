"""FastAPI application entry point."""
from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.database import init_db
from app.api.v1.auth import router as auth_router
from app.api.v1.crops import router as crops_router
from app.api.v1.market import router as market_router
from app.api.v1.voice import router as voice_router
from app.api.v1.marketplace import router as marketplace_router
from app.api.v1.labour import router as labour_router
from app.api.v1.store import router as store_router
from app.api.v1.lifecycle import router as lifecycle_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.app_name}...")
    await init_db()
    print("Database initialized.")
    yield
    print(f"Shutting down {settings.app_name}...")

app = FastAPI(
    title="AI-powered agriculture platform API",
    description="AI-powered agriculture platform API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

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
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "app_name": settings.app_name}

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else None,
    }

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(crops_router, prefix=settings.api_v1_prefix)
app.include_router(market_router, prefix=settings.api_v1_prefix)
app.include_router(voice_router, prefix=settings.api_v1_prefix)
app.include_router(marketplace_router, prefix=settings.api_v1_prefix)
app.include_router(labour_router, prefix=settings.api_v1_prefix)
app.include_router(store_router, prefix=settings.api_v1_prefix)
app.include_router(lifecycle_router, prefix=settings.api_v1_prefix)
