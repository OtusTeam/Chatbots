import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import telegram_bot_token
from app.handlers.routers import root_router


logging.basicConfig(level=logging.INFO)


async def run_bot():
    if not telegram_bot_token:
        raise RuntimeError('Telegram bot token not set. Проверьте, что он присутствует в .env')

    bot = Bot(token=telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(root_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_bot())


# /prof