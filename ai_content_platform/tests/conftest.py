from ai_content_platform.app.main import app as fastapi_app
import httpx
from ai_content_platform.app.modules.auth.models import Role
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
    alembic_cfg = Config(str(ALEMBIC_INI))
    command.upgrade(alembic_cfg, "head")


TEST_DB_PATH = "./test.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(app=fastapi_app, base_url="http://testserver") as c:
        yield c


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


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # Only create tables, don't delete DB file at start
    async with engine.begin() as conn:
        print("CREATING TABLES:", Base.metadata.tables.keys())
        await conn.run_sync(Base.metadata.create_all)
        # Insert required roles for tests
        await conn.execute(
            Role.__table__.insert(), [{"name": "admin"}, {"name": "viewer"}]
        )
        print("Inserted roles: admin, viewer")

        # Insert 'generate_content' permission and assign to admin role
        from ai_content_platform.app.modules.auth.models import (
            Permission,
            role_permissions,
        )

        # Insert permission if not exists
        result = await conn.execute(
            Permission.__table__.select().where(Permission.name == "generate_content")
        )
        perm = result.first()
        if not perm:
            perm_result = await conn.execute(
                Permission.__table__.insert()
                .values(name="generate_content", description="Can generate AI content")
                .returning(Permission.id)
            )
            perm_id = perm_result.scalar()
        else:
            perm_id = perm.id
        # Get admin role id
        result = await conn.execute(Role.__table__.select().where(Role.name == "admin"))
        admin_role = result.first()
        if admin_role:
            admin_role_id = admin_role.id
            # Assign permission to admin role if not already assigned
            rp_result = await conn.execute(
                role_permissions.select().where(
                    (role_permissions.c.role_id == admin_role_id)
                    & (role_permissions.c.permission_id == perm_id)
                )
            )
            if not rp_result.first():
                await conn.execute(
                    role_permissions.insert().values(
                        role_id=admin_role_id, permission_id=perm_id
                    )
                )
        print("Assigned 'generate_content' permission to admin role.")
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
