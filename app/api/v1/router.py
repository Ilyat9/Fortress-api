"""
API v1 Router
=============

Registers all v1 API routes.
"""

from datetime import datetime

from fastapi import APIRouter

from app.api.v1.endpoints import todos
from app.core.config import settings
from app.domain.todo.schemas import HealthResponse

api_router = APIRouter()

# Include todo endpoints
api_router.include_router(todos.router)


@api_router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint at /api/v1/health.

    Returns application status and version.
    Does not touch the database — safe for liveness probes.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(),
    )