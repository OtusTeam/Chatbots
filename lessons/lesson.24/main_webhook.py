import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from config.config import (
    telegram_bot_token,
    webhook_url,
    webhook_path,
    webhook_host,
    webhook_port,
)
from app.handlers.routers import root_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Инициализация бота и диспетчера
bot = Bot(token=telegram_bot_token)
dp = Dispatcher()
dp.include_router(root_router)


async def setup_webhook():
    """Установка webhook в Telegram."""
    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL not set. Проверьте .env файл")

    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для FastAPI."""
    # Startup
    await setup_webhook()
    yield
    # Shutdown
    await bot.session.close()


# FastAPI приложение с lifespan
app = FastAPI(title="Telegram Bot Webhook", lifespan=lifespan)


@app.post(webhook_path)
async def webhook_handler(request: Request):
    """Обработчик webhook от Telegram."""
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/health")
async def health_check():
    """Health-check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    # Запуск FastAPI сервера
    # lifespan будет вызван автоматически при старте и остановке
    uvicorn.run(
        app,
        host=webhook_host,
        port=webhook_port,
    )