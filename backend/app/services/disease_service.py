from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.disease_agent import DiseaseDetectionAgent
from app.db.models import DiseaseDetection


class DiseaseService:
    @staticmethod
    async def detect_disease(image_bytes: bytes, db: AsyncSession, firebase_uid: Optional[str] = None, image_filename: Optional[str] = None) -> Optional[dict]:
        """Detect disease from raw image bytes using Gemini Vision API and save to database."""
        agent = DiseaseDetectionAgent()
        detected = agent.detect(image_bytes)
        
        if detected:
            detection_record = DiseaseDetection(
                firebase_uid=firebase_uid or "anonymous",
                disease_name=detected.get("disease"),
                confidence=detected.get("confidence"),
                image_url=image_filename,
                description=detected.get("description"),
                detected_at=datetime.utcnow(),
            )
            db.add(detection_record)
            await db.commit()
            
            return detected
        return None
    
    @staticmethod
    async def get_user_disease_history(firebase_uid: str, db: AsyncSession, limit: int = 10) -> List[dict]:
        """Get disease detection history for a user from database."""
        query = select(DiseaseDetection).where(
            DiseaseDetection.firebase_uid == firebase_uid
        ).order_by(DiseaseDetection.detected_at.desc()).limit(limit)
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "disease_name": r.disease_name,
                "confidence": r.confidence,
                "description": r.description,
                "detected_at": r.detected_at.isoformat() if r.detected_at else None
            }
            for r in records
        ]
