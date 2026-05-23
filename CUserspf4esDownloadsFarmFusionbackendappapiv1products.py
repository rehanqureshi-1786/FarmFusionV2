"""
Product store and marketplace API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.api.deps import get_db, get_current_user
from app.models.product import Product, Order, OrderStatus, ProductCategory
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Product Store"])


@router.get("/")
async def get_products(
    category: ProductCategory = None,
    state: str = Query(None),
    search: str = Query(None),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get products with filters."""
    query = select(Product).where(Product.is_active == True)
    
    if category:
        query = query.where(Product.category == category)
    if state:
        query = query.where(Product.state.ilike(f"%{state}%"))
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if min_price:
        query = query.where(Product.price >= min_price)
    if max_price:
        query = query.where(Product.price <= max_price)
    
    query = query.order_by(desc(Product.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "items": products,
        "page": skip // limit + 1,
        "limit": limit
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product listing."""
    product = Product(
        seller_id=current_user.id,
        **product_data
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product."""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.post("/{product_id}/order", status_code=status.HTTP_201_CREATED)
async def create_order(
    product_id: int,
    order_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Place an order for a product."""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock_quantity < order_data.get("quantity", 1):
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    order = Order(
        buyer_id=current_user.id,
        total_amount=product.price * order_data.get("quantity", 1),
        **order_data
    )
    
    product.stock_quantity -= order_data.get("quantity", 1)
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return order


@router.get("/orders/my")
async def get_my_orders(
    status: OrderStatus = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's orders."""
    query = select(Order).where(Order.buyer_id == current_user.id)
    
    if status:
        query = query.where(Order.status == status)
    
    result = await db.execute(query.order_by(desc(Order.created_at)))
    return result.scalars().all()
