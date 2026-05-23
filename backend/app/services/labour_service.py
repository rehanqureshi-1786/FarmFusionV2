from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import math
from app.db.models import LabourJob
from app.schemas.labour import LabourJobCreate

class LabourService:
    @staticmethod
    async def post_job(db: AsyncSession, poster_id: int, job_data: LabourJobCreate):
        db_job = LabourJob(
            **job_data.model_dump(),
            poster_id=poster_id
        )
        db.add(db_job)
        await db.commit()
        await db.refresh(db_job)
        return db_job

    @staticmethod
    async def find_nearby_jobs(
        db: AsyncSession, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 25.0,
        job_type: Optional[str] = None
    ):
        query = select(LabourJob).where(LabourJob.status == "open")
        
        if job_type:
            query = query.where(LabourJob.job_type == job_type)
            
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        # Filter by distance
        filtered = []
        for job in jobs:
            dist = LabourService._calculate_distance(latitude, longitude, job.latitude, job.longitude)
            if dist <= radius_km:
                filtered.append(job)
        
        return sorted(filtered, key=lambda x: LabourService._calculate_distance(latitude, longitude, x.latitude, x.longitude))

    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
