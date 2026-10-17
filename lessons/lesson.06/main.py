import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import APP_NAME, TELEGRAM_BOT_TOKEN
from app.handlers.common import router as command_router
from app.handlers.bot_message import router as message_router
from app.handlers.bot_photo import router as photo_router
from app.handlers.call_back_handlers import router as callback_router
from app.handlers.career_choice import router as prof_router


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(command_router)
    dp.include_router(prof_router)
    dp.include_router(photo_router)
    dp.include_router(message_router)
    dp.include_router(callback_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())