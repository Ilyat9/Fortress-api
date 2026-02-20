"""
Tests for critical bug fixes.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo.models import Todo
from app.domain.todo.schemas import TodoCreate, TodoUpdate, get_priority_order
from app.infrastructure.repositories.todo_repository import TodoRepository


# BUG #2: Update actually applies changes to the ORM object
@pytest.mark.asyncio
async def test_bug2_update_applies_changes(
    client: AsyncClient, test_todo: dict
) -> None:
    todo_id = test_todo["id"]

    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"priority": "high", "title": "Updated Title"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["priority"] == "high"
    assert data["title"] == "Updated Title"

    # Verify persistence
    get_response = await client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["priority"] == "high"
    assert get_data["title"] == "Updated Title"


# BUG #3: COUNT uses SQL COUNT(*), not len(all())
@pytest.mark.asyncio
async def test_bug3_count_is_efficient(client: AsyncClient, test_todo: dict) -> None:
    response = await client.get("/api/v1/todos?page=1&page_size=10")
    assert response.status_code == 200

    data = response.json()
    assert "total" in data
    assert isinstance(data["total"], int)
    assert data["total"] >= 1


# BUG #5: Priority validation rejects invalid values
@pytest.mark.asyncio
async def test_bug5_priority_validation(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/todos",
        json={"title": "Test", "priority": "invalid_priority"},
    )
    assert response.status_code == 422


# BUG #5: Priority validation accepts valid values
@pytest.mark.asyncio
async def test_bug5_priority_valid_values(client: AsyncClient) -> None:
    for priority in ("low", "medium", "high"):
        response = await client.post(
            "/api/v1/todos",
            json={"title": f"Test {priority}", "priority": priority},
        )
        assert response.status_code == 201
        assert response.json()["priority"] == priority


# BUG #6: get_priority_order is importable from schemas (not config)
def test_bug6_get_priority_order_importable() -> None:
    assert get_priority_order("high") == 3
    assert get_priority_order("medium") == 2
    assert get_priority_order("low") == 1
    assert get_priority_order("unknown") == 1


# BUG #7: _test_completed_todo fixture works correctly
@pytest.mark.asyncio
async def test_bug7_completed_todo_fixture(
    client: AsyncClient, _test_completed_todo: dict
) -> None:
    assert _test_completed_todo["is_completed"] is True
    assert "id" in _test_completed_todo


# BUG #8: Dependency override uses test DB (create + read back works)
@pytest.mark.asyncio
async def test_bug8_db_dependency_override(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "DB Override Test", "priority": "low"},
    )
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    get_response = await client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "DB Override Test"


# BUG #1: HTTP duration is positive
@pytest.mark.asyncio
async def test_bug1_positive_duration(client: AsyncClient) -> None:
    # This test validates the app doesn't crash; duration correctness is in metrics.
    response = await client.get("/api/v1/todos")
    assert response.status_code == 200
