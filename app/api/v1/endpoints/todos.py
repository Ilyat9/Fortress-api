"""
Todo API Endpoints
==================

RESTful endpoints for todo operations.

Each endpoint:
- Uses FastAPI dependency injection
- Records metrics
- Includes tracing
- Returns structured responses
"""


from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import record_http_request_end, record_http_request_start
from app.core.tracing import get_tracer
from app.domain.todo.schemas import (
    HealthResponse,
    TodoCreate,
    TodoListResponse,
    TodoResponse,
    TodoUpdate,
)
from app.infrastructure.db import get_db
from app.services.todo_service import TodoService

logger = get_logger(__name__)
router = APIRouter(prefix="/todos", tags=["todos"])
tracer = get_tracer()


@router.get("/", response_model=TodoListResponse)
async def list_todos(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    is_completed: bool | None = Query(None, description="Filter by completion status"),
    priority: str | None = Query(
        None, regex="^(low|medium|high)$", description="Filter by priority"
    ),
    session: AsyncSession = Depends(get_db),
) -> TodoListResponse:
    """
    Get all todos with pagination and filtering.

    Query Parameters:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        sort_by: Field to sort by (default: created_at)
        order: Sort order (default: desc)
        is_completed: Filter by completion status
        priority: Filter by priority (low, medium, high)

    Returns:
        Paginated list of todos
    """
    logger.info("Fetching todos list", page=page, page_size=page_size)
    start_time = record_http_request_start("GET", "/api/v1/todos")

    try:
        with tracer.start_as_current_span("list_todos", kind="server") as span:
            span.set_attribute("page", page)
            span.set_attribute("page_size", page_size)
            span.set_attribute("sort_by", sort_by)
            span.set_attribute("order", order)

            service = TodoService(session)
            todos, total = await service.get_todos(
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                order=order,
                is_completed=is_completed,
                priority=priority,
            )

            has_next = (page * page_size) < total
            has_previous = page > 1

            response = TodoListResponse(
                items=todos,
                total=total,
                page=page,
                page_size=page_size,
                has_next=has_next,
                has_previous=has_previous,
            )

            duration = (datetime.now() - start_time).total_seconds()
            record_http_request_end("GET", "/api/v1/todos", status.HTTP_200_OK, duration)

            logger.info("Todos fetched successfully", total=total)

            return response

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_http_request_end(
            "GET", "/api/v1/todos", status.HTTP_500_INTERNAL_SERVER_ERROR, duration
        )

        logger.error("Failed to fetch todos", error=str(e))
        raise


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_db),
) -> TodoResponse:
    """
    Get a specific todo by ID.

    Path Parameters:
        todo_id: Todo ID

    Returns:
        Todo entity
    """
    logger.info("Fetching todo", todo_id=todo_id)

    start_time = record_http_request_start("GET", "/api/v1/todos/{todo_id}")

    try:
        with tracer.start_as_current_span("get_todo", kind="server") as span:
            span.set_attribute("todo_id", todo_id)

            service = TodoService(session)
            todo = await service.get_todo(todo_id)

            if not todo:
                duration = (datetime.now() - start_time).total_seconds()
                record_http_request_end(
                    "GET", "/api/v1/todos/{todo_id}", status.HTTP_404_NOT_FOUND, duration
                )

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

            duration = (datetime.now() - start_time).total_seconds()
            record_http_request_end("GET", "/api/v1/todos/{todo_id}", status.HTTP_200_OK, duration)

            logger.info("Todo fetched successfully", todo_id=todo_id)

            return todo

    except HTTPException:
        raise
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_http_request_end(
            "GET", "/api/v1/todos/{todo_id}", status.HTTP_500_INTERNAL_SERVER_ERROR, duration
        )

        logger.error("Failed to fetch todo", todo_id=todo_id, error=str(e))
        raise


@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_data: TodoCreate,
    session: AsyncSession = Depends(get_db),
) -> TodoResponse:
    """
    Create a new todo.

    Request Body:
        title: Todo title (required)
        description: Todo description (optional, max 1000 chars)
        is_completed: Initial completion status (default: false)
        priority: Priority level (default: medium) - low, medium, high

    Returns:
        Created todo entity
    """
    logger.info("Creating todo", title=todo_data.title)

    start_time = record_http_request_start("POST", "/api/v1/todos")

    try:
        with tracer.start_as_current_span("create_todo", kind="server") as span:
            span.set_attribute("title", todo_data.title)
            span.set_attribute("priority", todo_data.priority)

            service = TodoService(session)
            todo = await service.create_todo(todo_data)

            duration = (datetime.now() - start_time).total_seconds()
            record_http_request_end("POST", "/api/v1/todos", status.HTTP_201_CREATED, duration)

            logger.info("Todo created successfully", todo_id=todo.id)

            return todo

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_http_request_end(
            "POST", "/api/v1/todos", status.HTTP_500_INTERNAL_SERVER_ERROR, duration
        )

        logger.error("Failed to create todo", error=str(e))
        raise


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    session: AsyncSession = Depends(get_db),
) -> TodoResponse:
    """
    Update a todo.

    Path Parameters:
        todo_id: Todo ID

    Request Body:
        title: New todo title (optional)
        description: New todo description (optional)
        is_completed: New completion status (optional)
        priority: New priority level (optional)

    Returns:
        Updated todo entity
    """
    logger.info("Updating todo", todo_id=todo_id)

    start_time = record_http_request_start("PUT", "/api/v1/todos/{todo_id}")

    try:
        with tracer.start_as_current_span("update_todo", kind="server") as span:
            span.set_attribute("todo_id", todo_id)

            service = TodoService(session)
            updated_todo = await service.update_todo(todo_id, todo_data)

            if not updated_todo:
                duration = (datetime.now() - start_time).total_seconds()
                record_http_request_end(
                    "PUT", "/api/v1/todos/{todo_id}", status.HTTP_404_NOT_FOUND, duration
                )

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

            duration = (datetime.now() - start_time).total_seconds()
            record_http_request_end("PUT", "/api/v1/todos/{todo_id}", status.HTTP_200_OK, duration)

            logger.info("Todo updated successfully", todo_id=todo_id)

            return updated_todo

    except HTTPException:
        raise
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_http_request_end(
            "PUT", "/api/v1/todos/{todo_id}", status.HTTP_500_INTERNAL_SERVER_ERROR, duration
        )

        logger.error("Failed to update todo", todo_id=todo_id, error=str(e))
        raise


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a todo.

    Path Parameters:
        todo_id: Todo ID

    Returns:
        204 No Content on success
    """
    logger.info("Deleting todo", todo_id=todo_id)

    start_time = record_http_request_start("DELETE", "/api/v1/todos/{todo_id}")

    try:
        with tracer.start_as_current_span("delete_todo", kind="server") as span:
            span.set_attribute("todo_id", todo_id)

            service = TodoService(session)
            deleted = await service.delete_todo(todo_id)

            if not deleted:
                duration = (datetime.now() - start_time).total_seconds()
                record_http_request_end(
                    "DELETE", "/api/v1/todos/{todo_id}", status.HTTP_404_NOT_FOUND, duration
                )

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

            duration = (datetime.now() - start_time).total_seconds()
            record_http_request_end(
                "DELETE", "/api/v1/todos/{todo_id}", status.HTTP_204_NO_CONTENT, duration
            )

            logger.info("Todo deleted successfully", todo_id=todo_id)

    except HTTPException:
        raise
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_http_request_end(
            "DELETE", "/api/v1/todos/{todo_id}", status.HTTP_500_INTERNAL_SERVER_ERROR, duration
        )

        logger.error("Failed to delete todo", todo_id=todo_id, error=str(e))
        raise


@router.patch("/{todo_id}/complete", response_model=TodoResponse)
async def toggle_todo_completion(
    todo_id: int,
    session: AsyncSession = Depends(get_db),
) -> TodoResponse:
    """
    Toggle todo completion status.

    Path Parameters:
        todo_id: Todo ID

    Returns:
        Updated todo entity with new completion status
    """
    logger.info("Toggling todo completion", todo_id=todo_id)

    start_time = record_http_request_start("PATCH", "/api/v1/todos/{todo_id}/complete")

    try:
        with tracer.start_as_current_span("toggle_todo_completion", kind="server") as span:
            span.set_attribute("todo_id", todo_id)

            service = TodoService(session)
            updated_todo = await service.toggle_todo_completion(todo_id)

            if not updated_todo:
                duration = (datetime.now() - start_time).total_seconds()
                record_http_request_end(
                    "PATCH", "/api/v1/todos/{todo_id}/complete", status.HTTP_404_NOT_FOUND, duration
                )

                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

            duration = (datetime.now() - start_time).total_seconds()
            record_http_request_end(
                "PATCH", "/api/v1/todos/{todo_id}/complete", status.HTTP_200_OK, duration
            )

            logger.info(
                "Todo completion toggled successfully",
                todo_id=todo_id,
                is_completed=updated_todo.is_completed,
            )

            return updated_todo

    except HTTPException:
        raise
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        record_http_request_end(
            "PATCH",
            "/api/v1/todos/{todo_id}/complete",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            duration,
        )

        logger.error(
            "Failed to toggle todo completion", todo_id=todo_id, error=str(e)
        )
        raise