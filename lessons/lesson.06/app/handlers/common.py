from aiogram import Router, types, Bot
from aiogram.filters.command import Command

from app.keyboards.reply import main_menu_keyboard, help_menu_keyboard
from app.keyboards.inline import demo_inline_keyboard
from app.utils.fox import async_fox


router = Router()


@router.message(Command('start'))
async def command_start(message: types.Message):
    # print(message.chat.first_name)
    await message.answer(f"Привет! {message.chat.first_name}", reply_markup=main_menu_keyboard)


@router.message(Command('info'))
async def command_info(message: types.Message):
    text = """
    Я бот ассистент.
    """
    await message.answer(f"{text}", reply_markup=demo_inline_keyboard)


@router.message(Command('help'))
async def command_help(message: types.Message):
    text = """
    Что я умеюЖ
    1) /start - Запуск бота и приветствие
    2) /info - Информация о боте
    3) /help - Помощь
    4) /prof - Анкета выбора профессии
    """
    await message.answer(f"{text}", reply_markup=help_menu_keyboard)


@router.message(Command('fox'))
@router.message(Command('лиса'))
async def command_fox(message: types.Message, bot: Bot):
    image_fox = await async_fox()
    # print(image_fox)
    await message.answer_photo(image_fox)
    image_fox = await async_fox()
    await bot.send_photo(message.chat.id, image_fox)
