from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import StoreProduct
from app.schemas.store import StoreProductCreate, StoreProductResponse


class StoreService:
    @staticmethod
    async def get_products(db: AsyncSession) -> List[StoreProductResponse]:
        result = await db.execute(select(StoreProduct).limit(50))
        return [StoreProductResponse(id=product.id, name=product.name, description=product.description, price=product.price, available=product.available, created_at=product.created_at) for product in result.scalars().all()]

    @staticmethod
    async def seed_store(db: AsyncSession) -> dict:
        products = [
            StoreProduct(name="Fertilizer", description="Balanced fertilizer", price=500.0),
            StoreProduct(name="Seed Pack", description="Certified seed pack", price=250.0),
        ]
        db.add_all(products)
        await db.commit()
        return {"seeded": len(products)}
