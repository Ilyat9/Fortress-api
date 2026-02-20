"""
Database Infrastructure
======================

Database connection and session management.

Provides:
- Database engine initialization
- Session management
- Model registration
"""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.lifespan import async_session_maker, engine
from app.infrastructure.database import Base


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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    Commits on success, rolls back on any exception.

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
