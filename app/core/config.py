"""
Application Configuration
=========================

12-Factor App configuration management using Pydantic Settings.

Environment variables are the source of truth for all configuration.
"""

from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    database_url: str = Field(
        default="postgresql+asyncpg://todo_user:todo_password@localhost:5432/todo_db",
        description="PostgreSQL connection URL with async driver",
    )

    pool_size: int = Field(default=10, ge=1, le=50, description="Database connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=50, description="Max overflow connections")

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RedisSettings(BaseSettings):
    """Redis connection settings."""

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    pool_size: int = Field(default=10, ge=1, le=50, description="Redis connection pool size")

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class TracingSettings(BaseSettings):
    """OpenTelemetry tracing settings."""

    otel_enabled: bool = Field(default=True, description="Enable distributed tracing")
    otel_endpoint: str = Field(
        default="http://localhost:4318/v1/traces",
        description="OTLP trace export endpoint",
    )
    otel_service_name: str = Field(
        default="todo-api",
        description="OTLP service name",
    )
    otel_environment: str = Field(
        default="development",
        description="OTLP environment",
    )
    otel_sampling_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="OTLP sampling rate")

    model_config = SettingsConfigDict(
        env_prefix="OTEL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class MetricsSettings(BaseSettings):
    """Prometheus metrics settings."""

    metrics_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_path: str = Field(
        default="/metrics",
        description="Prometheus metrics endpoint path",
    )

    model_config = SettingsConfigDict(
        env_prefix="METRICS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LoggingSettings(BaseSettings):
    """Application logging settings."""

    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json",
        description="Log format: json or text",
    )
    log_trace_id: bool = Field(default=True, description="Include trace_id in logs")

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppSettings(BaseSettings):
    """Application-level settings."""

    app_name: str = Field(default="Todo API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # CORS settings
    cors_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins",
    )

    # API settings
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=100, ge=1, description="Rate limit requests per window"
    )
    rate_limit_window: int = Field(default=60, ge=1, description="Rate limit window in seconds")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        """Validate CORS origins."""
        return [
            origin if origin.startswith(("http://", "https://")) else f"http://{origin}"
            for origin in v
        ]

    @model_validator(mode="after")
    def set_debug_from_env(self) -> "AppSettings":
        """Set debug mode from environment."""
        import os

        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        return self


@lru_cache
def get_settings() -> AppSettings:
    """
    Get cached application settings.

    Returns:
        AppSettings: Cached settings instance
    """
    return AppSettings()


# Get database, redis, tracing, and metrics settings as global instances
settings = get_settings()
db_settings = DatabaseSettings()
redis_settings = RedisSettings()
tracing_settings = TracingSettings()
metrics_settings = MetricsSettings()
logging_settings = LoggingSettings()
