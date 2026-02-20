# Fortress - Production-Ready Todo API - Quick Start

## 🎯 Project Summary

Полный, готовый к продакшену микросервис FastAPI с полной наблюдаемостью, CI/CD и корпоративным уровнем архитектуры.

## 📦 Deliverables

✅ **Core Stack**: FastAPI (async), PostgreSQL, Redis, Poetry, Pydantic v2
✅ **Architecture**: Clean Architecture / DDD-inspired layering
✅ **Observability**: Prometheus, Jaeger, Grafana, JSON structured logging
✅ **Testing**: pytest with integration tests and coverage
✅ **CI/CD**: GitHub Actions pipeline (lint, type check, tests, docker build)
✅ **Containerization**: Docker + Docker Compose with all services
✅ **Documentation**: Complete README, guides, and architecture docs
✅ **Git Workflow**: Conventional Commits with detailed commit guide

## 🚀 One-Command Setup

```bash
# Запустить все сервисы
docker compose up -d

# Дождаться проверки работоспособности
docker compose ps

# Запустить тесты
docker compose exec app poetry run pytest

# Доступ к сервисам
# API:     http://localhost:8000
# Health:  http://localhost:8000/api/v1/health
# Metrics: http://localhost:8000/metrics
# Docs:    http://localhost:8000/docs
# Grafana: http://localhost:3000 (admin/admin)
# Jaeger:  http://localhost:16686
# Prometheus: http://localhost:9090

# Остановить сервисы
docker compose down
```

## 📊 Architecture

```
app/
├── api/            # HTTP interface (FastAPI)
├── domain/         # Business logic (entities, schemas)
├── services/       # Use cases (business orchestration)
├── infrastructure/ # Data access (DB, Redis, repositories)
└── core/           # Core infrastructure (config, logging, tracing, metrics)
```

## 🔍 Observability URLs

| Service | URL | Purpose |
|---------|-----|---------|
| API | http://localhost:8000 | Application |
| Health | http://localhost:8000/api/v1/health | Health check |
| Metrics | http://localhost:8000/metrics | Prometheus |
| Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | API docs |
| Grafana | http://localhost:3000 | Dashboards |
| Jaeger | http://localhost:16686 | Traces |
| Prometheus | http://localhost:9090 | Metrics |

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test
poetry run pytest tests/test_todos.py

# Run with verbose output
poetry run pytest -v
```

## 📝 API Endpoints

```
POST   /api/v1/todos          Create todo
GET    /api/v1/todos          List todos (paginated)
GET    /api/v1/todos/{id}     Get todo
PUT    /api/v1/todos/{id}     Update todo
DELETE /api/v1/todos/{id}     Delete todo
PATCH  /api/v1/todos/{id}/complete Toggle completion
GET    /api/v1/health         Health check
GET    /metrics              Prometheus metrics
```

## 🔐 Authentication

**Grafana:**
- Username: `admin`
- Password: `admin`


## 📚 Documentation

- **README.md**: Complete project documentation
- **PROJECT_STRUCTURE.md**: Architecture overview
- **CONTRIBUTING.md**: Contribution guidelines
- **GIT_COMMIT_GUIDE.md**: Git workflow guide
- **.env.example**: Environment variables template

## ✨ Key Features

### Production-Ready
- ✅ Clean Architecture (DDD)
- ✅ Full observability (metrics, tracing, logging)
- ✅ Connection pooling (PostgreSQL, Redis)
- ✅ Caching layer (Redis)
- ✅ Structured JSON logging
- ✅ Security (non-root Docker user)
- ✅ Health checks
- ✅ Graceful shutdown

### Developer Experience
- ✅ Complete test suite
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Code quality tools (ruff, mypy)
- ✅ Type safety (mypy strict)
- ✅ API documentation (Swagger/ReDoc)
- ✅ Development server with hot reload

### DevOps
- ✅ Multi-stage Docker build
- ✅ Docker Compose orchestration
- ✅ Automated testing
- ✅ Automated linting
- ✅ Automated type checking
- ✅ Automated Docker builds

## 🎨 Tech Stack

```
Core:        Python 3.11+, FastAPI (async), Pydantic v2
Database:    PostgreSQL 16, SQLAlchemy 2.0 (async)
Cache:       Redis 7 (async)
Observability: OpenTelemetry, Prometheus, Jaeger, Grafana
Logging:     structlog (JSON)
Testing:     pytest, pytest-asyncio, pytest-cov
CI/CD:       GitHub Actions
Container:   Docker, Docker Compose
```

## 🚀 Next Steps

1. **Review Code**: Check all files in the project
2. **Run Tests**: `docker compose exec app poetry run pytest`
3. **Start Services**: `docker compose up -d`
4. **Explore API**: Open http://localhost:8000/docs
5. **Check Metrics**: Open http://localhost:9090
6. **View Traces**: Open http://localhost:16686
7. **Configure Grafana**: Open http://localhost:3000 (admin/admin)

## 🐛 Troubleshooting

```bash
# View app logs
docker compose logs -f app

# Check service health
docker compose ps

# Restart services
docker compose restart

# View database logs
docker compose logs -f postgres

# Clear Redis cache
docker compose exec app python -c "import redis; r = redis.from_url('redis://redis:6379/0'); r.flushdb()"
```

## 📄 License

MIT License - See LICENSE file for details

---

**Ready to deploy to production tomorrow.**
