"""
Todo Repository
===============

Data access layer for Todo entity.

This repository:
- Implements data access patterns
- Separates business logic from data access
- Provides caching support
- Uses ORM patterns
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Select, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_priority_order
from app.core.metrics import record_db_query
from app.core.logging import get_logger
from app.domain.todo.models import Todo
from app.infrastructure.redis import get, set

logger = get_logger(__name__)


class TodoRepository:
    """Repository for Todo entity."""

    def __init__(self, session: AsyncSession, cache_enabled: bool = True):
        """
        Initialize repository.

        Args:
            session: Database session
            cache_enabled: Enable caching for this repository
        """
        self.session = session
        self.cache_enabled = cache_enabled

    async def get_by_id(self, id: int) -> Todo | None:
        """
        Get todo by ID.

        Args:
            id: Todo ID

        Returns:
            Todo entity or None
        """
        cache_key = f"todo:{id}"

        # Try cache first
        if self.cache_enabled:
            cached = await get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for todo {id}")
                return cached

        logger.debug(f"Cache miss for todo {id}, querying database")

        # Query database
        result = await self.session.execute(select(Todo).where(Todo.id == id))
        todo = result.scalar_one_or_none()

        # Cache result
        if todo:
            await set(cache_key, todo.to_dict(), ttl=300)  # 5 minutes

        return todo

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        is_completed: bool | None = None,
        priority: str | None = None,
    ) -> tuple[list[Todo], int]:
        """
        Get all todos with pagination and filtering.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            sort_by: Field to sort by
            order: Sort order (asc or desc)
            is_completed: Filter by completion status
            priority: Filter by priority

        Returns:
            Tuple of (todos list, total count)
        """
        query = select(Todo)

        # Apply filters
        if is_completed is not None:
            query = query.where(Todo.is_completed == is_completed)

        if priority:
            query = query.where(Todo.priority == priority)

        # Apply ordering
        if sort_by == "priority":
            query = query.order_by(asc(Todo.priority) if order == "asc" else desc(Todo.priority))
        elif sort_by in ("created_at", "updated_at"):
            query = query.order_by(asc(getattr(Todo, sort_by)) if order == "asc" else desc(getattr(Todo, sort_by)))
        else:
            # Default sort by created_at descending
            query = query.order_by(desc(Todo.created_at))

        # Get total count
        count_query = select(Todo.id).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = len(total_result.all())

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        start_time = datetime.now()
        result = await self.session.execute(query)
        todos = result.scalars().all()
        duration = (datetime.now() - start_time).total_seconds()

        # Record metrics
        record_db_query("SELECT", "todos", duration)

        return list(todos), total

    async def create(self, todo_data: dict[str, Any]) -> Todo:
        """
        Create a new todo.

        Args:
            todo_data: Todo data dictionary

        Returns:
            Created Todo entity
        """
        todo = Todo(**todo_data)

        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)

        # Clear cache for affected items
        await self.clear_cache()

        logger.info(f"Created todo with ID: {todo.id}")
        return todo

    async def update(self, id: int, todo_data: dict[str, Any]) -> Todo | None:
        """
        Update todo by ID.

        Args:
            id: Todo ID
            todo_data: Update data dictionary

        Returns:
            Updated Todo entity or None
        """
        todo = await self.get_by_id(id)
        if not todo:
            return None

        # Apply updates
        update_data = {}
        for key, value in todo_data.items():
            if hasattr(todo, key) and key != "id":
                update_data[key] = value

        if update_data:
            await self.session.commit()
            todo.updated_at = datetime.now()

            # Clear cache for updated item
            await self.clear_cache()

            logger.info(f"Updated todo with ID: {id}")
            return todo

        return todo

    async def delete(self, id: int) -> bool:
        """
        Delete todo by ID.

        Args:
            id: Todo ID

        Returns:
            True if deleted
        """
        todo = await self.get_by_id(id)
        if not todo:
            return False

        await self.session.delete(todo)
        await self.session.commit()

        # Clear cache for deleted item
        await self.clear_cache()

        logger.info(f"Deleted todo with ID: {id}")
        return True

    async def update_status(self, id: int, is_completed: bool) -> Todo | None:
        """
        Update todo completion status.

        Args:
            id: Todo ID
            is_completed: New completion status

        Returns:
            Updated Todo entity or None
        """
        todo = await self.get_by_id(id)
        if not todo:
            return None

        todo.is_completed = is_completed
        todo.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(todo)

        # Clear cache
        await self.clear_cache()

        logger.info(f"Updated todo status: {id} -> {is_completed}")
        return todo

    async def clear_cache(self) -> None:
        """Clear all todo-related cache."""
        await clear_pattern("todo:*")
        logger.debug("Cleared todo cache")


# Cache helper function
async def clear_pattern(pattern: str) -> int:
    """
    Clear all keys matching a pattern.

    Args:
        pattern: Redis pattern

    Returns:
        Number of keys deleted
    """
    from app.infrastructure.redis import clear_pattern as redis_clear_pattern

    return await redis_clear_pattern(pattern)
