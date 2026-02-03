# Deployment Guide

## Overview

This guide covers deploying the AI Content Platform using Docker Compose or to the cloud (Render, Railway, Heroku, AWS, GCP). The platform is deployment-agnostic and runs anywhere Docker or Python is supported.

## Pre-Deployment Checklist

- Python 3.11+, PostgreSQL 15+, Redis 7+
- Gemini API key, SMTP credentials (optional)
- Environment variables configured
- Database migrations created
- All tests passing
- Security review completed

## Environment Configuration

Create a `.env.production` file with required variables:

```env
APP_NAME=AI Content Platform
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@db-host:5432/dbname
REDIS_URL=redis://redis-host:6379/0
SECRET_KEY=your-production-secret-key
GEMINI_API_KEY=your-gemini-api-key
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Docker Deployment

**Production Docker Compose Example:**

```yaml
version: "3.8"
services:
  app:
    build: .
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/var/app/uploads
  worker:
    build: .
    env_file:
      - .env.production
    command: python app/worker.py
    depends_on:
      - db
      - redis
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
volumes:
  postgres_data:
  redis_data:
```

**Production Dockerfile Example:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .
EXPOSE 8000
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Nginx Example:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /uploads/ {
        alias /var/app/uploads/;
    }
}
```

## Cloud Deployment (Render Example)

**1. Create `render.yaml`:**

```yaml
services:
  - type: web
    name: ai-content-platform
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: |
      alembic upgrade head &&
      uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ai-platform-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: ai-platform-redis
          type: redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: GEMINI_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
  - type: worker
    name: ai-platform-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app/worker.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ai-platform-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: ai-platform-redis
          type: redis
          property: connectionString
databases:
  - name: ai-platform-db
    databaseName: ai_content_platform
redis:
  - name: ai-platform-redis
```

**2. Deploy:**

- Push code to GitHub
- Connect repo in Render dashboard
- Add required environment variables (e.g., `GEMINI_API_KEY`)
- Deploy and monitor logs

**Other Platforms:**

- Railway, Heroku, AWS, GCP: Supported with similar steps (see code comments or platform docs)

## Database Setup

**Run migrations:**

```bash
alembic upgrade head
# or in Docker:
docker-compose exec app alembic upgrade head
```

## CI/CD Pipeline (Summary)

- Use GitHub Actions or similar for test/build/deploy
- Typical steps: checkout, install, lint, test, build, push, deploy, health check

## Monitoring & Logging

- Health check endpoint: `/health`
- Centralized logging (stdout, JSON)
- Metrics endpoint (Prometheus): `/metrics`

## Troubleshooting & Rollback

- Check logs: `docker-compose logs -f` or platform dashboard
- Common issues: DB/Redis connection, migration errors, out of memory
- Rollback: redeploy previous image or use platform rollback

## Deployment Checklist

- [ ] All tests passing
- [ ] Env vars configured
- [ ] Migrations applied
- [ ] SSL enabled (prod)
- [ ] Monitoring active
- [ ] Backups in place

## Support & Resources

- **Docs**: [Your docs URL]
- **Status Page**: [Your status page]
- **Support Email**: devops@yourdomain.com
