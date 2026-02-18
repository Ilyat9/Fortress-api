"""
Todo Service
============

Business logic layer for Todo entity.

The service layer:
- Orchestrates business operations
- Implements business rules
- Coordinates between domain and infrastructure
- Handles transactions
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_priority_order
from app.core.logging import get_logger
from app.core.metrics import (
    business_operations_duration_seconds,
    todos_completed_total,
    todos_created_total,
    todos_deleted_total,
    todos_updated_total,
)
from app.domain.todo.models import Todo
from app.domain.todo.schemas import TodoCreate, TodoUpdate
from app.infrastructure.repositories.todo_repository import TodoRepository

logger = get_logger(__name__)


class TodoService:
    """Service for Todo operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize service.

        Args:
            session: Database session
        """
        self.session = session
        self.repository = TodoRepository(session, cache_enabled=True)

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
        """
        Create a new todo.

        Args:
            todo_data: Todo creation data

        Returns:
            Created Todo entity
        """
        start_time = datetime.now()

        logger.info(f"Creating todo: {todo_data.title}")

        with business_operations_duration_seconds.labels(operation="create_todo").time():
            # Validate priority order
            priority_order = get_priority_order(todo_data.priority)
            logger.debug(f"Priority order for '{todo_data.priority}': {priority_order}")

            # Create todo using repository
            todo_dict = todo_data.model_dump(exclude_unset=True)
            todo = await self.repository.create(todo_dict)

            # Record metric
            todos_created_total.inc()

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Todo created successfully in {duration:.3f}s",
                todo_id=todo.id,
                priority=todo.priority,
            )

            return todo

    async def get_todo(self, todo_id: int) -> Todo | None:
        """
        Get todo by ID.

        Args:
            todo_id: Todo ID

        Returns:
            Todo entity or None
        """
        start_time = datetime.now()

        logger.debug(f"Getting todo: {todo_id}")

        with business_operations_duration_seconds.labels(operation="get_todo").time():
            todo = await self.repository.get_by_id(todo_id)

            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Todo retrieved in {duration:.3f}s", todo_id=todo_id)

            return todo

    async def get_todos(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        is_completed: bool | None = None,
        priority: str | None = None,
    ) -> tuple[list[Todo], int]:
        """
        Get all todos with filtering and pagination.

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
        start_time = datetime.now()

        logger.info(
            "Fetching todos",
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order,
            is_completed=is_completed,
            priority=priority,
        )

        with business_operations_duration_seconds.labels(operation="get_todos").time():
            todos, total = await self.repository.get_all(
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                order=order,
                is_completed=is_completed,
                priority=priority,
            )

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Todos fetched successfully in {duration:.3f}s",
                total=total,
                returned=len(todos),
            )

            return todos, total

    async def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> Todo | None:
        """
        Update todo.

        Args:
            todo_id: Todo ID
            todo_data: Update data

        Returns:
            Updated Todo entity or None
        """
        start_time = datetime.now()

        logger.info(f"Updating todo: {todo_id}")

        with business_operations_duration_seconds.labels(operation="update_todo").time():
            todo_dict = todo_data.model_dump(exclude_unset=True)
            updated_todo = await self.repository.update(todo_id, todo_dict)

            if updated_todo:
                todos_updated_total.inc()

                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Todo updated successfully in {duration:.3f}s",
                    todo_id=todo_id,
                )

            return updated_todo

    async def delete_todo(self, todo_id: int) -> bool:
        """
        Delete todo.

        Args:
            todo_id: Todo ID

        Returns:
            True if deleted
        """
        start_time = datetime.now()

        logger.info(f"Deleting todo: {todo_id}")

        with business_operations_duration_seconds.labels(operation="delete_todo").time():
            deleted = await self.repository.delete(todo_id)

            if deleted:
                todos_deleted_total.inc()

                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"Todo deleted successfully in {duration:.3f}s", todo_id=todo_id)

            return deleted

    async def toggle_todo_completion(self, todo_id: int) -> Todo | None:
        """
        Toggle todo completion status.

        Args:
            todo_id: Todo ID

        Returns:
            Updated Todo entity or None
        """
        start_time = datetime.now()

        logger.info(f"Toggling todo completion: {todo_id}")

        with business_operations_duration_seconds.labels(operation="toggle_completion").time():
            todo = await self.repository.get_by_id(todo_id)
            if not todo:
                return None

            # Toggle status
            new_status = not todo.is_completed
            updated_todo = await self.repository.update_status(todo_id, new_status)

            if updated_todo:
                if new_status:
                    todos_completed_total.inc()
                    logger.info(f"Todo marked as completed: {todo_id}")
                else:
                    logger.info(f"Todo marked as incomplete: {todo_id}")

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Todo completion toggled successfully in {duration:.3f}s",
                todo_id=todo_id,
                new_status=new_status,
            )

            return updated_todo
