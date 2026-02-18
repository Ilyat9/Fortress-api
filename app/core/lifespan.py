"""
Application Lifespan Management
===============================

Manages application startup and shutdown events using FastAPI lifespan.

This module handles:
- Database connection pool initialization
- Redis connection pool initialization
- Metrics collection start
- Graceful shutdown of resources
"""

import asyncio
import logging
import redis.asyncio as redis

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import db_settings, redis_settings
from app.core.logging import get_logger
from app.core.metrics import (
    db_connections_active,
    db_connections_idle,
    cache_operations_in_progress,
)

logger = get_logger(__name__)

# Create database engine
engine = create_async_engine(
    db_settings.database_url,
    pool_size=db_settings.pool_size,
    max_overflow=db_settings.max_overflow,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Global Redis connection pool
redis_pool: redis.ConnectionPool | None = None


async def get_redis_pool() -> redis.ConnectionPool:
    """
    Get or create global Redis connection pool.

    Returns:
        Redis connection pool
    """
    global redis_pool

    if redis_pool is None:
        logger.info("Initializing Redis connection pool")
        redis_pool = redis.ConnectionPool.from_url(
            redis_settings.redis_url,
            max_connections=redis_settings.pool_size,
            decode_responses=True,
        )
        logger.info("Redis connection pool initialized")

    return redis_pool


async def startup_event() -> None:
    """
    Application startup event handler.

    Initializes:
    - Database engine
    - Redis connection pool
    - Metrics collection
    """
    logger.info("Starting application startup sequence")

    try:
        # Test database connection
        logger.info("Testing database connection")
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        # Get Redis pool
        await get_redis_pool()

        # Update metrics
        db_connections_active.set(0)
        db_connections_idle.set(db_settings.pool_size)

        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        raise


async def shutdown_event() -> None:
    """
    Application shutdown event handler.

    Closes:
    - Database engine
    - Redis connection pool
    """
    logger.info("Starting application shutdown sequence")

    try:
        # Close Redis pool
        global redis_pool
        if redis_pool:
            await redis_pool.close()
            redis_pool = None
            logger.info("Redis connection pool closed")

        # Dispose database engine
        await engine.dispose()
        logger.info("Database engine disposed")

        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error("Application shutdown failed", error=str(e))
        raise

