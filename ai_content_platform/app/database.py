"""
Database connection setup using SQLAlchemy async engine and sessionmaker.
Handles both async (app) and sync (alembic) DB URLs.
"""
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from sqlalchemy.orm import declarative_base

Base = declarative_base()

ENCODED_PASSWORD = urllib.parse.quote_plus(settings.DB_PASSWORD)

ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{ENCODED_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
)

SYNC_DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{ENCODED_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
