"""
Crop Service - Business logic for crop recommendations
Handles database operations and AI agent coordination
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Recommendation, Farm
from app.agents.crop_agent import crop_agent
from app.models.schemas import CropRecommendRequest, CropRecommendResponse


class CropService:
    """Service layer for crop recommendations"""

    @staticmethod
    async def get_recommendations(
        request: CropRecommendRequest,
        user_id: Optional[int] = None,
        db: Optional[AsyncSession] = None
    ) -> CropRecommendResponse:
        """
        Get crop recommendations using AI agent

        Args:
            request: Crop recommendation request data
            user_id: Optional user ID for saving to history
            db: Optional database session

        Returns:
            CropRecommendResponse with recommendations
        """
        # Call AI agent
        recommendations, insights = await crop_agent.get_recommendations(
            location=request.location,
            soil_type=request.soil_type,
            rainfall_mm=request.rainfall_mm,
            temperature_c=request.temperature_c,
            farm_size_acres=request.farm_size_acres,
            budget_usd=request.budget_usd,
            language=request.preferred_language
        )

        from datetime import datetime

        response = CropRecommendResponse(
            success=True,
            recommendations=recommendations,
            ai_insights=insights,
            timestamp=datetime.now().isoformat()
        )

        # Save to history if user_id provided
        if user_id and db:
            await CropService._save_recommendation(user_id, request, response, db)

        return response

    @staticmethod
    async def _save_recommendation(
        user_id: int,
        request: CropRecommendRequest,
        response: CropRecommendResponse,
        db: AsyncSession
    ):
        """Save recommendation to database history"""
        import json

        recommendation = Recommendation(
            user_id=user_id,
            location=request.location,
            soil_type=request.soil_type,
            rainfall_mm=request.rainfall_mm,
            temperature_c=request.temperature_c,
            farm_size_acres=request.farm_size_acres,
            recommendations_data=[r.model_dump() for r in response.recommendations],
            ai_insights=response.ai_insights
        )
        db.add(recommendation)
        await db.commit()

    @staticmethod
    async def get_user_history(
        user_id: int,
        db: AsyncSession,
        limit: int = 10
    ) -> List[dict]:
        """Get user's recommendation history"""
        result = await db.execute(
            select(Recommendation)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
            .limit(limit)
        )
        recommendations = result.scalars().all()

        return [
            {
                "id": r.id,
                "location": r.location,
                "soil_type": r.soil_type,
                "recommendations": r.recommendations_data,
                "insights": r.ai_insights,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in recommendations
        ]

    @staticmethod
    async def get_farm_recommendations(
        farm_id: int,
        user_id: int,
        db: AsyncSession
    ) -> List[dict]:
        """Get recommendations for a specific farm"""
        result = await db.execute(
            select(Recommendation)
            .where(Recommendation.farm_id == farm_id)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
        )
        recommendations = result.scalars().all()

        return [
            {
                "id": r.id,
                "recommendations": r.recommendations_data,
                "insights": r.ai_insights,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in recommendations
        ]
