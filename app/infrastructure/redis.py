"""
Redis Infrastructure
====================

Redis connection and client management.

Provides:
- Connection pool management
- Cache operations
- Redis client helper functions
"""

import json
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import redis_settings
from app.core.logging import get_logger
from app.core.metrics import (
    cache_hits_total,
    cache_misses_total,
    cache_operations_in_progress,
    cache_set_duration_seconds,
)

logger = get_logger(__name__)

# Global Redis client instance
redis_client: Redis | None = None


async def get_redis() -> Redis:
    """
    Get or create global Redis client.

    Returns:
        Redis client instance
    """
    global redis_client

    if redis_client is None:
        pool = await get_redis_pool()
        redis_client = redis.Redis(connection_pool=pool)
        logger.info("Redis client initialized")

    return redis_client


async def get_redis_pool() -> redis.ConnectionPool:
    """
    Get or create Redis connection pool.

    Returns:
        Redis connection pool
    """
    from app.core.lifespan import get_redis_pool as lifespan_get_pool

    return await lifespan_get_pool()


async def close_redis() -> None:
    """Close Redis client and connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis client closed")


def get_key(key: str, prefix: str = "todo") -> str:
    """
    Generate cache key with prefix.

    Args:
        key: Cache key
        prefix: Key prefix

    Returns:
        Full cache key
    """
    return f"{prefix}:{key}"


async def get(key: str, prefix: str = "todo") -> Any | None:
    """
    Get value from cache.

    Args:
        key: Cache key
        prefix: Key prefix

    Returns:
        Cached value or None
    """
    global redis_client

    cache_key = get_key(key, prefix)

    cache_operations_in_progress.labels(operation="get").inc()

    try:
        value = await redis_client.get(cache_key)
        cache_operations_in_progress.labels(operation="get").dec()

        if value:
            record_cache_hit()
            logger.debug(f"Cache hit for key: {cache_key}")
            return json.loads(value)

        record_cache_miss()
        logger.debug(f"Cache miss for key: {cache_key}")
        return None

    except Exception as e:
        cache_operations_in_progress.labels(operation="get").dec()
        logger.error(f"Cache get error for key {cache_key}: {e}")
        return None


async def set(key: str, value: Any, prefix: str = "todo", ttl: int = 3600) -> bool:
    """
    Set value in cache.

    Args:
        key: Cache key
        value: Value to cache
        prefix: Key prefix
        ttl: Time to live in seconds

    Returns:
        True if successful
    """
    global redis_client

    cache_key = get_key(key, prefix)

    cache_operations_in_progress.labels(operation="set").inc()

    try:
        serialized_value = json.dumps(value)
        await redis_client.setex(cache_key, ttl, serialized_value)
        cache_operations_in_progress.labels(operation="set").dec()

        logger.debug(f"Cache set for key: {cache_key}, TTL: {ttl}s")
        return True

    except Exception as e:
        cache_operations_in_progress.labels(operation="set").dec()
        logger.error(f"Cache set error for key {cache_key}: {e}")
        return False


async def delete(key: str, prefix: str = "todo") -> bool:
    """
    Delete value from cache.

    Args:
        key: Cache key
        prefix: Key prefix

    Returns:
        True if successful
    """
    global redis_client

    cache_key = get_key(key, prefix)

    try:
        await redis_client.delete(cache_key)
        logger.debug(f"Cache delete for key: {cache_key}")
        return True

    except Exception as e:
        logger.error(f"Cache delete error for key {cache_key}: {e}")
        return False


async def exists(key: str, prefix: str = "todo") -> bool:
    """
    Check if key exists in cache.

    Args:
        key: Cache key
        prefix: Key prefix

    Returns:
        True if key exists
    """
    cache_key = get_key(key, prefix)

    try:
        exists = await redis_client.exists(cache_key)
        return exists > 0

    except Exception as e:
        logger.error(f"Cache exists error for key {cache_key}: {e}")
        return False


async def clear_pattern(pattern: str) -> int:
    """
    Clear all keys matching a pattern.

    Args:
        pattern: Redis pattern (e.g., "todo:*")

    Returns:
        Number of keys deleted
    """
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            deleted = await redis_client.delete(*keys)
            logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
            return deleted
        return 0

    except Exception as e:
        logger.error(f"Error clearing pattern {pattern}: {e}")
        return 0
