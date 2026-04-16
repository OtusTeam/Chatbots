from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings

engine: AsyncEngine = create_async_engine(settings.database_url, pool_pre_ping=True)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS bot_events (
                    id SERIAL PRIMARY KEY,
                    event_name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
            )
        )


async def record_event(event_name: str) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text("INSERT INTO bot_events (event_name) VALUES (:event_name)"),
            {"event_name": event_name},
        )


async def count_events() -> int:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM bot_events"))
        return int(result.scalar_one())


async def postgres_healthcheck() -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return result.scalar_one() == 1
