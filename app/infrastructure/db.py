"""
Database Infrastructure
======================

Database connection and session management.

Provides:
- Database engine initialization
- Session management
- Model registration
"""

from typing import AsyncGenerator

from app.core.config import db_settings
from app.core.lifespan import engine, async_session_maker
from app.domain.todo.models import Base as TodoBase

from sqlalchemy import text


async def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in the Base metadata.
    Use this in application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully")


async def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This deletes all data! Use with caution.
    Use this for testing only.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Database tables dropped successfully")


async def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        True if connection is successful
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


async def get_db() -> AsyncGenerator:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        yield session
