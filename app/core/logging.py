"""
Structured Logging Configuration
================================

Configures structlog for JSON-structured logging with tracing support.
All logs must be JSON format with proper tracing context.
"""

import logging.config
import logging
import structlog
from structlog.types import EventDict, Processor

from app.core.config import logging_settings


def add_trace_id(logger: logging.Logger, _method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add trace_id to log context if available.

    Args:
        logger: Logger instance
        method_name: Name of the logging method
        event_dict: Log event dictionary

    Returns:
        EventDict with trace_id added
    """
    # Try to get trace_id from context
    trace_id = getattr(logger, "trace_id", None)
    if trace_id:
        event_dict["trace_id"] = trace_id

    return event_dict


def add_request_id(logger: logging.Logger, _method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add request_id to log context if available.

    Args:
        logger: Logger instance
        method_name: Name of the logging method
        event_dict: Log event dictionary

    Returns:
        EventDict with request_id added
    """
    # Try to get request_id from context
    request_id = getattr(logger, "request_id", None)
    if request_id:
        event_dict["request_id"] = request_id

    return event_dict


def setup_logging() -> None:
    """
    Configure structlog for JSON-structured logging.

    Sets up:
    - JSON output format
    - Trace ID injection
    - Request ID injection
    - Proper log levels
    """
    # Define log processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        add_trace_id,
        add_request_id,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    # Configure logging
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": processors,
                    "format": "%(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": logging_settings.log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "app": {
                    "level": logging_settings.log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": logging.INFO,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "sqlalchemy": {
                    "level": logging.WARNING,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    )

    # Set up structlog
    structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
    )



def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance with proper configuration.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured BoundLogger instance
    """
    return structlog.get_logger(name)
