from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.disease_agent import DiseaseDetectionAgent
from app.db.models import DiseaseDetection


class DiseaseService:
    @staticmethod
    async def detect_disease(
        image_bytes: bytes,
        db: AsyncSession,
        user_id: Optional[int] = None,
        firebase_uid: Optional[str] = None,
        image_filename: Optional[str] = None,
        crop_type: Optional[str] = None,
        response_language: str = "en",
    ) -> Optional[dict]:
        """Detect disease from raw image bytes using Gemini Vision API and save to database."""
        agent = DiseaseDetectionAgent()
        detected = agent.detect(
            image_bytes,
            crop_type=crop_type,
            response_language=response_language,
        )

        if detected:
            if user_id is None and firebase_uid:
                from app.services.user_service import UserService
                user = await UserService.get_user_by_firebase_uid(firebase_uid, db)
                user_id = user.id if user else None

            if user_id is not None:
                detection_record = DiseaseDetection(
                    user_id=user_id,
                    image_url=image_filename,
                    crop_type=crop_type,
                    disease_name=detected.get("disease"),
                    confidence=detected.get("confidence", 0.0),
                    severity=detected.get("severity", "unknown"),
                    description=detected.get("description"),
                    treatment_suggestions=detected.get("treatment", []),
                    prevention_tips=detected.get("prevention", []),
                )
                db.add(detection_record)
                await db.commit()

            return detected
        return None
    
    @staticmethod
    async def get_user_disease_history(
        user_id: Optional[int] = None,
        db: AsyncSession = None,
        limit: int = 10,
        firebase_uid: Optional[str] = None,
    ) -> List[dict]:
        """Get disease detection history for a user from database."""
        if user_id is None and firebase_uid:
            from app.services.user_service import UserService
            user = await UserService.get_user_by_firebase_uid(firebase_uid, db)
            user_id = user.id if user else None

        if user_id is None or db is None:
            return []

        query = select(DiseaseDetection).where(
            DiseaseDetection.user_id == user_id
        ).order_by(DiseaseDetection.created_at.desc()).limit(limit)
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "disease_name": r.disease_name,
                "confidence": r.confidence,
                "description": r.description,
                "crop_type": r.crop_type,
                "severity": r.severity,
                "treatment_suggestions": r.treatment_suggestions,
                "prevention_tips": r.prevention_tips,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]
