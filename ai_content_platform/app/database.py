"""
Database connection setup using SQLAlchemy async engine and sessionmaker.
Handles both async (app) and sync (alembic) DB URLs.
"""

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ai_content_platform.app.config import settings
from sqlalchemy.orm import declarative_base

Base = declarative_base()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set.")

# Render may provide 'postgres://' or 'postgresql://' so handle both
if DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
else:
    ASYNC_DATABASE_URL = DATABASE_URL


engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

SYNC_DATABASE_URL = DATABASE_URL
