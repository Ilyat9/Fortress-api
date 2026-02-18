# Структура проекта

```
Fortress/
├── .github/
│   └── workflows/
│       └── ci.yml                          # GitHub Actions CI/CD pipeline
├── app/
│   ├── __init__.py                         # Package initialization
│   ├── main.py                             # Application entry point
│   ├── core/
│   │   ├── config.py                       # Configuration management (12-Factor App)
│   │   ├── logging.py                      # Structured logging (JSON, tracing)
│   │   ├── metrics.py                      # Prometheus metrics collection
│   │   ├── tracing.py                      # OpenTelemetry distributed tracing
│   │   └── lifespan.py                     # Application lifecycle management
│   ├── api/
│   │   └── v1/
│   │       ├── router.py                   # API v1 routing
│   │       └── endpoints/
│   │           └── todos.py                # Todo API endpoints
│   ├── domain/
│   │   └── todo/
│   │       ├── models.py                   # Domain entities (pure business logic)
│   │       └── schemas.py                  # Pydantic v2 validation schemas
│   ├── services/
│   │   └── todo_service.py                 # Business orchestration layer
│   └── infrastructure/
│       ├── db.py                           # Database infrastructure
│       ├── redis.py                        # Redis client infrastructure
│       └── repositories/
│           └── todo_repository.py          # Data access layer
├── grafana/
│   ├── dashboards/
│   │   └── todo-api-dashboard.json         # Grafana dashboard configuration
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboard.yml               # Dashboard provisioning
│       └── datasources/
│           └── prometheus.yml              # Datasource provisioning
├── tests/
│   ├── __init__.py                         # Test package initialization
│   ├── conftest.py                         # Test fixtures and configuration
│   ├── test_main.py                        # Main application tests
│   └── test_todos.py                       # Todo API integration tests
├── .env.example                            # Environment variables template
├── .gitignore                              # Git ignore patterns
├── CONTRIBUTING.md                         # Contribution guidelines
├── GIT_COMMIT_GUIDE.md                     # Git commit guide
├── docker-compose.yaml                     # Docker Compose orchestration
├── init-db.sql                             # Database initialization
├── prometheus.yml                          # Prometheus configuration
├── pyproject.toml                          # Poetry configuration
├── README.md                               # Main documentation
├── QUICKSTART.md                           # Quick start guide
├── PROJECT_STRUCTURE.md                    # This file
└── ARCHITECTURE.md                         # Architecture documentation
```

## Архитектура слоев

### 1. API Layer (app/api/)
- FastAPI endpoints and routers
- HTTP request/response handling
- Pydantic validation

### 2. Domain Layer (app/domain/)
- Pure business logic
- Domain entities
- Business rules
- Validation schemas

### 3. Services Layer (app/services/)
- Use case orchestration
- Business logic coordination
- Transaction management

### 4. Infrastructure Layer (app/infrastructure/)
- Database connectors (SQLAlchemy)
- Redis client
- Repository implementations
- External system integrations

### 5. Core Layer (app/core/)
- Configuration management
- Logging setup
- Tracing setup
- Metrics setup
- Application lifecycle

## Infrastructure Services

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   FastAPI   │◄────►│   PostgreSQL│◄────►│  Redis      │
│   Application│      │   Database  │      │  Cache      │
└─────────────┘      └─────────────┘      └─────────────┘
       │                     │                     │
       ├─────────────────────┴─────────────────────┤
       │                                           │
       ┌──────────────┐    ┌──────────────┐       │
       │ Prometheus   │    │   Jaeger     │       │
       │   Metrics    │    │   Tracing    │       │
       └──────────────┘    └──────────────┘       │
                                                    │
                    ┌─────────────────────────────┘
                    │
           ┌────────▼────────┐
           │   Grafana       │
           │   Dashboard     │
           └─────────────────┘
```

## Обязанности слоев

### 1. Domain Layer
Pure business logic, domain concepts, rules

### 2. Infrastructure Layer
Database, caching, external integrations

### 3. Services Layer
Business orchestration, use cases

### 4. API Layer
HTTP interface, request/response handling

## Ключевые особенности

### Production-Ready
- Connection pooling (PostgreSQL, Redis)
- Async/await throughout
- Graceful shutdown
- Health checks
- Security (non-root Docker user)
- Multi-stage Docker build

### Developer Experience
- Complete test suite
- CI/CD pipeline (GitHub Actions)
- Code quality tools (ruff, mypy)
- Type safety (mypy strict)
- API documentation (Swagger/ReDoc)
- Development server with hot reload

### DevOps
- Docker Compose orchestration
- Automated testing
- Automated linting
- Automated type checking
- Automated Docker builds

### Observability
- JSON structured logging (structlog)
- Prometheus metrics (all endpoints)
- OpenTelemetry tracing (Jaeger)
- Metrics for DB, cache, business operations
- Grafana dashboards
