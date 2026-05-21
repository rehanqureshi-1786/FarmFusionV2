import json
import logging
import os
from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def _initialize():
        if not firebase_admin._apps:
            if settings.firebase_credentials_path:
                cred = credentials.Certificate(settings.firebase_credentials_path)
            elif settings.firebase_credentials_json:
                json_data = json.loads(settings.firebase_credentials_json)
                cred = credentials.Certificate(json_data)
            elif os.path.exists("/etc/secrets/FIREBASE_CREDENTIALS_JSON"):
                with open("/etc/secrets/FIREBASE_CREDENTIALS_JSON", "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                cred = credentials.Certificate(json_data)
            elif os.path.exists("/etc/secrets/firebase_credentials.json"):
                with open("/etc/secrets/firebase_credentials.json", "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                cred = credentials.Certificate(json_data)
            else:
                cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)

    @staticmethod
    async def verify_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            AuthService._initialize()
            decoded = auth.verify_id_token(token)
            return decoded
        except Exception as exc:
            logger.exception("Firebase token verification failed")
            return None
