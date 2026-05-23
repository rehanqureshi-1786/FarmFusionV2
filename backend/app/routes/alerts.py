"""
Dashboard / urgent farm alerts (weather-informed when lat/lon are provided).
"""
from fastapi import APIRouter, Query

from app.services.urgent_alert_service import get_dashboard_urgent_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/urgent")
async def get_urgent_alert(
    lat: float | None = Query(None, description="Farmer's latitude (optional)"),
    lon: float | None = Query(None, description="Farmer's longitude (optional)"),
):
    """
    Returns a single headline alert for the home dashboard carousel.
    Uses live weather when coordinates are sent; otherwise a static advisory.
    """
    return await get_dashboard_urgent_alert(lat, lon)
