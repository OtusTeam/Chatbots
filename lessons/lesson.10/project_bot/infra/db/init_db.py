import asyncio
from infra.db import Base, engine
from app.models.db import UserDB, CareerProfileDB, MessageHistoryDB


async def init_db() -> None:
    print("Создаём таблицы в БД...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Готово: Таблицы созданы.")


if __name__ == '__main__':
    asyncio.run(init_db())