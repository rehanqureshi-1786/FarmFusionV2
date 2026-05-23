"""Database base class and utilities."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings, is_using_postgres


class Base(DeclarativeBase):
    pass


# Create engine with database-specific configuration
engine_kwargs = {
    "echo": settings.debug,
    "future": True,
}

# Only add pool configuration for PostgreSQL
if is_using_postgres():
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 0,
    })

engine = create_async_engine(
    settings.effective_async_database_url,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
