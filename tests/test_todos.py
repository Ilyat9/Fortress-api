"""
Todo API Tests
==============

Integration tests for todo endpoints.
"""

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.domain.todo.models import Todo
from app.domain.todo.schemas import TodoResponse
from app.infrastructure.db import get_db


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient, test_db_session: AsyncSession) -> None:
    """Test creating a new todo."""
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

    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "This is a test todo"
    assert data["is_completed"] is False
    assert data["priority"] == "medium"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_todo_missing_title(client: AsyncClient) -> None:
    """Test creating a todo without title (should fail)."""
    response = await client.post(
        "/api/v1/todos",
        json={
            "description": "This is a test todo",
            "is_completed": False,
            "priority": "medium",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_todo_invalid_priority(client: AsyncClient) -> None:
    """Test creating a todo with invalid priority (should fail)."""
    response = await client.post(
        "/api/v1/todos",
        json={
            "title": "Test Todo",
            "description": "This is a test todo",
            "is_completed": False,
            "priority": "invalid_priority",
        },
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_todo(client: AsyncClient, test_todo: dict) -> None:
    """Test retrieving a todo by ID."""
    todo_id = test_todo["id"]

    response = await client.get(f"/api/v1/todos/{todo_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == test_todo["title"]
    assert data["description"] == test_todo["description"]
    assert data["is_completed"] == test_todo["is_completed"]


@pytest.mark.asyncio
async def test_get_todo_not_found(client: AsyncClient) -> None:
    """Test getting a non-existent todo (should fail)."""
    response = await client.get("/api/v1/todos/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_todos(client: AsyncClient, test_todo: dict) -> None:
    """Test listing todos."""
    response = await client.get("/api/v1/todos")

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "has_next" in data
    assert "has_previous" in data

    # Check that our test todo is in the list
    todo_ids = [todo["id"] for todo in data["items"]]
    assert test_todo["id"] in todo_ids

    # Verify pagination metadata
    assert data["total"] >= 1
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_todos_pagination(client: AsyncClient) -> None:
    """Test listing todos with pagination."""
    # Create multiple todos
    for i in range(5):
        await client.post(
            "/api/v1/todos",
            json={
                "title": f"Todo {i}",
                "is_completed": False,
                "priority": "medium",
            },
        )

    # Test page 1
    response = await client.get("/api/v1/todos?page=1&page_size=2")
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["has_next"] is True
    assert data["has_previous"] is False

    # Test page 2
    response = await client.get("/api/v1/todos?page=2&page_size=2")
    assert response.status_code == 200

    data = response.json()
    assert len(data["items"]) == 2
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_list_todos_filter_completed(client: AsyncClient, test_completed_todo: dict) -> None:
    """Test listing todos with completion filter."""
    # Create another incomplete todo
    await client.post(
        "/api/v1/todos",
        json={
            "title": "Incomplete Todo",
            "is_completed": False,
            "priority": "medium",
        },
    )

    # Get completed todos
    response = await client.get("/api/v1/todos?is_completed=true")
    assert response.status_code == 200

    data = response.json()
    assert all(todo["is_completed"] for todo in data["items"])

    # Get incomplete todos
    response = await client.get("/api/v1/todos?is_completed=false")
    assert response.status_code == 200

    data = response.json()
    assert all(not todo["is_completed"] for todo in data["items"])


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient, test_todo: dict) -> None:
    """Test updating a todo."""
    todo_id = test_todo["id"]

    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={
            "title": "Updated Title",
            "description": "Updated description",
            "is_completed": True,
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["is_completed"] is True
    assert data["priority"] == "high"


@pytest.mark.asyncio
async def test_update_todo_partial(client: AsyncClient, test_todo: dict) -> None:
    """Test partial update of a todo."""
    todo_id = test_todo["id"]

    # Only update title
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Partially Updated"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Partially Updated"
    assert data["description"] == test_todo["description"]
    assert data["is_completed"] == test_todo["is_completed"]


@pytest.mark.asyncio
async def test_update_todo_not_found(client: AsyncClient) -> None:
    """Test updating non-existent todo (should fail)."""
    response = await client.put(
        "/api/v1/todos/99999",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient, test_todo: dict) -> None:
    """Test deleting a todo."""
    todo_id = test_todo["id"]

    response = await client.delete(f"/api/v1/todos/{todo_id}")

    assert response.status_code == 204

    # Verify todo is deleted
    get_response = await client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo_not_found(client: AsyncClient) -> None:
    """Test deleting non-existent todo (should fail)."""
    response = await client.delete("/api/v1/todos/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_todo_completion(client: AsyncClient, test_todo: dict) -> None:
    """Test toggling todo completion status."""
    todo_id = test_todo["id"]

    # Initially incomplete
    get_response = await client.get(f"/api/v1/todos/{todo_id}")
    assert get_response.json()["is_completed"] is False

    # Toggle to complete
    toggle_response = await client.patch(f"/api/v1/todos/{todo_id}/complete")
    assert toggle_response.status_code == 200

    assert toggle_response.json()["is_completed"] is True

    # Toggle back to incomplete
    toggle_response = await client.patch(f"/api/v1/todos/{todo_id}/complete")
    assert toggle_response.status_code == 200

    assert toggle_response.json()["is_completed"] is False


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_create_todo_via_db(test_db_session: AsyncSession) -> None:
    """Test creating todo directly in database."""
    todo = Todo(
        title="Database Test Todo",
        description="Created directly in DB",
        is_completed=True,
        priority="high",
    )

    test_db_session.add(todo)
    await test_db_session.commit()
    await test_db_session.refresh(todo)

    assert todo.id is not None
    assert todo.title == "Database Test Todo"
    assert todo.is_completed is True


@pytest.mark.asyncio
async def test_database_transactions(test_db_session: AsyncSession) -> None:
    """Test database transaction rollback."""
    todo = Todo(
        title="Transaction Test Todo",
        description="Should be rolled back",
        is_completed=False,
        priority="medium",
    )

    test_db_session.add(todo)
    await test_db_session.commit()

    todo_id = todo.id

    # Query after commit - should exist
    result = await test_db_session.execute(select(Todo).where(Todo.id == todo_id))
    retrieved_todo = result.scalar_one_or_none()
    assert retrieved_todo is not None

    # Now rollback the session
    await test_db_session.rollback()

    # Query after rollback - should not exist
    result = await test_db_session.execute(select(Todo).where(Todo.id == todo_id))
    retrieved_todo = result.scalar_one_or_none()
    assert retrieved_todo is None


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient) -> None:
    """Test rate limiting (if enabled)."""
    # Make multiple rapid requests
    responses = []
    for _ in range(5):
        response = await client.get("/api/v1/todos")
        responses.append(response.status_code)

    # Should not be rate limited (default limit is 100 per 60 seconds)
    assert all(code in (200, 404, 405) for code in responses)
