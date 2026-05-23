from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime
import math
from app.db.models import MarketListing
from app.schemas.marketplace import MarketListingCreate, MarketListingUpdate

class MarketplaceService:
    @staticmethod
    async def create_listing(db: AsyncSession, user_id: int, listing: MarketListingCreate):
        db_listing = MarketListing(
            **listing.model_dump(),
            user_id=user_id
        )
        db.add(db_listing)
        await db.commit()
        await db.refresh(db_listing)
        return db_listing

    @staticmethod
    async def get_listings(
        db: AsyncSession, 
        crop_filter: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: float = 50.0
    ):
        query = select(MarketListing).where(MarketListing.is_active == True)
        
        if crop_filter:
            query = query.where(MarketListing.crop_name.ilike(f"%{crop_filter}%"))
            
        result = await db.execute(query)
        listings = result.scalars().all()
        
        if latitude is not None and longitude is not None:
            # Simple Euclidean distance filtering (optimization possible with GeoAlchemy)
            filtered = []
            for item in listings:
                dist = MarketplaceService._calculate_distance(latitude, longitude, item.latitude, item.longitude)
                if dist <= radius_km:
                    filtered.append(item)
            return filtered
            
        return listings

    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        # Haversine formula
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
