from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CropCycle
from app.schemas.lifecycle import CropCycleCreate, CropCycleResponse


class LifecycleService:
    @staticmethod
    async def start_crop_cycle(request: CropCycleCreate, db: AsyncSession) -> CropCycleResponse:
        cycle = CropCycle(
            farm_id=request.farm_id,
            current_stage=request.current_stage,
            start_date=request.start_date or "",
            end_date=request.end_date or "",
            status="active",
        )
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)
        return CropCycleResponse(
            id=cycle.id,
            farm_id=cycle.farm_id,
            current_stage=cycle.current_stage,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            status=cycle.status,
            created_at=cycle.created_at,
        )

    @staticmethod
    async def get_my_crops(db: AsyncSession) -> List[CropCycleResponse]:
        result = await db.execute(select(CropCycle))
        return [CropCycleResponse(
            id=cycle.id,
            farm_id=cycle.farm_id,
            current_stage=cycle.current_stage,
            start_date=cycle.start_date,
            end_date=cycle.end_date,
            status=cycle.status,
            created_at=cycle.created_at,
        ) for cycle in result.scalars().all()]
