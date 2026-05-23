from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db import get_db
from app.services.store_service import StoreService
from app.schemas.store import StoreProductResponse

router = APIRouter(prefix="/store", tags=["store"])

@router.get("/products", response_model=List[StoreProductResponse])
async def get_products(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await StoreService.get_products(db, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed")
async def seed_store(db: AsyncSession = Depends(get_db)):
    """Seed the store with initial stock"""
    try:
        await StoreService.populate_initial_stock(db)
        return {"success": True, "message": "Initial stock added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
