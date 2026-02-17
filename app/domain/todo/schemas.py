"""
Pydantic Schemas
================

Pydantic v2 schemas for request/response validation.

These schemas are:
- Used for API request/response validation
- Independent of database models
- Can be shared between API and tests
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class TodoBase(BaseModel):
    """Base schema for Todo."""

    title: str = Field(..., min_length=1, max_length=255, description="Todo title")
    description: Optional[str] = Field(None, max_length=1000, description="Todo description")
    is_completed: bool = Field(default=False, description="Todo completion status")
    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high)$",
        description="Todo priority: low, medium, or high",
    )

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""

    model_config = ConfigDict(
        extra="forbid",
    )


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_completed: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")

    model_config = ConfigDict(
        extra="forbid",
    )


class TodoResponse(TodoBase):
    """Schema for todo response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class TodoListResponse(BaseModel):
    """Schema for paginated todo list response."""

    items: list[TodoResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str
    version: str
    timestamp: datetime

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )


# Validators for prioritization
@field_validator("priority")
@classmethod
def validate_priority(cls, v: str) -> str:
    """Validate priority is one of allowed values."""
    valid_priorities = ["low", "medium", "high"]
    if v not in valid_priorities:
        raise ValueError(f"Priority must be one of {valid_priorities}")
    return v


# Priority ordering for sorting
PRIORITY_ORDER = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


def get_priority_order(priority: str) -> int:
    """
    Get numeric priority order for sorting.

    Args:
        priority: Priority string

    Returns:
        Numeric priority order
    """
    return PRIORITY_ORDER.get(priority, 1)
