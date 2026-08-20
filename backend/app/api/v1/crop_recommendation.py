"""
Crop Recommendation API Router — "No Soil Report" flow.

Exposes:
    POST /crop-recommendation/no-soil-report
"""
from fastapi import APIRouter, HTTPException

from app.schemas.crop_recommendation import (
    NoSoilReportRequest,
    NoSoilReportResponse,
)
from app.services.no_soil_crop_service import no_soil_crop_service

router = APIRouter(prefix="/crop-recommendation", tags=["Crop Recommendation"])


@router.post("/no-soil-report", response_model=NoSoilReportResponse)
async def no_soil_report_crop_recommendation(
    request: NoSoilReportRequest,
) -> NoSoilReportResponse:
    """
    POST /crop-recommendation/no-soil-report

    Recommend crops when the farmer has NO soil report.

    The flow auto-fetches soil (pH, texture) via SoilGrids (ISRIC) from
    latitude/longitude, weather (temperature/humidity/seasonal rainfall)
    via Open-Meteo Historical API, determines the season, then runs the
    trained XGBoost crop model to obtain candidate crops. A separate
    regional validation layer re-ranks them and the final top 3 are
    returned with an LLM explanation.

    IMPORTANT: N/P/K are NOT available from lat/lon without a soil test.
    The model requires plant-available N/P/K in kg/ha. Global mapped
    datasets (SoilGrids) provide concentration values (g/kg, mg/kg,
    cmolc/kg) which are NOT scientifically equivalent and cannot be
    converted without bulk density, depth, and mineralization assumptions.
    If N/P/K are needed, use the "I Have Soil Report" flow with lab data.

    Request:
        {
          "latitude": 27.0238,
          "longitude": 74.2179,
          "state": "Rajasthan"   // optional
        }

    Returns success, location, season, estimated soil (pH, texture),
    soil source, weather, top 3 crops with model probability + regional
    score, and an explanation/warnings.
    """
    try:
        return await no_soil_crop_service.recommend(request)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate crop recommendation: {exc}",
        )