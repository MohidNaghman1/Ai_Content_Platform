import os
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from ai_content_platform.app.main import app
from ai_content_platform.app.database import Base
from ai_content_platform.app.shared.dependencies import get_db
from ai_content_platform.app.modules.users import models  # noqa

TEST_DB_PATH = "./test.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AsyncTestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False
)

async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # Only create tables, don't delete DB file at start
    async with engine.begin() as conn:
        print("CREATING TABLES:", Base.metadata.tables.keys())
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Dispose engine to close all connections
    await engine.dispose()
    # Now safely delete the DB file
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        print("Could not delete test.db, file still in use.")

@pytest.fixture(scope="function")
def client():
    print("TEST ROUTES:", [route.path for route in app.routes])
    return TestClient(app)