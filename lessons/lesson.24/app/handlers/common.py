import logging

from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardRemove
from app.utils import fox
from app.services.menu_content import get_help_text


logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('start'))
async def command_start(message: types.Message):
    user_name = message.chat.username or "друг"
    await message.answer(
        f"Привет, {user_name}! Отправь текст или голосовое — отвечу через GigaChat. Режим ответа: /mode или /voice.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command('help'))
@router.message(Command('помощь'))
async def command_help(message: types.Message):
    help_text = get_help_text()
    await message.answer(text=help_text, reply_markup=ReplyKeyboardRemove())


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

