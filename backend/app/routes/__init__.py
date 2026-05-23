"""API Routes for FarmFusion Backend"""
from .crop import router as crop_router
from .disease import router as disease_router
from .market import router as market_router
from .weather import router as weather_router
from .auth import router as auth_router
from .user import router as user_router
from .voice import router as voice_router
from .diagnostics import router as diagnostics_router
from .alerts import router as alerts_router
from .store import router as store_router

__all__ = [
    "crop_router",
    "disease_router",
    "market_router",
    "weather_router",
    "auth_router",
    "user_router",
    "voice_router",
    "diagnostics_router",
    "alerts_router",
    "store_router",
]
