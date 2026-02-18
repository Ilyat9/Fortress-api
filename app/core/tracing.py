"""
OpenTelemetry Tracing Configuration
===================================

Configures distributed tracing with OpenTelemetry SDK.
Traces are exported to Jaeger via OTLP.

Coverage:
- HTTP requests (FastAPI)
- Database queries (SQLAlchemy)
- Cache operations (Redis)
"""

from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from app.core.config import tracing_settings


def setup_tracing(app: Any) -> None:
    """
    Setup OpenTelemetry tracing for the application.

    This function:
    1. Configures the tracer provider with resource attributes
    2. Sets up span processors (batch for production, console for dev)
    3. Instruments FastAPI application
    4. Instruments SQLAlchemy database
    5. Instruments Redis cache

    Args:
        app: FastAPI application instance
    """
    if not tracing_settings.otel_enabled:
        return

    # Create resource with service attributes
    resource = Resource.create(
        {
            SERVICE_NAME: tracing_settings.otel_service_name,
            SERVICE_VERSION: tracing_settings.otel_environment,
            "service.environment": tracing_settings.otel_environment,
            "service.version": "0.1.0",
        }
    )

    # Set up tracer provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Add span processors
    # In production: BatchSpanProcessor with OTLP exporter
    # In development: ConsoleSpanExporter for debugging
    if tracing_settings.otel_environment != "development":
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        otlp_exporter = OTLPSpanExporter(endpoint=tracing_settings.otel_endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    else:
        # Development: console exporter for debugging
        provider.add_span_processor(ConsoleSpanExporter())

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument(enable_commenter=False, sqlalchemy_plugin=True)

    # Instrument Redis
    RedisInstrumentor().instrument()


def get_tracer() -> trace.Tracer:
    """
    Get the current tracer for the application.

    Returns:
        OpenTelemetry tracer instance
    """
    if not tracing_settings.otel_enabled:
        return trace.get_tracer(__name__)

    return trace.get_tracer(__name__)


@contextmanager
def trace_operation(name: str, **kwargs: Any):
    """
    Context manager for tracing operations.

    Args:
        name: Operation name
        **kwargs: Additional span attributes

    Yields:
        Tracer context
    """
    if not tracing_settings.otel_enabled:
        yield
        return

    tracer = get_tracer()
    with tracer.start_as_current_span(
        name, kind=trace.SpanKind.INTERNAL, attributes=kwargs
    ) as span:
        yield span


def extract_trace_context(_request: Any) -> dict[str, str]:
    """
    Extract trace context from HTTP request.

    Args:
        request: FastAPI request instance

    Returns:
        Dictionary with extracted trace context
    """
    carrier = {}
    TraceContextTextMapPropagator().inject(carrier)
    return carrier


def inject_trace_context(carrier: dict[str, str]) -> None:
    """
    Inject trace context into carrier for propagation.

    Args:
        carrier: Dictionary to inject context into
    """
    TraceContextTextMapPropagator().inject(carrier)


def extract_from_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Extract trace context from HTTP headers.

    Args:
        headers: HTTP headers dictionary

    Returns:
        Dictionary with trace context
    """
    carrier = {}
    for key, value in headers.items():
        if key.lower() in ("traceparent", "trace-id", "tracestate"):
            carrier[key] = value
    return carrier


def add_span_attribute(span: trace.Span, key: str, value: Any) -> None:
    """
    Add attribute to current span.

    Args:
        span: Span instance
        key: Attribute key
        value: Attribute value
    """
    if span and tracing_settings.otel_enabled:
        span.set_attribute(key, str(value))
