from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime
import math
from app.db.models import MarketListing
from app.models.user import User
from app.schemas.marketplace import MarketListingCreate, MarketListingUpdate

class MarketplaceService:
    @staticmethod
    async def create_listing(db: AsyncSession, user_id: Optional[int], listing: MarketListingCreate):
        actual_user_id = None
        if user_id is not None:
            user_check = await db.execute(select(User).where(User.id == user_id))
            if user_check.scalar_one_or_none():
                actual_user_id = user_id
            else:
                first_user = await db.execute(select(User).limit(1))
                u = first_user.scalar_one_or_none()
                if u:
                    actual_user_id = u.id

        data = listing.model_dump()
        if "is_active" not in data or data["is_active"] is None:
            data["is_active"] = True

        if not data.get("price_per_unit"):
            c = (data.get("crop_name") or "").lower()
            if "wheat" in c:
                data["price_per_unit"] = 2200.0
            elif "rice" in c or "paddy" in c:
                data["price_per_unit"] = 2800.0
            elif "onion" in c:
                data["price_per_unit"] = 1600.0
            elif "soybean" in c or "soya" in c:
                data["price_per_unit"] = 4300.0
            elif "mustard" in c:
                data["price_per_unit"] = 5400.0
            elif "cotton" in c:
                data["price_per_unit"] = 6800.0
            elif "potato" in c:
                data["price_per_unit"] = 1400.0
            elif "tomato" in c:
                data["price_per_unit"] = 1800.0
            else:
                data["price_per_unit"] = 2100.0

        db_listing = MarketListing(
            **data,
            user_id=actual_user_id
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
        radius_km: float = 50.0,
        user_id: Optional[int] = None,
        active_only: bool = False
    ):
        query = select(MarketListing)
        
        if active_only:
            query = query.where(MarketListing.is_active == True)
        if user_id is not None:
            query = query.where(MarketListing.user_id == user_id)
        if crop_filter:
            query = query.where(MarketListing.crop_name.ilike(f"%{crop_filter}%"))
            
        query = query.order_by(MarketListing.created_at.desc())
        result = await db.execute(query)
        listings = list(result.scalars().all())


        
        if latitude is not None and longitude is not None:
            filtered = []
            for item in listings:
                if item.latitude is not None and item.longitude is not None:
                    dist = MarketplaceService._calculate_distance(latitude, longitude, item.latitude, item.longitude)
                    if dist <= radius_km:
                        filtered.append(item)
                else:
                    filtered.append(item)
            return filtered
            
        return listings

    @staticmethod
    async def delete_listing(db: AsyncSession, listing_id: int) -> bool:
        query = select(MarketListing).where(MarketListing.id == listing_id)
        result = await db.execute(query)
        listing = result.scalar_one_or_none()
        if not listing:
            return False
        await db.delete(listing)
        await db.commit()
        return True

    @staticmethod
    async def toggle_listing_status(db: AsyncSession, listing_id: int, is_active: bool) -> Optional[MarketListing]:
        query = select(MarketListing).where(MarketListing.id == listing_id)
        result = await db.execute(query)
        listing = result.scalar_one_or_none()
        if not listing:
            return None
        listing.is_active = is_active
        await db.commit()
        await db.refresh(listing)
        return listing

    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        # Haversine formula
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
