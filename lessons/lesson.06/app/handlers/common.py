import logging

from aiogram import Router, types, F
from aiogram.filters.command import Command
from app.utils import fox
from app.keyboards.reply import main_menu_keyboard, help_menu_keyboard


logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('start'))
async def command_start(message: types.Message):
    user_name = message.chat.username
    await message.answer(f'Привет, {user_name}', reply_markup=main_menu_keyboard)


@router.message(Command('help'))
@router.message(Command('помощь'))
async def command_help(message: types.Message):
    user_name = message.chat.username
    help_text = """
        Что я умею:
        1) /start - запуск бота и приветствие
        2) /help - помощь
        3) /prof - анкета выбора профессии
        4) Эхо бот - отвечаю на любое сообщение
    """

    await message.answer(help_text, reply_markup=help_menu_keyboard)


@router.message(Command('fox'))
async def command_fox(message: types.Message):
    image_fox = fox()

    await message.answer_photo(image_fox)


@router.message(F.photo)
async def photo_handler(message: types.Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    photo_list = message.photo
    print(message)
    print(photo_list)
    print(len(photo_list))
    await message.answer(f'Привет, получил фото')


@router.message(F.video)
async def video_handler(message: types.Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    video_list = message.video
    print(message)
    print(video_list)
    print(len(video_list))
    await message.answer(f'Привет, получил видео')

