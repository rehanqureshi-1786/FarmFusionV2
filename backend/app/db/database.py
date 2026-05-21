from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import get_db_url, settings

# Ensure model metadata is registered before creating tables
import app.models.user  # noqa: F401
import app.db.models  # noqa: F401

engine = create_async_engine(get_db_url(), future=True, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db() -> None:
    from app.db.base import Base as BaseModel
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
