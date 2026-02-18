"""
Prometheus Metrics Configuration
=================================

Configures Prometheus metrics collection for the application.
Provides metrics for:
- HTTP request/response performance
- Database operations
- Cache operations
- Custom business metrics
"""

from prometheus_client import REGISTRY, Counter, Gauge, Histogram

# HTTP Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=REGISTRY,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
    registry=REGISTRY,
)

# Database Metrics
db_connections_active = Gauge(
    "db_connections_active",
    "Active database connections",
    registry=REGISTRY,
)

db_connections_idle = Gauge(
    "db_connections_idle",
    "Idle database connections",
    registry=REGISTRY,
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
    registry=REGISTRY,
)

db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"],
    registry=REGISTRY,
)

# Cache Metrics
cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
    registry=REGISTRY,
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
    registry=REGISTRY,
)

cache_operations_in_progress = Gauge(
    "cache_operations_in_progress",
    "Number of cache operations in progress",
    registry=REGISTRY,
)

cache_set_duration_seconds = Histogram(
    "cache_set_duration_seconds",
    "Cache set operation duration in seconds",
    registry=REGISTRY,
)

# Application Metrics
business_operations_total = Counter(
    "business_operations_total",
    "Total business operations",
    ["operation", "status"],
    registry=REGISTRY,
)

business_operations_duration_seconds = Histogram(
    "business_operations_duration_seconds",
    "Business operation duration in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
    registry=REGISTRY,
)

# Todo-specific metrics
todos_created_total = Counter(
    "todos_created_total",
    "Total number of todos created",
    registry=REGISTRY,
)

todos_updated_total = Counter(
    "todos_updated_total",
    "Total number of todos updated",
    registry=REGISTRY,
)

todos_deleted_total = Counter(
    "todos_deleted_total",
    "Total number of todos deleted",
    registry=REGISTRY,
)

todos_completed_total = Counter(
    "todos_completed_total",
    "Total number of todos completed",
    registry=REGISTRY,
)


def record_http_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """
    Record an HTTP request metric.

    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Request endpoint
        status_code: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def record_http_request_start(method: str, endpoint: str) -> None:
    """
    Record start of HTTP request.

    Args:
        method: HTTP method
        endpoint: Request endpoint
    """
    http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()


def record_http_request_end(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """
    Record end of HTTP request.

    Args:
        method: HTTP method
        endpoint: Request endpoint
        status_code: HTTP status code
        duration: Request duration in seconds
    """
    http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
    record_http_request(method, endpoint, status_code, duration)


def record_cache_hit() -> None:
    """Record a cache hit."""
    cache_hits_total.inc()


def record_cache_miss() -> None:
    """Record a cache miss."""
    cache_misses_total.inc()


def record_db_query(operation: str, table: str, duration: float) -> None:
    """
    Record database query metric.

    Args:
        operation: Database operation type (SELECT, INSERT, etc.)
        table: Table name
        duration: Query duration in seconds
    """
    db_queries_total.labels(operation=operation, table=table).inc()
    db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)


def record_business_operation(operation: str, status: str, duration: float) -> None:
    """
    Record business operation metric.

    Args:
        operation: Operation name
        status: Operation status (success, error, etc.)
        duration: Operation duration in seconds
    """
    business_operations_total.labels(operation=operation, status=status).inc()
    business_operations_duration_seconds.labels(operation=operation).observe(duration)
