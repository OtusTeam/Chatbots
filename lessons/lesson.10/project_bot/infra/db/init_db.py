import asyncio

from infra.db import engine, Base

from app.models.db.user import UserDB
from app.models.db.career_profile import CareerProfileDB
from app.models.db.message_history import MessageHistoryDB


async def init_db() -> None:
    print("Создаём таблицы в базе данных")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Готово -  таблицы в базе данных созданы")


if __name__ == '__main__':
    asyncio.run(init_db())