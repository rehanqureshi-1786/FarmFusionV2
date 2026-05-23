from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.db.models import StoreProduct
from app.schemas.store import StoreProductCreate

class StoreService:
    @staticmethod
    async def get_products(db: AsyncSession, category: Optional[str] = None):
        query = select(StoreProduct)
        if category:
            query = query.where(StoreProduct.category == category)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_product(db: AsyncSession, product_data: StoreProductCreate):
        db_product = StoreProduct(**product_data.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product

    @staticmethod
    async def populate_initial_stock(db: AsyncSession):
        """Seed the store with initial mock inventory"""
        initial_products = [
            {"name": "Premium Wheat Seeds", "category": "Seeds", "price": 1200, "stock_quantity": 50, "unit": "10kg Bag", "description": "High yield variety"},
            {"name": "Organic MPK Fertilizer", "category": "Fertilizer", "price": 850, "stock_quantity": 100, "unit": "50kg Bag", "description": "Rich in Nitrogen and Phos"},
            {"name": "Handheld Seeder Tool", "category": "Tools", "price": 2500, "stock_quantity": 15, "unit": "Unit", "description": "Ergonomic design for small farms"},
            {"name": "Neem Oil Bio-Pesticide", "category": "Pesticides", "price": 450, "stock_quantity": 40, "unit": "1L Bottle", "description": "Natural pest control"}
        ]
        
        for p in initial_products:
            # Check if exists
            exists = await db.execute(select(StoreProduct).where(StoreProduct.name == p["name"]))
            if not exists.scalars().first():
                db.add(StoreProduct(**p))
        
        await db.commit()
