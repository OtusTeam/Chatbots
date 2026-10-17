import asyncio
import logging
from aiogram import Bot, Dispatcher


from app.config import APP_NAME, TELEGRAM_BOT_TOKEN
from app.handlers.common import router as command_router
from app.handlers.bot_message import router as message_router
from app.handlers.bot_photo import router as photo_router



async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(command_router)
    dp.include_router(photo_router)
    dp.include_router(message_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())