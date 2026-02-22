"""Точка входа: Telegram-бот с RAG."""
import asyncio

from aiogram import Bot, Dispatcher

from config.config import TELEGRAM_BOT_TOKEN
from app.handlers.routers import root_router


async def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("Задайте TELEGRAM_BOT_TOKEN в .env")
        return
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(root_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_bot())
