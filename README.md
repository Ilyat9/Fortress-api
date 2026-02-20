# Fortress - Production-Ready Todo API

Проект **Fortress** — это полноценный, готовый к продакшену микросервис FastAPI с полной наблюдаемостью, CI/CD и корпоративным уровнем архитектуры.

## 🎯 Обзор проекта

Это не учебный демо-проект — это готовое к продакшену приложение, построенное с использованием:
- **Чистая архитектура** (принципы Domain-Driven Design)
- **Полная наблюдаемость** (Tracing, Metrics, Structured Logging)
- **Готовое к продакшену** (Security, Reliability, Scalability)
- **Полный DevOps** (Docker, CI/CD, Testing)

## 🚀 Быстрый старт

### Требования
- Docker & Docker Compose
- Python 3.11+
- Poetry (необязательно, можно использовать pip)

### One-Command Setup

```bash
# Запустить все сервисы (app, postgres, redis, prometheus, grafana, jaeger, elasticsearch)
docker compose up -d

# Дождаться проверки работоспособности сервисов
docker compose ps

# Запустить тесты
docker compose exec app poetry run pytest

# Остановить все сервисы
docker compose down
```

## 📋 Архитектура

```
app/
├── api/                    # HTTP API Layer
│   └── v1/
│       ├── router.py       # API routing
│       └── endpoints/
│           └── todos.py    # Todo endpoints
├── domain/                 # Business Logic Layer
│   └── todo/
│       ├── models.py       # Domain entities
│       └── schemas.py      # Pydantic schemas
├── services/               # Use Case Layer
│   └── todo_service.py     # Business logic orchestration
├── infrastructure/         # Infrastructure Layer
│   ├── db.py              # Database management
│   ├── redis.py           # Redis management
│   └── repositories/
│       └── todo_repository.py  # Data access layer
├── core/                   # Core Infrastructure
│   ├── config.py          # Configuration management
│   ├── logging.py         # Structured logging
│   ├── tracing.py         # OpenTelemetry tracing
│   ├── metrics.py         # Prometheus metrics
│   └── lifespan.py        # Application lifecycle
└── main.py                 # Application entry point
```

### Обязанности слоев

1. **Domain Layer** - Чистая бизнес-логика, концепции домена, правила
2. **Infrastructure Layer** - База данных, кеширование, внешние интеграции
3. **Services Layer** - Оркестрация бизнес-логики, use cases
4. **API Layer** - HTTP-интерфейс, обработка запросов/ответов

## 🔍 Наблюдаемость (Observability)

### Доступные сервисы

| Service | URL | Назначение |
|---------|-----|-----------|
| API | http://localhost:8000 | FastAPI приложение |
| Health Check | http://localhost:8000/api/v1/health | Мониторинг работоспособности |
| Metrics | http://localhost:8000/metrics | Prometheus метрики |
| Swagger Docs | http://localhost:8000/docs | Интерактивная документация API |
| ReDoc | http://localhost:8000/redoc | Документация API |
| Prometheus | http://localhost:9090 | Хранилище метрик |
| Grafana | http://localhost:3000 | Дашборды |
| Jaeger | http://localhost:16686 | Распределённый tracing |

### Аутентификация и доступ

**Grafana:**
- Username: `admin`
- Password: `admin`

### Доступные метрики

- HTTP request/response rates
- Request latency (P50, P95, P99)
- Error rates
- Database queries & performance
- Redis cache hit/miss rates
- Business operation counters

## 🧪 Тестирование

### Запуск всех тестов

```bash
# Через Docker
docker compose exec app poetry run pytest

# Или локально через poetry
poetry install --with dev
poetry run pytest
```

### Покрытие кода

```bash
# Сгенерировать отчет покрытия
poetry run pytest --cov=app --cov-report=html

# Открыть HTML отчет
open htmlcov/index.html
```

### Результаты тестов

- **Integration Tests**: Полное тестирование API endpoint'ов
- **Database Tests**: Транзакции и ORM тесты
- **Rate Limiting Tests**: Нагрузочное тестирование
- **Coverage**: Полное покрытие кода

## 🛠️ Разработка

### Настройка локально

```bash
# Клонировать репозиторий
git clone https://github.com/Ilyat9/Fortress-api
cd Fortress-api

# Установить зависимости
poetry install --with dev

# Скопировать файл среды
cp .env.example .env

# Создать таблицы в базе данных
poetry run alembic upgrade head

# Запустить в режиме разработки
poetry run uvicorn app.main:app --reload
```

### Environment Variables

См. [`.env.example`](.env.example) для всех доступных параметров конфигурации.

### Код-ревью и качество

```bash
# Проверка кода (linting)
poetry run ruff check app tests

# Форматирование кода
poetry run ruff format app tests

# Проверка типов (type checking)
poetry run mypy app

# Запустить все проверки качества
poetry run ruff check app tests && \
poetry run ruff format --check app tests && \
poetry run mypy app
```

## 📦 Docker

### Build Image

```bash
docker build -t todo-api:latest .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db \
  -e REDIS_URL=redis://redis:6379/0 \
  todo-api:latest
```

### Docker Compose

```bash
# Запустить все сервисы
docker compose up -d

# Просмотреть логи
docker compose logs -f app

# Остановить сервисы
docker compose down

# Остановить и удалить volumes
docker compose down -v
```

## 🔄 CI/CD

### GitHub Actions Pipeline

Репозиторий включает полный CI/CD pipeline:

1. **Lint**: Ruff проверка качества кода
2. **Type Check**: Mypy строгая проверка типов
3. **Tests**: pytest с покрытием
4. **Docker Build**: Сборка образа контейнера

### Запуск локально

```bash
# Запустить конкретный job
docker compose run --rm app pytest

# Запустить с покрытием
docker compose run --rm app pytest --cov=app --cov-report=term-missing
```

## 📡 API Endpoints

### Todos API

#### Create Todo (Создать todo)
```http
POST /api/v1/todos
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": false,
  "priority": "high"
}
```

#### List Todos (Список todo)
```http
GET /api/v1/todos?page=1&page_size=20&sort_by=created_at&order=desc
```

#### Get Todo (Получить todo)
```http
GET /api/v1/todos/{id}
```

#### Update Todo (Обновить todo)
```http
PUT /api/v1/todos/{id}
Content-Type: application/json

{
  "title": "Updated title",
  "is_completed": true
}
```

#### Delete Todo (Удалить todo)
```http
DELETE /api/v1/todos/{id}
```

#### Toggle Completion (Переключить статус выполнения)
```http
PATCH /api/v1/todos/{id}/complete
```

### Health & Metrics

```http
GET /api/v1/health
GET /metrics
```

## 🎨 Configuration

### Database

- PostgreSQL 16
- Connection pooling
- Async driver (asyncpg)
- Automatic migrations via Alembic

### Cache

- Redis 7
- Connection pooling
- JSON serialization
- TTL support

### Observability

- **Tracing**: OpenTelemetry + Jaeger
- **Metrics**: Prometheus + Grafana
- **Logging**: JSON structured logs with structlog

## 🔒 Безопасность

- **Authentication**: Не включено (заглушка для будущего)
- **Authorization**: Не включено (заглушка для будущего)
- **CORS**: Configurable origins
- **Input Validation**: Pydantic v2 строгая валидация
- **Database**: Non-root user в Docker
- **Rate Limiting**: Configurable (placeholder)

## 📊 Производительность

- **Async/Await**: Полное async-реализация
- **Connection Pooling**: PostgreSQL + Redis
- **Caching**: Redis для горячих данных
- **Indexing**: Оптимизированные индексы базы данных
- **Compression**: GZIP middleware

## 🚦 Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'feat(scope): message'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

Этот проект лицензирован по MIT License - подробности в файле LICENSE.

## 🆘 Поддержка

По вопросам и проблемам:
- Откройте GitHub issue
- Проверьте существующую документацию
- Изучите тестовые кейсы для примеров

## 🙏 Acknowledgments

Built with:
- FastAPI
- SQLAlchemy 2.0
- Redis
- PostgreSQL
- OpenTelemetry
- Prometheus
- Grafana
- Pydantic v2
- structlog

---

**Production-ready. Deploy immediately.**
