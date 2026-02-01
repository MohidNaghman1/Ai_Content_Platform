# Architecture Documentation

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Design Patterns](#design-patterns)
- [Module Structure](#module-structure)
- [Database Design](#database-design)
- [Event-Driven Architecture](#event-driven-architecture)
- [AI Integration](#ai-integration)
- [Security Architecture](#security-architecture)
- [Caching Strategy](#caching-strategy)
- [Scalability](#scalability)
- [Performance Optimization](#performance-optimization)
- [Monitoring & Observability](#monitoring--observability)

## Overview

The AI Content Platform follows a modular, layered architecture designed for scalability, maintainability, and extensibility. The system is built using modern software engineering principles and best practices.

### Core Principles

1. **Separation of Concerns**: Clear boundaries between different system components
2. **Single Responsibility**: Each module/class has one well-defined purpose
3. **Dependency Inversion**: High-level modules don't depend on low-level modules
4. **Open/Closed Principle**: Open for extension, closed for modification
5. **DRY (Don't Repeat Yourself)**: Reusable components and utilities
6. **SOLID Principles**: Applied throughout the codebase

### Technology Stack

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  FastAPI + Uvicorn + Pydantic          │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│         Business Logic Layer            │
│  Services + Repositories + Events       │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│          Data Layer                     │
│  SQLAlchemy ORM + Alembic Migrations   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│        Infrastructure Layer             │
│  PostgreSQL + Redis + Gemini AI        │
└─────────────────────────────────────────┘
```

## System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Client Layer                          │
│   [Web App] [Mobile App] [Third-Party Integrations]       │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                   API Gateway Layer                        │
│  ┌──────────────────────────────────────────────────┐     │
│  │  CORS Middleware                                  │     │
│  │  Authentication Middleware                        │     │
│  │  Rate Limiting Middleware                         │     │
│  │  Logging Middleware                               │     │
│  │  Error Handling Middleware                        │     │
│  └──────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    Router Layer                            │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│  │  Auth  │ │ Users  │ │Content │ │  Chat  │ │ Admin  │ │
│  │ Router │ │ Router │ │ Router │ │ Router │ │ Router │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                   Service Layer                            │
│  ┌────────────────────────────────────────────────┐       │
│  │  Business Logic & Orchestration                 │       │
│  │  • Input Validation                             │       │
│  │  • Authorization Checks                         │       │
│  │  • Data Transformation                          │       │
│  │  • Event Publishing                             │       │
│  │  • External Service Integration                 │       │
│  └────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ Repository   │ │  Event   │ │   External   │
    │    Layer     │ │ Publisher│ │   Services   │
    │              │ │          │ │              │
    │ • CRUD Ops   │ │ • Redis  │ │ • Gemini AI  │
    │ • Queries    │ │ • Events │ │ • SMTP       │
    │ • Filters    │ │          │ │              │
    └──────────────┘ └──────────┘ └──────────────┘
              │             │
              ▼             ▼
    ┌──────────────┐ ┌──────────┐
    │  PostgreSQL  │ │  Redis   │
    │   Database   │ │  Cache   │
    └──────────────┘ └──────────┘
```

### Request Flow

```
1. Client Request
   ↓
2. API Gateway (Middleware Stack)
   ↓
3. Router (Endpoint Handler)
   ↓
4. Dependency Injection (Auth, DB Session)
   ↓
5. Service Layer (Business Logic)
   ↓
6. Repository Layer (Data Access)
   ↓
7. Database/Cache/External Services
   ↓
8. Event Publishing (Async)
   ↓
9. Response Serialization
   ↓
10. Client Response
```

### Component Interaction

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
│                                                          │
│  ┌──────────────┐                                       │
│  │   Router     │──────┐                                │
│  │  (Endpoint)  │      │                                │
│  └──────────────┘      │                                │
│         │              │                                │
│         │              ▼                                │
│         │     ┌──────────────┐                          │
│         └────>│   Service    │                          │
│               │    Layer     │                          │
│               └──────────────┘                          │
│                      │                                  │
│         ┌────────────┼────────────┐                     │
│         ▼            ▼            ▼                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │Repository│ │  Events  │ │  AI/Ext  │               │
│  └──────────┘ └──────────┘ └──────────┘               │
│         │            │            │                     │
│         ▼            ▼            ▼                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │PostgreSQL│ │  Redis   │ │ Gemini   │               │
│  └──────────┘ └──────────┘ └──────────┘               │
└─────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Repository Pattern

**Purpose**: Abstracts data access logic from business logic.

**Implementation**:
```python
# app/modules/content/repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Article

class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, article_id: str) -> Optional[Article]:
        return self.db.query(Article).filter(
            Article.id == article_id
        ).first()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: dict = None
    ) -> List[Article]:
        query = self.db.query(Article)
        
        if filters:
            if filters.get('author_id'):
                query = query.filter(
                    Article.author_id == filters['author_id']
                )
            if filters.get('status'):
                query = query.filter(
                    Article.status == filters['status']
                )
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, article_data: dict) -> Article:
        article = Article(**article_data)
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def update(
        self, 
        article_id: str, 
        update_data: dict
    ) -> Optional[Article]:
        article = self.get_by_id(article_id)
        if article:
            for key, value in update_data.items():
                setattr(article, key, value)
            self.db.commit()
            self.db.refresh(article)
        return article
    
    def delete(self, article_id: str) -> bool:
        article = self.get_by_id(article_id)
        if article:
            self.db.delete(article)
            self.db.commit()
            return True
        return False
```

**Benefits**:
- Testable (can mock repository)
- Reusable queries
- Centralized data access logic
- Easy to switch databases

### 2. Service Layer Pattern

**Purpose**: Encapsulates business logic and orchestrates operations.

**Implementation**:
```python
# app/modules/content/service.py
from typing import List, Optional
from .repository import ArticleRepository
from .schemas import ArticleCreate, ArticleUpdate
from app.events.publisher import EventPublisher
from app.shared.exceptions import NotFoundException

class ArticleService:
    def __init__(
        self,
        repository: ArticleRepository,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.event_publisher = event_publisher
    
    async def create_article(
        self,
        article_data: ArticleCreate,
        author_id: str
    ):
        # Business logic
        article_dict = article_data.dict()
        article_dict['author_id'] = author_id
        article_dict['slug'] = self._generate_slug(
            article_data.title
        )
        
        # Repository call
        article = self.repository.create(article_dict)
        
        # Publish event
        await self.event_publisher.publish(
            'article.created',
            {'article_id': article.id, 'author_id': author_id}
        )
        
        return article
    
    async def publish_article(self, article_id: str):
        article = self.repository.get_by_id(article_id)
        if not article:
            raise NotFoundException("Article not found")
        
        # Business rule: only drafts can be published
        if article.status != 'draft':
            raise ValueError("Only draft articles can be published")
        
        # Update article
        updated = self.repository.update(
            article_id,
            {
                'status': 'published',
                'published_at': datetime.utcnow()
            }
        )
        
        # Publish event
        await self.event_publisher.publish(
            'article.published',
            {'article_id': article_id}
        )
        
        return updated
    
    def _generate_slug(self, title: str) -> str:
        # Slug generation logic
        return title.lower().replace(' ', '-')
```

**Benefits**:
- Clear separation of concerns
- Reusable business logic
- Easy to test
- Centralized event publishing

### 3. Dependency Injection Pattern

**Purpose**: Provides loose coupling and testability.

**Implementation**:
```python
# app/shared/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.content.repository import ArticleRepository
from app.modules.content.service import ArticleService
from app.events.publisher import EventPublisher

def get_article_repository(
    db: Session = Depends(get_db)
) -> ArticleRepository:
    return ArticleRepository(db)

def get_event_publisher() -> EventPublisher:
    return EventPublisher()

def get_article_service(
    repository: ArticleRepository = Depends(get_article_repository),
    event_publisher: EventPublisher = Depends(get_event_publisher)
) -> ArticleService:
    return ArticleService(repository, event_publisher)
```

**Usage in Router**:
```python
# app/modules/content/router.py
from fastapi import APIRouter, Depends
from .service import ArticleService
from .schemas import ArticleCreate, ArticleResponse
from app.shared.dependencies import get_article_service

router = APIRouter()

@router.post("/articles", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    service: ArticleService = Depends(get_article_service),
    current_user = Depends(get_current_user)
):
    return await service.create_article(
        article_data,
        current_user.id
    )
```

### 4. Factory Pattern

**Purpose**: Centralized object creation.

**Implementation**:
```python
# app/shared/factories.py
from app.modules.auth.service import AuthService
from app.modules.content.service import ArticleService
from app.modules.chat.ai_client import GeminiClient
from app.config import settings

class ServiceFactory:
    @staticmethod
    def create_auth_service(db: Session):
        from app.modules.auth.repository import UserRepository
        repository = UserRepository(db)
        return AuthService(repository)
    
    @staticmethod
    def create_ai_client():
        return GeminiClient(
            api_key=settings.GEMINI_API_KEY,
            model=settings.AI_MODEL
        )
```

### 5. Observer Pattern (Event-Driven)

**Purpose**: Decoupled event handling.

**Implementation**:
```python
# app/events/publisher.py
import json
from typing import Dict, Any
from app.config import get_redis_client

class EventPublisher:
    def __init__(self):
        self.redis = get_redis_client()
    
    async def publish(self, event_type: str, data: Dict[str, Any]):
        message = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.redis.publish(
            'events',
            json.dumps(message)
        )

# app/events/subscriber.py
class EventSubscriber:
    def __init__(self):
        self.redis = get_redis_client()
        self.handlers = {}
    
    def register_handler(self, event_type: str, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def listen(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe('events')
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                event_type = data['event_type']
                
                if event_type in self.handlers:
                    for handler in self.handlers[event_type]:
                        await handler(data['data'])
```

## Module Structure

### Modular Architecture

Each module follows a consistent structure:

```
app/modules/{module_name}/
├── __init__.py
├── models.py          # Database models
├── schemas.py         # Pydantic schemas
├── repository.py      # Data access layer
├── service.py         # Business logic
├── router.py          # API endpoints
├── dependencies.py    # Module-specific dependencies
└── utils.py           # Module-specific utilities
```

### Module Example: Auth Module

```python
# app/modules/auth/models.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# app/modules/auth/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    role: Optional[str] = "viewer"

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# app/modules/auth/service.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, repository):
        self.repository = repository
    
    def create_user(self, user_data: UserCreate):
        hashed_password = pwd_context.hash(user_data.password)
        user_dict = user_data.dict()
        user_dict['hashed_password'] = hashed_password
        del user_dict['password']
        
        return self.repository.create(user_dict)
    
    def authenticate_user(self, email: str, password: str):
        user = self.repository.get_by_email(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
```

### Module Communication

Modules communicate through:
1. **Direct Service Calls**: For synchronous operations
2. **Events**: For asynchronous operations
3. **Shared Utilities**: For common functionality

```python
# Direct service call
from app.modules.users.service import UserService

class ArticleService:
    def create_article(self, article_data, author_id):
        # Validate author exists
        user = UserService.get_user(author_id)
        if not user:
            raise ValueError("Author not found")
        
        # Create article
        return self.repository.create(article_data)

# Event-based communication
await event_publisher.publish(
    'article.created',
    {'article_id': article.id}
)
```

## Database Design

### Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    Users     │         │   Articles   │         │     Tags     │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │────────<│ author_id(FK)│         │ id (PK)      │
│ email        │         │ id (PK)      │>────────│ name         │
│ password     │         │ title        │         │ slug         │
│ full_name    │         │ content      │         └──────────────┘
│ role         │         │ status       │                │
│ is_active    │         │ created_at   │                │
│ created_at   │         └──────────────┘                │
└──────────────┘                │                        │
       │                        │                        │
       │                        │          ┌─────────────┴──────────┐
       │                        │          │   article_tags        │
       │                        │          ├─────────────────────────┤
       │                        └─────────>│ article_id (FK)        │
       │                                   │ tag_id (FK)            │
       │                                   └────────────────────────┘
       │
       │           ┌──────────────┐
       └──────────>│Conversations │
                   ├──────────────┤
                   │ id (PK)      │
                   │ user_id (FK) │
                   │ title        │
                   │ created_at   │
                   └──────────────┘
                          │
                          │
                   ┌──────┴──────┐
                   │   Messages  │
                   ├─────────────┤
                   │ id (PK)     │
                   │ conv_id(FK) │
                   │ role        │
                   │ content     │
                   │ tokens      │
                   │ created_at  │
                   └─────────────┘
```

### Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    avatar_url VARCHAR(500),
    bio TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Articles Table
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    views INTEGER DEFAULT 0,
    reading_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP
);

CREATE INDEX idx_articles_author ON articles(author_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_created ON articles(created_at DESC);

-- Full-text search index
CREATE INDEX idx_articles_content_search ON articles 
    USING gin(to_tsvector('english', title || ' ' || content));

-- Tags Table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tags_slug ON tags(slug);

-- Article-Tag Junction Table
CREATE TABLE article_tags (
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- Conversations Table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);

-- Messages Table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);

-- Notifications Table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);
```

### Database Migrations

Using Alembic for database versioning:

```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), server_default='viewer'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])

def downgrade():
    op.drop_index('idx_users_role')
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

## Event-Driven Architecture

### Event Flow

```
┌────────────────┐
│  Service Layer │
│  (Publisher)   │
└────────┬───────┘
         │ Publish Event
         ▼
┌────────────────┐
│  Redis Queue   │
│  (Pub/Sub)     │
└────────┬───────┘
         │ Subscribe
         ▼
┌────────────────┐
│ Event Worker   │
│  (Subscriber)  │
└────────┬───────┘
         │ Route to Handler
         ▼
┌────────────────┐
│ Event Handlers │
│  • Email       │
│  • Notification│
│  • Analytics   │
└────────────────┘
```

### Event Types

```python
# app/events/types.py
from enum import Enum

class EventType(str, Enum):
    # User Events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    
    # Article Events
    ARTICLE_CREATED = "article.created"
    ARTICLE_UPDATED = "article.updated"
    ARTICLE_PUBLISHED = "article.published"
    ARTICLE_DELETED = "article.deleted"
    
    # Chat Events
    CONVERSATION_CREATED = "conversation.created"
    MESSAGE_SENT = "message.sent"
    
    # Notification Events
    NOTIFICATION_CREATED = "notification.created"
```

### Event Handlers

```python
# app/events/handlers/user_events.py
from app.modules.notifications.service import NotificationService

class UserEventHandler:
    def __init__(self):
        self.notification_service = NotificationService()
    
    async def handle_user_created(self, data: dict):
        """Send welcome notification to new user"""
        await self.notification_service.create_notification(
            user_id=data['user_id'],
            type='welcome',
            title='Welcome to AI Content Platform!',
            message='Get started by creating your first article.',
            link='/articles/new'
        )
    
    async def handle_user_login(self, data: dict):
        """Log user login for analytics"""
        # Analytics logic here
        pass

# app/events/handlers/content_events.py
class ContentEventHandler:
    async def handle_article_published(self, data: dict):
        """Notify followers when article is published"""
        article_id = data['article_id']
        # Get article and author
        # Notify followers
        # Update analytics
        pass
```

### Worker Process

```python
# app/worker.py
import asyncio
from app.events.subscriber import EventSubscriber
from app.events.handlers.user_events import UserEventHandler
from app.events.handlers.content_events import ContentEventHandler
from app.events.types import EventType

async def main():
    subscriber = EventSubscriber()
    user_handler = UserEventHandler()
    content_handler = ContentEventHandler()
    
    # Register handlers
    subscriber.register_handler(
        EventType.USER_CREATED,
        user_handler.handle_user_created
    )
    subscriber.register_handler(
        EventType.ARTICLE_PUBLISHED,
        content_handler.handle_article_published
    )
    
    # Start listening
    print("Event worker started...")
    await subscriber.listen()

if __name__ == "__main__":
    asyncio.run(main())
```

## AI Integration

### Gemini Client Architecture

```python
# app/modules/chat/ai_client.py
import google.generativeai as genai
from typing import AsyncGenerator
from app.config import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.AI_MODEL)
    
    async def generate_content(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate content using Gemini"""
        response = await self.model.generate_content_async(
            prompt,
            generation_config={
                'max_output_tokens': max_tokens,
                'temperature': temperature
            }
        )
        return response.text
    
    async def stream_response(
        self,
        messages: list,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses"""
        response = await self.model.generate_content_async(
            messages,
            generation_config={'temperature': temperature},
            stream=True
        )
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return self.model.count_tokens(text).total_tokens
```

### AI Service Layer

```python
# app/modules/content/ai_service.py
class AIContentService:
    def __init__(self, ai_client: GeminiClient):
        self.ai_client = ai_client
    
    async def generate_article(
        self,
        prompt: str,
        style: str = "professional"
    ):
        """Generate article content"""
        enhanced_prompt = f"""
        Write a {style} article about: {prompt}
        
        Include:
        - Engaging title
        - Clear introduction
        - Well-structured body
        - Conclusion
        - Suggested excerpt
        """
        
        content = await self.ai_client.generate_content(
            enhanced_prompt,
            max_tokens=2000
        )
        
        return self._parse_article(content)
    
    async def summarize_content(
        self,
        content: str,
        max_length: int = 200
    ):
        """Summarize long-form content"""
        prompt = f"""
        Summarize the following content in {max_length} words or less:
        
        {content}
        
        Provide:
        - Brief summary
        - Key points (bullet format)
        """
        
        summary = await self.ai_client.generate_content(prompt)
        return self._parse_summary(summary)
```

## Security Architecture

### Authentication Flow

```
1. User Login Request
   ↓
2. Validate Credentials
   ↓
3. Generate JWT Tokens
   • Access Token (short-lived)
   • Refresh Token (long-lived)
   ↓
4. Return Tokens to Client
   ↓
5. Client Includes Access Token in Requests
   ↓
6. Verify Token on Each Request
   ↓
7. Check User Permissions
   ↓
8. Allow/Deny Access
```

### Authorization Layers

```python
# app/shared/permissions.py
from enum import Enum
from functools import wraps
from fastapi import HTTPException, status

class Permission(str, Enum):
    READ_ARTICLES = "read:articles"
    WRITE_ARTICLES = "write:articles"
    DELETE_ARTICLES = "delete:articles"
    MANAGE_USERS = "manage:users"
    VIEW_ANALYTICS = "view:analytics"

ROLE_PERMISSIONS = {
    "viewer": [
        Permission.READ_ARTICLES
    ],
    "creator": [
        Permission.READ_ARTICLES,
        Permission.WRITE_ARTICLES,
        Permission.DELETE_ARTICLES
    ],
    "admin": [
        Permission.READ_ARTICLES,
        Permission.WRITE_ARTICLES,
        Permission.DELETE_ARTICLES,
        Permission.MANAGE_USERS,
        Permission.VIEW_ANALYTICS
    ]
}

def require_permission(permission: Permission):
    """Decorator to check permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            user_permissions = ROLE_PERMISSIONS.get(
                current_user.role,
                []
            )
            
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

### Security Headers

```python
# app/shared/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = (
            'max-age=31536000; includeSubDomains'
        )
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'"
        )
        
        return response
```

## Caching Strategy

### Multi-Layer Caching

```
┌─────────────────────────────────────┐
│      Application Memory Cache       │
│      (Function-level, @lru_cache)  │
└─────────────────────────────────────┘
                 ↓ Cache Miss
┌─────────────────────────────────────┐
│         Redis Cache Layer           │
│     (Distributed, Session Data)     │
└─────────────────────────────────────┘
                 ↓ Cache Miss
┌─────────────────────────────────────┐
│        Database Query Layer         │
│    (PostgreSQL with Indexes)        │
└─────────────────────────────────────┘
```

### Cache Implementation

```python
# app/shared/cache.py
import json
from typing import Optional, Any
from functools import wraps
from app.config import get_redis_client

class CacheService:
    def __init__(self):
        self.redis = get_redis_client()
        self.default_ttl = 300  # 5 minutes
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = None
    ):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    async def delete(self, key: str):
        """Delete key from cache"""
        await self.redis.delete(key)
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

def cache_response(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching endpoint responses"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(kwargs)}"
            
            # Try to get from cache
            cache_service = CacheService()
            cached_value = await cache_service.get(cache_key)
            
            if cached_value:
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

### Usage Example

```python
@router.get("/articles/{article_id}")
@cache_response(ttl=600, key_prefix="article")
async def get_article(article_id: str):
    # This response will be cached for 10 minutes
    return service.get_article(article_id)
```

## Scalability

### Horizontal Scaling

```
┌─────────────────────────────────────────┐
│         Load Balancer (Nginx)           │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    ┌──────┐    ┌──────┐    ┌──────┐
    │ App  │    │ App  │    │ App  │
    │  1   │    │  2   │    │  3   │
    └──────┘    └──────┘    └──────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
    ┌─────────────────────────────────┐
    │    PostgreSQL (Primary)         │
    │    Redis (Primary)              │
    └─────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    ┌──────┐    ┌──────┐    ┌──────┐
    │  PG  │    │  PG  │    │ Redis│
    │Repli │    │Repli │    │Repli │
    │ ca 1 │    │ ca 2 │    │ ca 1 │
    └──────┘    └──────┘    └──────┘
```

### Database Scaling Strategies

1. **Read Replicas**: Direct read queries to replicas
2. **Connection Pooling**: Efficient connection management
3. **Query Optimization**: Indexes and query tuning
4. **Partitioning**: Table partitioning for large datasets

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Primary database (writes)
primary_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Read replica (reads)
replica_engine = create_engine(
    settings.DATABASE_REPLICA_URL,
    pool_size=30,
    max_overflow=20,
    pool_pre_ping=True
)

def get_db(read_only=False):
    engine = replica_engine if read_only else primary_engine
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Performance Optimization

### Query Optimization

```python
# Bad: N+1 Query Problem
articles = session.query(Article).all()
for article in articles:
    print(article.author.name)  # Separate query for each

# Good: Eager Loading
articles = session.query(Article).options(
    joinedload(Article.author),
    joinedload(Article.tags)
).all()
```

### Async Operations

```python
# app/shared/utils.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

async def run_in_executor(func, *args):
    """Run blocking function in executor"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

# Usage
result = await run_in_executor(blocking_function, arg1, arg2)
```

## Monitoring & Observability

### Logging Structure

```python
# app/shared/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger('app')
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Health Checks

```python
# app/routers/health.py
from fastapi import APIRouter, status
from app.database import engine
from app.config import get_redis_client

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}

@router.get("/health/db")
async def database_health():
    """Database health check"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy", "service": "database"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "database",
            "error": str(e)
        }

@router.get("/health/redis")
async def redis_health():
    """Redis health check"""
    try:
        redis = get_redis_client()
        await redis.ping()
        return {"status": "healthy", "service": "redis"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "redis",
            "error": str(e)
        }
```

---

## Conclusion

This architecture provides:
- **Modularity**: Easy to add/modify features
- **Scalability**: Horizontal scaling support
- **Maintainability**: Clear separation of concerns
- **Testability**: Dependency injection and isolated components
- **Performance**: Caching, async operations, query optimization
- **Security**: Multiple layers of protection
- **Observability**: Comprehensive logging and monitoring

For specific implementation details, refer to the codebase and module-specific documentation.

---

*Last Updated: January 31, 2025*