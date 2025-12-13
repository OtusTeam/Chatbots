import logging

from aiogram import Router, types
from aiogram.filters.command import Command
from app.utils import fox


logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('start'))
async def command_start(message: types.Message):
    user_name = message.chat.username
    await message.answer(f'Привет, {user_name}')


@router.message(Command('help'))
@router.message(Command('помощь'))
async def command_help(message: types.Message):
    user_name = message.chat.username
    help_text = """
        Что я умею:
        1) /start - запуск бота и приветствие
        2) /help -помощь
        3) Эхо бот - отвечаю на любое сообщение
    """

    await message.answer(help_text)


@router.message(Command('fox'))
async def command_fox(message: types.Message):
    image_fox = fox()

    await message.answer_photo(image_fox)
    await message.answer_
