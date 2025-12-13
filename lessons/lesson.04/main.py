import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import telegram_bot_token
from app.handlers import bot_message, common

logging.basicConfig(level=logging.INFO)


async def run_bot():
    bot = Bot(token=telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(bot_message.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_bot())

