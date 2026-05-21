from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.crop_agent import CropRecommendationAgent
from app.db.models import Recommendation
from app.models.crop import Crop
from app.schemas.crop import CropRecommendRequest, CropRecommendationResponse


class CropService:
    @staticmethod
    async def list_crops(db: AsyncSession) -> List[CropRecommendationResponse]:
        result = await db.execute(select(Crop).limit(20))
        crops = result.scalars().all()
        return [CropRecommendationResponse(crop_name=c.name, recommendations=[{'recommendation': 'Update your irrigation schedule.'}]) for c in crops]

    @staticmethod
    async def get_recommendations(request: CropRecommendRequest, db: AsyncSession) -> CropRecommendationResponse:
        agent = CropRecommendationAgent()
        recommendation = agent.recommend(request.crop_name, request.soil_type)
        return CropRecommendationResponse(crop_name=request.crop_name, recommendations=[{"recommendation": recommendation}])

    @staticmethod
    async def get_crop(crop_id: int, db: AsyncSession):
        result = await db.execute(select(Crop).where(Crop.id == crop_id))
        return result.scalar_one_or_none()
