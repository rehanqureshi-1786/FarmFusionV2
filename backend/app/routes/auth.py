"""
Authentication API Routes
POST /auth/verify - Verify Firebase token
GET /auth/user/{uid} - Get user info
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/verify")
async def verify_token(
    firebase_token: str = Query(..., description="Firebase ID token from Android app"),
    db: AsyncSession = Depends(get_db)
):
    """
    POST /auth/verify

    Verify Firebase authentication token and get/create user

    - **firebase_token**: ID token from Firebase Auth on Android

    Returns user data including uid, phone number, and database user ID
    """
    try:
        # Verify token
        user_data = await AuthService.verify_token(firebase_token)

        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        # Get or create user in database
        user = await UserService.get_or_create_user(
            firebase_uid=user_data["uid"],
            phone_number=user_data.get("phone_number"),
            db=db
        )

        return {
            "success": True,
            "message": "Authentication successful",
            "user": {
                "id": user.id,
                "firebase_uid": user.firebase_uid,
                "phone_number": user.phone_number,
                "name": user.name,
                "email": user.email,
                "language_preference": user.language_preference,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/user/{uid}")
async def get_user_info(uid: str):
    """
    GET /auth/user/{uid}

    Get user information from Firebase

    - **uid**: Firebase user ID
    """
    try:
        user = await AuthService.get_user(uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "success": True,
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")


@router.get("/test")
async def test_auth_api():
    """
    GET /auth/test

    Test endpoint for auth API
    """
    return {
        "success": True,
        "message": "Auth API is working!",
        "endpoints": {
            "verify": "POST /auth/verify?firebase_token=YOUR_TOKEN",
            "user_info": "GET /auth/user/{uid}"
        },
        "note": "Get Firebase token from Android app after Phone Auth"
    }
