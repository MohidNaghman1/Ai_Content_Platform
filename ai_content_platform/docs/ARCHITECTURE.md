# AI Content Platform Architecture

## Overview

The platform uses a modular, layered architecture for scalability, maintainability, and extensibility. Built with FastAPI, SQLAlchemy, Redis, and Gemini AI, it follows modern best practices.

## System Architecture

**Layers:**

- Application: FastAPI, Pydantic
- Business Logic: Services, Events
- Data: SQLAlchemy ORM, Alembic
- Infrastructure: PostgreSQL, Redis, Gemini AI

**High-Level Diagram:**

```
Client → API Gateway (Middleware) → Routers → Services → (Repositories | Events | AI) → (DB | Redis | Gemini)
```

**Request Flow:**

1. Client Request → Middleware (auth, rate limit, logging)
2. Router (endpoint)
3. Dependency Injection (auth, DB)
4. Service (business logic)
5. Repository (data access)
6. DB/Cache/AI/Events
7. Response

## Key Design Patterns

- **Repository Pattern:** Abstracts data access from business logic.
- **Service Layer:** Encapsulates business rules and orchestration.
- **Dependency Injection:** For loose coupling and testability.
- **Observer/Event-Driven:** For async event handling (Redis pub/sub).

## Module Structure

Each module contains:

```
models.py   # DB models
schemas.py  # Pydantic schemas
repository.py  # Data access
service.py  # Business logic
router.py   # API endpoints
```

## Database Design

**Entities:** Users, Articles, Tags, Conversations, Messages, Notifications

**Relationships:**

- Users have many Articles, Conversations, Notifications
- Articles have many Tags (many-to-many)
- Conversations have many Messages

**Indexes:** On emails, roles, slugs, created_at, etc. for performance.

## Event-Driven Architecture

- Services publish events to Redis (e.g., `article.created`)
- Worker subscribes and routes to handlers (notifications, analytics)
- Decouples business logic from side effects

## AI Integration

- Gemini AI client for content generation and chat
- Service layer orchestrates prompts and parses responses

## Security

- JWT authentication (access/refresh tokens)
- Role-based permissions (viewer, creator, admin)
- Security headers and middleware

## Caching

- Multi-layer: in-memory (lru_cache), Redis (distributed), DB
- Decorators for endpoint response caching

## Scalability

**Horizontal scaling:**

```
Load Balancer → Multiple App Instances → Shared DB/Redis
```

- Read replicas for DB
- Connection pooling

## Monitoring & Observability

- Structured JSON logging
- Health check endpoints for app, DB, Redis

---

## Conclusion

This architecture ensures modularity, scalability, maintainability, security, and observability. For implementation details, see the codebase and module docs.

---
