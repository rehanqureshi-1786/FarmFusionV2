from typing import List

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketListing
from app.schemas.marketplace import MarketListingCreate, MarketListingResponse


class MarketplaceService:
    @staticmethod
    async def create_listing(request: MarketListingCreate, db: AsyncSession) -> MarketListingResponse:
        listing = MarketListing(
            title=request.title,
            description=request.description or "",
            price=request.price,
            location=request.location or "",
        )
        db.add(listing)
        await db.commit()
        await db.refresh(listing)
        return MarketListingResponse(
            id=listing.id,
            title=listing.title,
            description=listing.description,
            price=listing.price,
            location=listing.location,
        )

    @staticmethod
    async def search_listings(query: str, db: AsyncSession) -> List[MarketListingResponse]:
        stmt = select(MarketListing).where(
            or_(MarketListing.title.ilike(f"%{query}%"), MarketListing.description.ilike(f"%{query}%"))
        )
        result = await db.execute(stmt)
        return [MarketListingResponse(id=row.id, title=row.title, description=row.description, price=row.price, location=row.location) for row in result.scalars().all()]
