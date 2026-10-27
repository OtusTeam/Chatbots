import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import APP_NAME, TELEGRAM_BOT_TOKEN
from app.handlers.routers import root_router
from app.front.bot_entrypoint import setup_logging, logger

async def main():

    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Не найден TELEGRAM_BOT_TOKEN")

    # logging.basicConfig(level=logging.INFO)
    setup_logging()
    logger.info('Бот запущен')

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(root_router)


    try:
        logger.info('Запуск long polling')
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Неожиданная  ошибка {e}")
    finally:
        logger.info('Остановка бота')


if __name__ == '__main__':
    asyncio.run(main())