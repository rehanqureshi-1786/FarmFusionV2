from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.store_service import StoreService

router = APIRouter(prefix="/store", tags=["store"])


@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    return await StoreService.get_products(db)


@router.post("/seed")
async def seed_store(db: AsyncSession = Depends(get_db)):
    return await StoreService.seed_store(db)
