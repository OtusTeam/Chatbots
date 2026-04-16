import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, Update
from fastapi import FastAPI, Request, Response, status

from app.cache.redis import (
    get_user_counter,
    increment_user_counter,
    redis_client,
    redis_healthcheck,
)
from app.config import settings
from app.storage.postgres import count_events, init_db, postgres_healthcheck, record_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()
router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    await increment_user_counter(user_id)
    await record_event("start_command")
    await message.answer(
        "Бот lesson.32 активен.\n"
        "Использует PostgreSQL (события) и Redis (счетчик сообщений).\n"
        "Команды: /start, /stats"
    )


@router.message(lambda msg: msg.text and msg.text.strip() == "/stats")
async def stats_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    user_count = await get_user_counter(user_id)
    total_events = await count_events()
    await message.answer(
        f"Ваш счетчик сообщений в Redis: {user_count}\n"
        f"Всего событий в PostgreSQL: {total_events}"
    )


@router.message()
async def echo_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    count = await increment_user_counter(user_id)
    await record_event("message")
    await message.answer(f"Echo: {message.text}\nСообщений от вас: {count}")


dp.include_router(router)


async def setup_webhook() -> None:
    await bot.set_webhook(settings.webhook_url)
    logger.info("Webhook configured: %s", settings.webhook_url)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await setup_webhook()
    yield
    await bot.session.close()
    await redis_client.close()


app = FastAPI(title="Lesson 32 Bot", lifespan=lifespan)


@app.post(settings.webhook_path)
async def webhook_handler(request: Request) -> Response:
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return Response(status_code=status.HTTP_200_OK)
    except Exception:
        logger.exception("Webhook processing error")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/health")
async def healthcheck() -> dict:
    postgres_ok = await postgres_healthcheck()
    redis_ok = await redis_healthcheck()
    return {
        "status": "ok" if postgres_ok and redis_ok else "degraded",
        "postgres": postgres_ok,
        "redis": redis_ok,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.webhook_host,
        port=settings.webhook_port,
        reload=False,
    )
