from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings, is_using_postgres

class Base(DeclarativeBase):
    pass

engine_kwargs = {
    "future": True,
    "echo": settings.debug,
}
if is_using_postgres():
    engine_kwargs.update({"pool_pre_ping": True})

engine = create_async_engine(settings.db_url, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
