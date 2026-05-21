"""
User Management API Routes
POST /users/farms - Create farm
GET /users/farms - Get user's farms
PUT /users/farms/{id} - Update farm
DELETE /users/farms/{id} - Delete farm
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.deps import get_db
from app.services.user_service import UserService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/farms")
async def create_farm(
    firebase_token: str = Query(..., description="Firebase ID token"),
    name: str = Query(..., description="Farm name"),
    location: str = Query(..., description="Location/address"),
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    soil_type: str = Query(..., description="Soil type (clay, sandy, loamy, silty, peaty)"),
    farm_size_acres: float = Query(..., description="Farm size in acres"),
    annual_rainfall_mm: float = Query(0, description="Annual rainfall in mm"),
    avg_temperature_c: float = Query(25, description="Average temperature in Celsius"),
    db: AsyncSession = Depends(get_db)
):
    """
    POST /users/farms

    Create a new farm for the authenticated user

    - All parameters required except rainfall and temperature

    Returns created farm details
    """
    try:
        # Verify token
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        # Get user
        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create farm
        farm = await UserService.create_farm(
            user_id=user.id,
            name=name,
            location=location,
            latitude=latitude,
            longitude=longitude,
            soil_type=soil_type,
            farm_size_acres=farm_size_acres,
            annual_rainfall_mm=annual_rainfall_mm,
            avg_temperature_c=avg_temperature_c,
            db=db
        )

        return {
            "success": True,
            "message": "Farm created successfully",
            "farm": {
                "id": farm.id,
                "name": farm.name,
                "location": farm.location,
                "latitude": farm.latitude,
                "longitude": farm.longitude,
                "soil_type": farm.soil_type,
                "farm_size_acres": farm.farm_size_acres,
                "created_at": farm.created_at.isoformat() if farm.created_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create farm: {str(e)}")


@router.get("/farms")
async def get_user_farms(
    firebase_token: str = Query(..., description="Firebase ID token"),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /users/farms

    Get all farms for the authenticated user
    """
    try:
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            return {"success": True, "farms": []}

        farms = await UserService.get_user_farms(user.id, db)

        return {
            "success": True,
            "farms": [
                {
                    "id": f.id,
                    "name": f.name,
                    "location": f.location,
                    "latitude": f.latitude,
                    "longitude": f.longitude,
                    "soil_type": f.soil_type,
                    "farm_size_acres": f.farm_size_acres,
                    "annual_rainfall_mm": f.annual_rainfall_mm,
                    "avg_temperature_c": f.avg_temperature_c,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in farms
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get farms: {str(e)}")


@router.get("/farms/{farm_id}")
async def get_farm_details(
    farm_id: int,
    firebase_token: str = Query(..., description="Firebase ID token"),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /users/farms/{farm_id}

    Get details of a specific farm
    """
    try:
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        farm = await UserService.get_farm(farm_id, user.id, db)
        if not farm:
            raise HTTPException(status_code=404, detail="Farm not found")

        return {
            "success": True,
            "farm": {
                "id": farm.id,
                "name": farm.name,
                "location": farm.location,
                "latitude": farm.latitude,
                "longitude": farm.longitude,
                "soil_type": farm.soil_type,
                "farm_size_acres": farm.farm_size_acres,
                "annual_rainfall_mm": farm.annual_rainfall_mm,
                "avg_temperature_c": farm.avg_temperature_c,
                "created_at": farm.created_at.isoformat() if farm.created_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get farm: {str(e)}")


@router.put("/farms/{farm_id}")
async def update_farm(
    farm_id: int,
    firebase_token: str = Query(..., description="Firebase ID token"),
    name: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    soil_type: Optional[str] = Query(None),
    farm_size_acres: Optional[float] = Query(None),
    annual_rainfall_mm: Optional[float] = Query(None),
    avg_temperature_c: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    PUT /users/farms/{farm_id}

    Update farm details
    """
    try:
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        updates = {k: v for k, v in {
            "name": name,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "soil_type": soil_type,
            "farm_size_acres": farm_size_acres,
            "annual_rainfall_mm": annual_rainfall_mm,
            "avg_temperature_c": avg_temperature_c
        }.items() if v is not None}

        success = await UserService.update_farm(farm_id, user.id, updates, db)

        if not success:
            raise HTTPException(status_code=404, detail="Farm not found")

        return {
            "success": True,
            "message": "Farm updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update farm: {str(e)}")


@router.delete("/farms/{farm_id}")
async def delete_farm(
    farm_id: int,
    firebase_token: str = Query(..., description="Firebase ID token"),
    db: AsyncSession = Depends(get_db)
):
    """
    DELETE /users/farms/{farm_id}

    Delete a farm
    """
    try:
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        success = await UserService.delete_farm(farm_id, user.id, db)

        if not success:
            raise HTTPException(status_code=404, detail="Farm not found")

        return {
            "success": True,
            "message": "Farm deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete farm: {str(e)}")


@router.get("/profile")
async def get_user_profile(
    firebase_token: str = Query(..., description="Firebase ID token"),
    db: AsyncSession = Depends(get_db)
):
    """
    GET /users/profile

    Get user profile information
    """
    try:
        user_data = await AuthService.verify_token(firebase_token)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        user = await UserService.get_user_by_firebase_uid(user_data["uid"], db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "success": True,
            "profile": {
                "id": user.id,
                "firebase_uid": user.firebase_uid,
                "phone_number": user.phone_number,
                "name": user.name,
                "email": user.email,
                "language_preference": user.language_preference,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "farm_count": len(user.farms) if hasattr(user, 'farms') else 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")
