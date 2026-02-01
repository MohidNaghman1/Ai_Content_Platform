# Deployment Guide

## Table of Contents

- [Overview](#overview)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Environment Configuration](#environment-configuration)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
  - [Render](#deploying-to-render)
  - [Railway](#deploying-to-railway)
  - [Heroku](#deploying-to-heroku)
  - [AWS](#deploying-to-aws)
  - [Google Cloud Platform](#deploying-to-google-cloud-platform)
- [Database Setup](#database-setup)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

## Overview

This guide covers deploying the AI Content Platform to various environments, from local Docker setups to cloud platforms. The platform is designed to be deployment-agnostic and can run on any infrastructure that supports Docker or Python applications.

### Deployment Options

1. **Docker Compose** - For local development and small deployments
2. **Render** - Easiest cloud deployment with automatic builds
3. **Railway** - Modern platform with simple CLI deployment
4. **Heroku** - Mature platform with extensive add-ons
5. **AWS/GCP/Azure** - Enterprise-grade cloud infrastructure
6. **Kubernetes** - Container orchestration for large scale

## Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] Python 3.11+ installed
- [ ] PostgreSQL 15+ database provisioned
- [ ] Redis 7+ instance provisioned
- [ ] Google Gemini API key obtained
- [ ] SMTP credentials (optional, for email notifications)
- [ ] Domain name configured (optional)
- [ ] SSL certificate (required for production)
- [ ] Environment variables configured
- [ ] Database migrations created
- [ ] All tests passing
- [ ] Security review completed

### Security Checklist

- [ ] `SECRET_KEY` is strong and unique (32+ characters)
- [ ] Database passwords are strong
- [ ] Debug mode disabled in production
- [ ] CORS origins properly configured
- [ ] Rate limiting enabled
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] API keys stored securely (not in code)
- [ ] Input validation implemented
- [ ] SQL injection protection verified

## Environment Configuration

### Production Environment Variables

Create a `.env.production` file:

```env
# ============================================
# Application Settings
# ============================================
APP_NAME=AI Content Platform
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1

# ============================================
# Server Configuration
# ============================================
HOST=0.0.0.0
PORT=8000
WORKERS=4  # (2 * CPU cores) + 1
RELOAD=False

# ============================================
# Database Configuration
# ============================================
DATABASE_URL=postgresql://user:password@db-host:5432/dbname
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ============================================
# Redis Configuration
# ============================================
REDIS_URL=redis://redis-host:6379/0
REDIS_MAX_CONNECTIONS=50

# ============================================
# Authentication & Security
# ============================================
SECRET_KEY=your-production-secret-key-min-32-chars-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# AI Configuration
# ============================================
GEMINI_API_KEY=your-production-gemini-api-key
AI_MODEL=gemini-pro
MAX_TOKENS_PER_USER=100000

# ============================================
# CORS Configuration
# ============================================
CORS_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]
CORS_CREDENTIALS=True

# ============================================
# Email Configuration
# ============================================
SMTP_ENABLED=True
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# ============================================
# Rate Limiting
# ============================================
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ============================================
# File Upload
# ============================================
MAX_UPLOAD_SIZE=5242880  # 5MB
UPLOAD_DIR=/var/app/uploads/
```

### Environment-Specific Configurations

**Development**:

```env
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
RELOAD=True
```

**Staging**:

```env
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=INFO
RELOAD=False
```

**Production**:

```env
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
RELOAD=False
```

## Docker Deployment

### Docker Compose Production Setup

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: ai-platform-app
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/var/app/uploads
      - ./logs:/var/app/logs
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  worker:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: ai-platform-worker
    restart: always
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    command: python app/worker.py
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    container_name: ai-platform-db
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ai-platform-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: ai-platform-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### Production Dockerfile

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /var/app/uploads /var/app/logs && \
    chown -R appuser:appuser /var/app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start application
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Client max body size
        client_max_body_size 10M;

        # Proxy settings
        location / {
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Static files
        location /uploads/ {
            alias /var/app/uploads/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://app/health;
        }
    }
}
```

### Deploy with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Run migrations
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head

# Create admin user
docker-compose -f docker-compose.prod.yml exec app python scripts/create_admin.py

# Stop services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (destructive!)
docker-compose -f docker-compose.prod.yml down -v
```

## Cloud Platforms

## Deploying to Render

### Prerequisites

- GitHub account
- Render account ([render.com](https://render.com))

### Step 1: Create `render.yaml`

```yaml
# render.yaml
services:
  # Web Service
  - type: web
    name: ai-content-platform
    env: python
    region: oregon
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: |
      alembic upgrade head &&
      uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
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
      - key: DEBUG
        value: false

  # Background Worker
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
  # PostgreSQL Database
  - name: ai-platform-db
    databaseName: ai_content_platform
    plan: starter
    region: oregon
    ipAllowList: []

# Redis Instance
redis:
  - name: ai-platform-redis
    plan: starter
    region: oregon
    maxmemoryPolicy: allkeys-lru
```

### Step 2: Deploy to Render

1. **Connect Repository**:

   ```bash
   # Push code to GitHub
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create New Web Service**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically

3. **Configure Environment Variables**:
   - In Render Dashboard, go to your service
   - Navigate to "Environment" tab
   - Add required variables:
     - `GEMINI_API_KEY`: Your Gemini API key
     - `SMTP_USER`: Email username (optional)
     - `SMTP_PASSWORD`: Email password (optional)

4. **Deploy**:
   - Render automatically builds and deploys
   - Monitor logs in the "Logs" tab
   - Access your app at: `https://your-service.onrender.com`

### Step 3: Run Migrations

```bash
# Using Render Shell
# Go to Shell tab in Render Dashboard
alembic upgrade head

# Create admin user
python scripts/create_admin.py
```

### Render Deployment Notes

- **Automatic Deploys**: Enabled by default on push to main
- **Health Checks**: Render automatically configures
- **HTTPS**: Automatically provided with free SSL certificate
- **Custom Domain**: Can be configured in Render settings
- **Scaling**: Upgrade plan for more instances

## Deploying to Railway

### Prerequisites

- GitHub account
- Railway account ([railway.app](https://railway.app))
- Railway CLI (optional)

### Option 1: Deploy via Dashboard

1. **Connect GitHub**:
   - Go to Railway Dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Add Services**:
   - Click "Add Service" → "Database" → PostgreSQL
   - Click "Add Service" → "Database" → Redis
   - Services are automatically configured

3. **Configure Variables**:
   - Click on your app service
   - Go to "Variables" tab
   - Add required environment variables

4. **Deploy**:
   - Railway automatically builds and deploys
   - Access logs in the "Deployments" tab

### Option 2: Deploy via CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project (optional)
railway link [project-id]

# Add PostgreSQL
railway add --database postgresql

# Add Redis
railway add --database redis

# Set environment variables
railway variables set GEMINI_API_KEY=your-key
railway variables set SECRET_KEY=your-secret
railway variables set ENVIRONMENT=production

# Deploy
railway up

# Run migrations
railway run alembic upgrade head

# Open application
railway open

# View logs
railway logs
```

### Railway Configuration File

```toml
# railway.toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[healthcheck]
path = "/health"
timeout = 100
interval = 60
```

### Railway Tips

- **Auto-scaling**: Available on Pro plan
- **Custom Domains**: Free on all plans
- **Automatic HTTPS**: Provided by default
- **Database Backups**: Automatic on paid plans
- **Metrics**: View in dashboard

## Deploying to Heroku

### Prerequisites

- Heroku account
- Heroku CLI installed

### Step 1: Create Heroku App

```bash
# Login to Heroku
heroku login

# Create new app
heroku create ai-content-platform

# Or use existing app
heroku git:remote -a ai-content-platform
```

### Step 2: Add Buildpack

```bash
# Set Python buildpack
heroku buildpacks:set heroku/python
```

### Step 3: Create `Procfile`

```procfile
# Procfile
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
worker: python app/worker.py
```

### Step 4: Create `runtime.txt`

```
python-3.11.0
```

### Step 5: Add Add-ons

```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:hobby-dev

# Add Papertrail for logging (optional)
heroku addons:create papertrail:choklad
```

### Step 6: Configure Environment Variables

```bash
# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set GEMINI_API_KEY=your-gemini-api-key
heroku config:set ALGORITHM=HS256
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP Configuration (optional)
heroku config:set SMTP_HOST=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USER=your-email@gmail.com
heroku config:set SMTP_PASSWORD=your-app-password

# View all config
heroku config
```

### Step 7: Deploy

```bash
# Deploy to Heroku
git push heroku main

# Run migrations
heroku run alembic upgrade head

# Create admin user
heroku run python scripts/create_admin.py

# Scale worker dyno
heroku ps:scale worker=1

# View logs
heroku logs --tail

# Open app
heroku open
```

### Heroku Tips

- **Custom Domain**: `heroku domains:add yourdomain.com`
- **SSL**: Automatic with paid dynos
- **Database Backups**: `heroku pg:backups:capture`
- **Monitor**: `heroku ps` to check dyno status
- **Restart**: `heroku restart` to restart dynos

## Deploying to AWS

### AWS Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│              Application Load Balancer           │
│                 (HTTPS/SSL)                      │
└─────────────────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐    ┌────────┐    ┌────────┐
    │  ECS   │    │  ECS   │    │  ECS   │
    │ Task 1 │    │ Task 2 │    │ Task 3 │
    └────────┘    └────────┘    └────────┘
         │             │             │
         └─────────────┼─────────────┘
                       ▼
         ┌─────────────────────────────┐
         │      RDS PostgreSQL         │
         │      ElastiCache Redis      │
         └─────────────────────────────┘
```

### Step 1: Create ECR Repository

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name ai-content-platform

# Build and tag image
docker build -t ai-content-platform:latest .
docker tag ai-content-platform:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-content-platform:latest

# Push image
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-content-platform:latest
```

### Step 2: Create RDS Database

```bash
# Create PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier ai-platform-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password YourSecurePassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-12345678 \
  --db-subnet-group-name my-db-subnet-group
```

### Step 3: Create ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id ai-platform-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1 \
  --security-group-ids sg-12345678
```

### Step 4: Create ECS Task Definition

```json
{
  "family": "ai-content-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-content-platform:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "ENVIRONMENT", "value": "production" },
        { "name": "DEBUG", "value": "False" }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-content-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "app"
        }
      }
    }
  ]
}
```

### Step 5: Create ECS Service

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name ai-platform-cluster

# Create service
aws ecs create-service \
  --cluster ai-platform-cluster \
  --service-name ai-platform-service \
  --task-definition ai-content-platform:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678],securityGroups=[sg-12345678],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=app,containerPort=8000
```

### AWS Terraform Example

```hcl
# terraform/main.tf
provider "aws" {
  region = "us-east-1"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "ai-platform-cluster"
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "ai-platform-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnets
}

# RDS Instance
resource "aws_db_instance" "postgres" {
  identifier        = "ai-platform-db"
  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  db_name           = "ai_content_platform"
  username          = var.db_username
  password          = var.db_password

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  skip_final_snapshot = false
  final_snapshot_identifier = "ai-platform-final-snapshot"
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "ai-platform-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  security_group_ids   = [aws_security_group.redis.id]
  subnet_group_name    = aws_elasticache_subnet_group.main.name
}
```

## Deploying to Google Cloud Platform

### GCP Deployment using Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-content-platform

# Deploy to Cloud Run
gcloud run deploy ai-content-platform \
  --image gcr.io/PROJECT_ID/ai-content-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production,DEBUG=False" \
  --set-secrets="DATABASE_URL=db-url:latest,SECRET_KEY=secret-key:latest"

# Create Cloud SQL PostgreSQL
gcloud sql instances create ai-platform-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create Redis instance
gcloud redis instances create ai-platform-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

## Database Setup

### Running Migrations

```bash
# Development
alembic upgrade head

# Production (Docker)
docker-compose exec app alembic upgrade head

# Production (Render/Railway)
# Use platform's shell or run command feature
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Create new migration
alembic revision --autogenerate -m "description"
```

### Database Backup

```bash
# PostgreSQL Backup
pg_dump -U username -h hostname -d database_name > backup.sql

# Restore from backup
psql -U username -h hostname -d database_name < backup.sql

# AWS RDS Backup
aws rds create-db-snapshot \
  --db-instance-identifier ai-platform-db \
  --db-snapshot-identifier ai-platform-snapshot-$(date +%Y%m%d)

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="ai_content_platform"

pg_dump $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          flake8 app/ tests/
          black --check app/ tests/

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ secrets.REGISTRY_URL }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./Dockerfile.prod
          push: true
          tags: |
            ${{ secrets.REGISTRY_URL }}/ai-content-platform:latest
            ${{ secrets.REGISTRY_URL }}/ai-content-platform:${{ github.sha }}
          cache-from: type=registry,ref=${{ secrets.REGISTRY_URL }}/ai-content-platform:buildcache
          cache-to: type=registry,ref=${{ secrets.REGISTRY_URL }}/ai-content-platform:buildcache,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
          RENDER_SERVICE_ID: ${{ secrets.RENDER_SERVICE_ID }}
        run: |
          curl -X POST \
            "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json"

      - name: Wait for deployment
        run: sleep 60

      - name: Health check
        run: |
          curl -f https://your-app.onrender.com/health || exit 1

      - name: Notify success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "Deployment successful! :rocket:"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Monitoring & Logging

### Application Metrics

```python
# app/shared/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import generate_latest
from fastapi import Response

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

ai_tokens_used = Counter(
    'ai_tokens_used_total',
    'Total AI tokens used',
    ['user_id']
)

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Centralized Logging

```python
# app/shared/logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

# Configure logging
handler = logging.StreamHandler()
formatter = CustomJsonFormatter()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Health Check Monitoring

```bash
# Add to crontab for periodic health checks
*/5 * * * * curl -f https://your-app.com/health || echo "Health check failed"

# UptimeRobot configuration
# Create monitor with 5-minute intervals
# Set alert contacts for downtime notifications
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Verify connection pool settings
# Increase pool size if seeing connection errors

# Check for connection leaks
# Monitor active connections in PostgreSQL
SELECT count(*) FROM pg_stat_activity;
```

#### Redis Connection Errors

```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping

# Check Redis memory usage
redis-cli -u $REDIS_URL info memory

# Clear Redis cache if needed
redis-cli -u $REDIS_URL FLUSHALL
```

#### Migration Failures

```bash
# Check current migration version
alembic current

# Rollback failed migration
alembic downgrade -1

# Fix migration and retry
alembic upgrade head

# If completely stuck, stamp the version
alembic stamp head
```

#### Out of Memory Errors

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G

# Optimize worker count
# Workers = (2 * CPU cores) + 1
```

#### Slow API Response

```bash
# Enable query logging
# Add to database.py
engine = create_engine(DATABASE_URL, echo=True)

# Check for missing indexes
# Add indexes for frequently queried columns

# Enable caching
# Use Redis for frequently accessed data

# Profile slow endpoints
# Use middleware to log request times
```

### Debug Mode

```bash
# Enable debug mode temporarily
export DEBUG=True
export LOG_LEVEL=DEBUG

# View detailed logs
docker-compose logs -f --tail=100

# Interactive debugging
docker-compose exec app python
>>> from app.database import engine
>>> engine.execute("SELECT version()").scalar()
```

## Rollback Procedures

### Application Rollback

```bash
# Docker deployment
# Deploy previous version
docker-compose pull  # Pull previous image
docker-compose up -d

# Render/Railway
# Use platform's UI to rollback to previous deployment

# Heroku
heroku releases
heroku rollback v123
```

### Database Rollback

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# Restore from backup
psql $DATABASE_URL < backup.sql
```

### Emergency Procedures

```bash
# 1. Stop accepting traffic
# Update load balancer or set maintenance mode

# 2. Assess the situation
# Check logs, metrics, database status

# 3. Rollback application
# Use deployment platform's rollback feature

# 4. Rollback database if needed
# Only if schema changes caused issues

# 5. Verify functionality
curl https://your-app.com/health

# 6. Resume traffic
# Remove maintenance mode
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code review completed
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] SSL certificates ready
- [ ] Backup procedures in place
- [ ] Monitoring configured
- [ ] Load testing completed
- [ ] Security scan passed

### During Deployment

- [ ] Notify team of deployment
- [ ] Enable maintenance mode (if needed)
- [ ] Deploy database migrations
- [ ] Deploy application
- [ ] Run smoke tests
- [ ] Check health endpoints
- [ ] Verify metrics/logs
- [ ] Disable maintenance mode

### Post-Deployment

- [ ] Monitor error rates
- [ ] Check application metrics
- [ ] Verify database performance
- [ ] Test critical user flows
- [ ] Update documentation
- [ ] Notify stakeholders
- [ ] Create deployment notes

---

## Support & Resources

- **Documentation**: [Your docs URL]
- **Status Page**: [Your status page]
- **Support Email**: devops@yourdomain.com
- **Emergency Hotline**: +1-XXX-XXX-XXXX

---

_Last Updated: January 31, 2025_
