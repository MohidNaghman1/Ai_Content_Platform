import asyncio
from sqlalchemy import text
from ai_content_platform.app.database import engine
from ai_content_platform.app.config import settings


async def test_connection():
    print("Loaded settings:", settings.model_dump())

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())


if __name__ == "__main__":
    asyncio.run(test_connection())
