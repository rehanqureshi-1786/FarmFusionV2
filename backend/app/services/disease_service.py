from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.disease_agent import DiseaseDetectionAgent
from app.db.models import DiseaseDetection


class DiseaseService:
    @staticmethod
    async def detect_disease(image_url: str, db: AsyncSession) -> Optional[dict]:
        agent = DiseaseDetectionAgent()
        detected = agent.detect(image_url)
        if detected:
            return {"disease": detected["disease"], "confidence": detected["confidence"]}
        return None
