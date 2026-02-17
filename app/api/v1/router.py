"""
API v1 Router
=============

Registers all v1 API routes.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import todos

api_router = APIRouter()

# Include todo endpoints
api_router.include_router(todos.router)
