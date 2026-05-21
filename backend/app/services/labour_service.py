from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LabourJob
from app.schemas.labour import LabourJobCreate, LabourJobResponse


class LabourService:
    @staticmethod
    async def post_job(job: LabourJobCreate, db: AsyncSession) -> LabourJobResponse:
        labour_job = LabourJob(
            title=job.title,
            description=job.description or "",
            location=job.location or "",
            wage=job.wage or 0.0,
            start_date=job.start_date or "",
            end_date=job.end_date or "",
        )
        db.add(labour_job)
        await db.commit()
        await db.refresh(labour_job)
        return LabourJobResponse(
            id=labour_job.id,
            title=labour_job.title,
            description=labour_job.description,
            location=labour_job.location,
            wage=labour_job.wage,
            start_date=labour_job.start_date,
            end_date=labour_job.end_date,
            created_at=labour_job.created_at,
        )

    @staticmethod
    async def get_nearby_jobs(location: Optional[str], db: AsyncSession) -> List[LabourJobResponse]:
        query = select(LabourJob)
        if location:
            query = query.where(LabourJob.location == location)
        result = await db.execute(query)
        return [LabourJobResponse(
            id=job.id,
            title=job.title,
            description=job.description,
            location=job.location,
            wage=job.wage,
            start_date=job.start_date,
            end_date=job.end_date,
            created_at=job.created_at,
        ) for job in result.scalars().all()]
