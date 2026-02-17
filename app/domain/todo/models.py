"""
Domain Models
=============

Domain entities representing business concepts.
These are pure business objects without infrastructure dependencies.

This layer contains:
- Domain entities
- Business rules
- Domain-specific validation
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Boolean, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.lifespan import Base


class Todo(Base):
    """
    Todo domain entity.

    Represents a todo item in the domain model.
    """

    __tablename__ = "todos"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Business attributes
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # User relationship can be added if needed

    def to_dict(self) -> dict[str, Any]:
        """
        Convert entity to dictionary representation.

        Returns:
            Dictionary representation of the entity
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_completed": self.is_completed,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update(self, **kwargs: Any) -> None:
        """
        Update entity attributes.

        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
