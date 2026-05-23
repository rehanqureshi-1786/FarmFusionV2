"""
Redis cache utilities.
"""
import json
import pickle
from typing import Any, Optional
from datetime import timedelta

import redis.asyncio as redis

from app.core.config import settings

# Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get or create Redis connection."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


async def set_cache(
    key: str,
    value: Any,
    expire: Optional[timedelta] = None
) -> None:
    """Set value in cache."""
    r = await get_redis()
    serialized = json.dumps(value, default=str)
    await r.set(key, serialized, ex=expire)


async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    r = await get_redis()
    value = await r.get(key)
    if value:
        return json.loads(value)
    return None


async def delete_cache(key: str) -> None:
    """Delete value from cache."""
    r = await get_redis()
    await r.delete(key)


async def clear_pattern(pattern: str) -> None:
    """Clear cache by pattern."""
    r = await get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)
