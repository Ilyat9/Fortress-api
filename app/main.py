"""
Application Entry Point
======================

FastAPI application initialization and configuration.

This module:
- Sets up the FastAPI application
- Configures middleware
- Sets up routing
- Initializes observability
- Manages application lifecycle
"""

import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import generate_latest
from app.infrastructure.database import Base
from app.infrastructure.db import engine
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.lifespan import shutdown_event, startup_event
from app.core.logging import setup_logging
from app.core.metrics import record_http_request

# Initialize logging
setup_logging()

logger = structlog.get_logger(__name__)


# Lifespan context manager
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    logger.info("Starting application lifespan")

    logger.info("Creating database tables if they don't exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Startup
    await startup_event()
    yield

    # Shutdown
    await shutdown_event()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Production-Ready Todo API with FastAPI, PostgreSQL, Redis, and Full Observability",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Metrics endpoint
@app.get(settings.metrics_path)
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns Prometheus-formatted metrics.

    Returns:
        Prometheus metrics
    """
    logger.debug("Metrics request received")
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4",
        headers={"Content-Type": "text/plain; version=0.0.4"},
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """
    Log all HTTP requests.

    Args:
        request: HTTP request
        call_next: Next middleware in chain

    Returns:
        HTTP response
    """
    request_id = request.headers.get("X-Request-ID", str(time.time()))

    logger.info(
        "Request started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    start_time = time.time()

    try:
        response = await call_next(request)

        duration = time.time() - start_time
        status_code = response.status_code

        logger.info(
            "Request completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration=f"{duration:.3f}s",
        )

        # Record metrics
        record_http_request(request.method, request.url.path, status_code, duration)

        return response

    except Exception as e:
        duration = time.time() - start_time

        logger.error(
            "Request failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration=f"{duration:.3f}s",
        )

        # Record failed request metric
        record_http_request(request.method, request.url.path, 500, duration)

        raise


# Include API routers
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.

    Returns basic API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "metrics": settings.metrics_path,
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
