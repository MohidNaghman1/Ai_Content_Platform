from ai_content_platform.app.main import app as fastapi_app
import httpx
from ai_content_platform.app.shared.dependencies import get_db
from ai_content_platform.app.database import Base
from ai_content_platform.app.main import app
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import pytest_asyncio
from alembic import command
from alembic.config import Config
import pytest
from pathlib import Path
import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

BASE_DIR = Path(__file__).resolve().parents[1]  # ai_content_platform/
ALEMBIC_INI = BASE_DIR / "alembic.ini"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    db_path = Path("test.db")
    if db_path.exists():
        db_path.unlink()

    alembic_cfg = Config(str(ALEMBIC_INI))
    alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///./test.db")
    command.upgrade(alembic_cfg, "head")


TEST_DB_PATH = "./test.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AsyncTestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(app=fastapi_app, base_url="http://testserver") as c:
        yield c
