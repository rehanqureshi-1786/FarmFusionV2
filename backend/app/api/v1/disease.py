from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.disease_info_service import DiseaseInfoService
from app.services.disease_service import DiseaseService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/disease", tags=["disease"])


@router.post("/detect")
async def detect_disease(
    image: UploadFile = File(...),
    crop_type: Optional[str] = Query(None),
    firebase_token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Detect disease from uploaded image using AI vision API."""
    # Authentication is optional in local/dev mode. To fully disable Firebase auth,
    # set BYPASS_FIREBASE_AUTH=1 in the environment or run the server with settings.debug=True.
    # The AuthService.verify_token will return a fake user when bypassed.
    firebase_uid = None
    
    try:
        content = await image.read()
        result = await DiseaseService.detect_disease(content, db, firebase_uid, image.filename)

        if not result:
            raise RuntimeError("Failed to detect disease from image")

        return {
            "success": True,
            "data": {
                "disease_name": result.get("disease"),
                "confidence": result.get("confidence"),
                "description": result.get("description"),
                "crop_type": crop_type,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "farmfusion-gemini-vision-api",
                "ai_analyzed": True,
            },
        }
    except RuntimeError as exc:
        status = 503 if "quota" in str(exc).lower() or "rate limit" in str(exc).lower() else 502
        return JSONResponse(
            status_code=status,
            content={"success": False, "error": "AI service error", "detail": str(exc)},
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Processing error", "detail": str(exc)},
        )


@router.get("/history")
async def get_disease_history(
    firebase_token: Optional[str] = Query(None, description="Firebase ID token"),
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db)
):
    """Get disease detection history for authenticated user from database.

    If no token is provided and BYPASS_FIREBASE_AUTH is enabled the endpoint will
    return the development user's history or an empty list.
    """
    try:
        if firebase_token:
            user_data = await AuthService.verify_token(firebase_token)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid Firebase token")
            firebase_uid = user_data.get("uid")
        else:
            # No token supplied — attempt to use AuthService bypass (if enabled),
            # otherwise return empty history for unauthenticated requests.
            user_data = await AuthService.verify_token("")
            if user_data:
                firebase_uid = user_data.get("uid")
            else:
                return {"success": True, "data": [], "count": 0}

        history = await DiseaseService.get_user_disease_history(firebase_uid, db, limit)

        return {
            "success": True,
            "data": history,
            "count": len(history)
        }
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Failed to fetch history", "detail": str(e)},
        )


@router.get("/info/{disease_name}")
async def get_disease_info(disease_name: str):
    """Get information about a detected disease using a live knowledge source."""
    try:
        info = DiseaseInfoService.get_disease_info(disease_name)
        return {
            "success": True,
            "data": info,
        }
    except ValueError as exc:
        return {
            "success": True,
            "data": {
                "name": disease_name,
                "description": "No disease detected or disease could not be identified.",
                "treatment": [],
                "prevention": ["Maintain proper crop hygiene", "Monitor plants regularly"],
                "severity": "none",
                "note": str(exc),
            }
        }
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={"success": False, "error": "Disease info lookup failed", "detail": str(exc)},
        )
