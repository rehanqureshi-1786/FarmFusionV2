from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from app.db.models import CropCycle
from app.schemas.lifecycle import CropCycleCreate

class LifecycleService:
    @staticmethod
    async def start_cycle(db: AsyncSession, user_id: int, cycle_data: CropCycleCreate):
        db_cycle = CropCycle(
            **cycle_data.model_dump(),
            user_id=user_id
        )
        db.add(db_cycle)
        await db.commit()
        await db.refresh(db_cycle)
        return db_cycle

    @staticmethod
    async def get_user_cycles(db: AsyncSession, user_id: int):
        result = await db.execute(select(CropCycle).where(CropCycle.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def update_status(db: AsyncSession, cycle_id: int, status: str):
        result = await db.execute(select(CropCycle).where(CropCycle.id == cycle_id))
        db_cycle = result.scalars().first()
        if db_cycle:
            db_cycle.status = status
            await db.commit()
            await db.refresh(db_cycle)
        return db_cycle
