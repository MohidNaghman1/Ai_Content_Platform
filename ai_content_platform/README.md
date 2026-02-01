# AI Content Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D.svg)](https://redis.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A production-ready, AI-powered content management platform with intelligent chat capabilities, event-driven notifications, and comprehensive admin controls.

## 🌟 Overview

AI Content Platform is a sophisticated backend system demonstrating modern software architecture patterns and AI integration. Built for scalability and maintainability, it showcases modular design, event-driven architecture, and production-grade deployment practices.

**Key Highlights:**
- 🤖 AI-powered content generation and summarization using Google Gemini
- 💬 Intelligent chat assistant with conversation memory
- 🔐 Enterprise-grade authentication with JWT and OAuth2
- 🔔 Event-driven notification system using Redis
- 📊 Comprehensive admin dashboard with analytics
- 🐳 Fully containerized with Docker
- 🚀 Production-ready deployment configurations

**Live Demo**: [Your Render/Railway URL]  
**API Documentation**: [Your URL]/docs  
**Video Walkthrough**: [Your YouTube/Loom Link]

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔐 User Management Module
- **JWT-based Authentication**: Secure token-based authentication with refresh tokens
- **OAuth2 Compliance**: Industry-standard authorization framework
- **Role-Based Access Control (RBAC)**: Three-tier permission system (Admin, Creator, Viewer)
- **User Profiles**: Complete profile management with avatar upload
- **Password Security**: bcrypt hashing with configurable salt rounds
- **Session Management**: Token blacklisting and concurrent session handling

### 📝 Content Module
- **Full CRUD Operations**: Create, read, update, and delete articles
- **AI Content Generation**: Generate high-quality content using Gemini AI
- **Intelligent Summarization**: Automatic summarization of long-form content
- **Flexible Tag System**: Many-to-many relationship for categorization
- **Full-Text Search**: PostgreSQL-powered search with ranking
- **Content Versioning**: Track changes and maintain history
- **Draft Management**: Save and publish workflow
- **Rich Text Support**: Markdown and HTML content

### 💬 AI Chat Module
- **Personal AI Assistant**: Dedicated assistant for each user
- **Persistent Conversations**: Full conversation history storage
- **Streaming Responses**: Real-time response delivery
- **Context-Aware Chat**: Maintains conversation context across sessions
- **Token Usage Tracking**: Monitor and limit AI API usage
- **Multi-Turn Dialogue**: Complex conversation flows
- **Conversation Branching**: Fork conversations at any point
- **Export Capabilities**: Download conversation history

### 🔔 Notification System
- **Event-Driven Architecture**: Redis-based message queue
- **Email Notifications**: SMTP integration with templates
- **In-App Notifications**: Real-time notification center
- **User Preferences**: Granular notification settings
- **Notification Templates**: Reusable, customizable templates
- **Delivery Tracking**: Monitor notification status
- **Batch Processing**: Efficient bulk notification handling
- **Priority Queue**: Urgent vs. normal notification routing

### 📊 Admin Dashboard
- **User Management**: Complete CRUD operations for users
- **Role Assignment**: Dynamic role and permission management
- **Content Moderation**: AI-assisted content review
- **Analytics Dashboard**: 
  - User growth metrics
  - Content creation trends
  - AI usage statistics
  - System performance metrics
- **System Health Monitoring**: Database, Redis, and API health checks
- **Audit Logging**: Complete activity trail for compliance
- **Usage Reports**: Exportable analytics and reports
- **Bulk Operations**: Mass user/content management

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                        │
│                    (FastAPI + Middleware)                       │
│  [CORS] [Auth] [Rate Limiting] [Logging] [Error Handling]     │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
         ┌──────────┐   ┌──────────┐   ┌──────────┐
         │   Auth   │   │ Content  │   │   Chat   │
         │  Module  │   │  Module  │   │  Module  │
         └──────────┘   └──────────┘   └──────────┘
                │             │             │
         ┌──────────┐   ┌──────────┐   ┌──────────┐
         │  Users   │   │  Notif.  │   │  Admin   │
         │  Module  │   │  Module  │   │  Module  │
         └──────────┘   └──────────┘   └──────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                  ┌───────────────────────┐
                  │   Service Layer       │
                  │  (Business Logic)     │
                  │  • Validation         │
                  │  • Authorization      │
                  │  • Event Publishing   │
                  └───────────────────────┘
                              │
                  ┌───────────┼───────────┐
                  ▼           ▼           ▼
            ┌──────────┐ ┌────────┐ ┌────────┐
            │Repository│ │ Events │ │   AI   │
            │  Layer   │ │ Layer  │ │ Layer  │
            └──────────┘ └────────┘ └────────┘
                  │           │           │
        ┌─────────┼───────────┼───────────┼─────────┐
        ▼         ▼           ▼           ▼         ▼
  ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │PostgreSQL│ │ Redis  │ │ Redis  │ │Gemini  │ │  SMTP  │
  │    DB    │ │ Cache  │ │ Queue  │ │   AI   │ │ Server │
  └──────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

### Design Patterns & Principles

- **Repository Pattern**: Abstracts data access logic from business logic
- **Service Layer Pattern**: Encapsulates business logic and orchestration
- **Dependency Injection**: Promotes loose coupling and testability
- **Event-Driven Architecture**: Asynchronous, decoupled communication
- **Factory Pattern**: Centralized object creation
- **Observer Pattern**: Event subscription and notification
- **SOLID Principles**: Clean, maintainable code architecture
- **Clean Architecture**: Separation of concerns across layers

## 🛠️ Tech Stack

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.104+ | High-performance async web framework |
| **Python** | 3.11+ | Primary programming language |
| **Pydantic** | 2.0+ | Data validation and settings management |
| **Uvicorn** | 0.24+ | ASGI server implementation |

### Database & Caching
| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 15+ | Primary relational database |
| **SQLAlchemy** | 2.0+ | ORM and database toolkit |
| **Alembic** | 1.12+ | Database migration tool |
| **Redis** | 7+ | Caching and message queue |

### AI & External Services
| Technology | Version | Purpose |
|------------|---------|---------|
| **Google Gemini** | Latest | AI content generation and chat |
| **python-jose** | 3.3+ | JWT token handling |
| **passlib** | 1.7+ | Password hashing |
| **aiosmtplib** | 3.0+ | Async email sending |

### DevOps & Deployment
| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | 24+ | Containerization |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **GitHub Actions** | - | CI/CD pipeline |
| **Render/Railway** | - | Cloud deployment platform |


## 📁 Project Structure

```
ai_content_platform/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection & session
│   ├── worker.py                  # Background task worker
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   │
│   │   ├── auth/                  # Authentication & Authorization
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # User, Token models
│   │   │   ├── schemas.py         # Pydantic schemas
│   │   │   ├── service.py         # Business logic
│   │   │   ├── router.py          # API endpoints
│   │   │   └── dependencies.py    # Auth dependencies
│   │   │
│   │   ├── users/                 # User Management
│   │   │   ├── models.py          # UserProfile model
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   │
│   │   ├── content/               # Content/Articles
│   │   │   ├── models.py          # Article, Tag models
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── ai_service.py      # AI generation/summarization
│   │   │
│   │   ├── chat/                  # AI Chat Functionality
│   │   │   ├── models.py          # Conversation, Message models
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── ai_client.py       # Gemini integration
│   │   │
│   │   ├── notifications/         # Notification System
│   │   │   ├── models.py          # Notification model
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── templates/         # Email templates
│   │   │
│   │   └── admin/                 # Admin Dashboard
│   │       ├── schemas.py
│   │       ├── service.py
│   │       ├── router.py
│   │
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Shared dependencies
│   │   ├── middleware.py          # Custom middleware
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── utils.py               # Utility functions
│   │
│   └── events/
│       ├── __init__.py
│       ├── publisher.py           # Event publishing
│       ├── subscriber.py          # Event subscription
│       ├── types.py               # Event type definitions
│       └── handlers/              # Event handlers
│           ├── __init__.py
│           ├── user_events.py
│           ├── content_events.py
│           └── notification_events.py
│
├── alembic/                       # Database Migrations
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_users.py
│   │   └── ...
│   ├── env.py
│   ├── script.py.mako
│   └── README
│
├── tests/                         # Test Suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   │
│   │   ├── test_auth.py
│   │   ├── test_content.py
│   │   ├── test_chat.py
│   │   └── ...
│
├── docs/                         # Documentation
│   ├── API.md                    # API documentation
│   ├── ARCHITECTURE.md           # Architecture details
│   ├── DEPLOYMENT.md             # Deployment guide
├── .github/
│   └── workflows/
│       ├── ci-cd.yml            # Main CI/CD pipeline
│       ├── tests.yml            # Test workflow
│       └── deploy.yml           # Deployment workflow
│
├── docker-compose.yml            # Docker orchestration
├── Dockerfile                    # Container definition
├── render.yaml                   # Render deployment config
├── railway.json                  # Railway deployment config
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitignore
├── .dockerignore
├── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Redis 7+** - [Download Redis](https://redis.io/download)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Docker & Docker Compose** (optional but recommended) - [Download Docker](https://www.docker.com/products/docker-desktop)

### API Keys Required

- **Google Gemini API Key** - [Get API Key](https://makersuite.google.com/app/apikey)
- **SMTP Credentials** (optional for email notifications)

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-content-platform.git
   cd ai-content-platform
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (see Configuration section)
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

5. **Create admin user** (in a new terminal)
   ```bash
   docker-compose exec app python scripts/create_admin.py
   ```

### Local Development Setup (Without Docker)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-content-platform.git
   cd ai-content-platform
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb ai_content_platform

   # Or using psql
   psql -U postgres
   CREATE DATABASE ai_content_platform;
   \q
   ```

5. **Set up Redis**
   ```bash
   # Start Redis server (varies by OS)
   redis-server
   ```

6. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and API credentials
   ```

7. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

8. **Seed the database** (optional)
   ```bash
   python scripts/seed_db.py
   ```

9. **Create admin user**
   ```bash
   python scripts/create_admin.py
   ```

10. **Start the application**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

11. **Start the background worker** (in a new terminal)
    ```bash
    python app/worker.py
    ```

12. **Access the application**
    - API: http://localhost:8000
    - API Documentation: http://localhost:8000/docs

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following configuration:

```env

# ============================================
# Database Configuration
# ============================================
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost  # Use 'db' for Docker
DB_PORT=5432
DB_NAME=ai_content_platform
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}


# ============================================
# Redis Configuration
# ============================================
REDIS_HOST=localhost  # Use 'redis' for Docker
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}

# Authentication & Security
# ============================================
SECRET_KEY=your-secret-key-min-32-characters-long-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7


# ============================================
# AI Configuration (Google Gemini)
# ============================================
GEMINI_API_KEY=your-gemini-api-key-here



### Configuration Validation

The application validates all environment variables on startup. Required variables:

- `SECRET_KEY`: Must be at least 32 characters
- `DATABASE_URL`: Must be a valid PostgreSQL connection string
- `REDIS_URL`: Must be a valid Redis connection string
- `GEMINI_API_KEY`: Required if AI features are enabled

## 📚 API Documentation

### Interactive Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs


### Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Quick API Reference

#### Authentication Endpoints

```http
POST   /api/v1/auth/register          # Register new user
POST   /api/v1/auth/login             # Login and get tokens
POST   /api/v1/auth/refresh           # Refresh access token
POST   /api/v1/auth/logout            # Logout (invalidate token)
GET    /api/v1/auth/me                # Get current user
PUT    /api/v1/auth/change-password   # Change password
```

#### User Endpoints

```http
GET    /api/v1/users                  # List all users (admin)
GET    /api/v1/users/{id}             # Get user by ID
PUT    /api/v1/users/{id}             # Update user
DELETE /api/v1/users/{id}             # Delete user (admin)
POST   /api/v1/users/{id}/avatar      # Upload avatar
```

#### Content Endpoints

```http
GET    /api/v1/content/articles       # List articles (with pagination)
POST   /api/v1/content/articles       # Create article
GET    /api/v1/content/articles/{id}  # Get article
PUT    /api/v1/content/articles/{id}  # Update article
DELETE /api/v1/content/articles/{id}  # Delete article
POST   /api/v1/content/generate       # AI generate content
POST   /api/v1/content/summarize      # AI summarize text
GET    /api/v1/content/search         # Search articles
GET    /api/v1/content/tags           # List all tags
```

#### Chat Endpoints

```http
POST   /api/v1/chat/conversations     # Create conversation
GET    /api/v1/chat/conversations     # List conversations
GET    /api/v1/chat/conversations/{id}# Get conversation
DELETE /api/v1/chat/conversations/{id}# Delete conversation
POST   /api/v1/chat/message           # Send message
GET    /api/v1/chat/history/{id}      # Get conversation history
POST   /api/v1/chat/stream            # Stream chat response
```

#### Notification Endpoints

```http
GET    /api/v1/notifications          # Get user notifications
PUT    /api/v1/notifications/{id}/read# Mark as read
DELETE /api/v1/notifications/{id}     # Delete notification
POST   /api/v1/notifications/preferences # Update preferences
```

#### Admin Endpoints

```http
GET    /api/v1/admin/users            # User management
PUT    /api/v1/admin/users/{id}/role  # Update user role
GET    /api/v1/admin/analytics        # Get analytics
GET    /api/v1/admin/content/moderate # Content moderation queue
POST   /api/v1/admin/content/{id}/approve # Approve content
GET    /api/v1/admin/system/health    # System health status
GET    /api/v1/admin/logs             # System logs
```

For detailed request/response schemas, see [API.md](docs/API.md).


## 🚢 Deployment

### Docker Deployment

#### Build and Run

```bash
# Build the image
docker build -t ai-content-platform:latest .

# Run the container
docker run -d \
  --name ai-platform \
  -p 8000:8000 \
  --env-file .env \
  ai-content-platform:latest

# Check logs
docker logs -f ai-platform

# Stop the container
docker stop ai-platform
```

#### Docker Compose (Production)

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Cloud Deployment

#### Render

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Use `render.yaml` configuration (already included)
   - Set environment variables in Render dashboard

3. **Deploy**
   - Render will automatically deploy on push to main branch

## 🔒 Security

### Security Features

- ✅ **Password Hashing**: bcrypt with configurable rounds
- ✅ **JWT Tokens**: Secure token generation with expiration
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- ✅ **XSS Protection**: Input validation and sanitization with Pydantic
- ✅ **CSRF Protection**: Token-based validation
- ✅ **CORS**: Configurable allowed origins
- ✅ **Rate Limiting**: Redis-based request throttling
- ✅ **Environment Variables**: Sensitive data protection
- ✅ **HTTPS**: TLS/SSL encryption (in production)
- ✅ **Input Validation**: Strict schema validation
- ✅ **Role-Based Access**: Permission-based authorization

### Security Best Practices

1. **Never commit `.env` files**
2. **Use strong, unique SECRET_KEY** (minimum 32 characters)
3. **Enable HTTPS** in production
4. **Regularly update dependencies**
5. **Implement rate limiting**
6. **Use prepared statements** (automatically done by SQLAlchemy)
7. **Validate all user inputs**
8. **Sanitize HTML content**
9. **Log security events**
10. **Regular security audits**

### Security Headers

The application automatically adds security headers:

```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Health Checks

```bash
# Application health
GET /health

# Database health
GET /health/db

# Redis health
GET /health/redis

# Complete system health
GET /health/system
```

### Metrics

If enabled, metrics are exposed at:

```
GET /metrics
```

Includes:
- Request count and latency
- Database connection pool stats
- Redis connection stats
- AI token usage
- Error rates

## 🤝 Contributing

We welcome contributions! Please follow these steps:

### Development Workflow

1. **Fork the repository**
   ```bash
   gh repo fork yourusername/ai-content-platform
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Install dev dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

4. **Make your changes**
   - Write clean, documented code
   - Follow PEP 8 style guide
   - Add/update tests
   - Update documentation

5. **Run tests and linting**
   ```bash
   # Format code
   black app/ tests/
   
   # Lint code
   flake8 app/ tests/
   
   # Type checking
   mypy app/
   
   # Run tests
   pytest --cov=app
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `test:` Tests
   - `refactor:` Code refactoring
   - `style:` Formatting
   - `chore:` Maintenance

7. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

8. **Open a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Ensure all checks pass



## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com
- Website: https://yourwebsite.com

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The amazing web framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI capabilities
- [PostgreSQL](https://www.postgresql.org/) - Robust database system
- [Redis](https://redis.io/) - High-performance caching
- The open-source community for inspiration and tools
