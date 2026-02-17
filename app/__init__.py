"""
FastAPI Todo API - Production-Ready Backend
============================================

This is a clean architecture implementation following DDD principles.

Layer Explanation:
------------------

1. **app/domain**: Business logic and domain models
   - Pure business concepts without infrastructure dependencies
   - Contains the core domain entities and schemas
   - Defines the rules of the domain

2. **app/infrastructure**: External system integrations
   - Database connectors (PostgreSQL, Redis)
   - Repository implementations
   - Adapter patterns for external systems
   - Database migrations

3. **app/services**: Use cases and business orchestration
   - Orchestrates domain logic and infrastructure
   - Contains application-specific business rules
   - Coordinates between domain and infrastructure layers

4. **app/api**: HTTP interface and routing
   - REST endpoints
   - Request/response handling
   - Input validation and transformation

5. **app/core**: Application configuration and utilities
   - Settings management
   - Logging configuration
   - Tracing and metrics setup
   - Application lifecycle management
"""

__version__ = "0.1.0"
