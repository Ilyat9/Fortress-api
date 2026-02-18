"""
Test Configuration and Fixtures
================================

Provides shared fixtures and test configuration.
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.lifespan import Base
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://todo_user:todo_password@localhost:5432/todo_test_db"


# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a fresh database session for each test.

    Yields:
        AsyncSession: Test database session
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

        # Rollback all changes after test
        await session.rollback()

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(test_db_session: AsyncSession) -> AsyncGenerator:
    """
    Create a test HTTP client.

    Args:
        test_db_session: Test database session

    Yields:
        AsyncClient: Test HTTP client
    """

    # Override database session dependency
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_settings] = lambda: get_settings()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_todo(client: AsyncClient) -> dict:
    """
    Create a test todo for testing.

    Args:
        client: Test HTTP client

    Yields:
        dict: Created todo data
    """
    response = await client.post(
        "/api/v1/todos",
        json={
            "title": "Test Todo",
            "description": "This is a test todo",
            "is_completed": False,
            "priority": "medium",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def test_completed_todo(client: AsyncClient, test_todo: dict) -> dict:
    """
    Create and complete a test todo.

    Args:
        client: Test HTTP client
        test_todo: Test todo data

    Yields:
        dict: Completed todo data
    """
    todo_id = test_todo["id"]

    response = await client.patch(f"/api/v1/todos/{todo_id}/complete")
    assert response.status_code == 200

    updated_todo = response.json()
    assert updated_todo["is_completed"] is True

    return updated_todo
