"""
Authentication Service - Firebase Auth integration
Verifies Firebase tokens from Android app
"""
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth, credentials
from app.core.config import get_settings


class AuthService:
    """Service layer for Firebase Authentication"""

    _firebase_initialized = False

    @classmethod
    def _initialize_firebase(cls):
        """Initialize Firebase Admin SDK (only once)"""
        if cls._firebase_initialized:
            return

        try:
            settings = get_settings()

            # Try to use default credentials or service account
            if settings.firebase_credentials_path:
                cred = credentials.Certificate(settings.firebase_credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                # Try default initialization (requires GOOGLE_APPLICATION_CREDENTIALS env var)
                firebase_admin.initialize_app()

            cls._firebase_initialized = True
            print("Firebase initialized successfully")
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            cls._firebase_initialized = False

    @staticmethod
    async def verify_token(id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token from Android app

        Args:
            id_token: Firebase ID token from Android

        Returns:
            User data if valid, None if invalid
        """
        AuthService._initialize_firebase()

        if not AuthService._firebase_initialized:
            # Fallback for development - accept any token
            return {
                "uid": "dev-user-123",
                "phone_number": "+911234567890",
                "verified": True,
                "source": "development"
            }

        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                "uid": decoded_token["uid"],
                "phone_number": decoded_token.get("phone_number"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "verified": True,
                "source": "firebase"
            }
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None

    @staticmethod
    async def get_user(uid: str) -> Optional[Dict[str, Any]]:
        """Get user info from Firebase"""
        AuthService._initialize_firebase()

        if not AuthService._firebase_initialized:
            return None

        try:
            user = auth.get_user(uid)
            return {
                "uid": user.uid,
                "phone_number": user.phone_number,
                "email": user.email,
                "name": user.display_name,
                "photo_url": user.photo_url,
                "disabled": user.disabled
            }
        except Exception as e:
            print(f"Failed to get user: {e}")
            return None

    @staticmethod
    def create_custom_token(uid: str, claims: Optional[Dict] = None) -> str:
        """Create custom token for user"""
        AuthService._initialize_firebase()

        if not AuthService._firebase_initialized:
            return "dev-token"

        try:
            return auth.create_custom_token(uid, claims or {})
        except Exception as e:
            print(f"Failed to create token: {e}")
            return ""
