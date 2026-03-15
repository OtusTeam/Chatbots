from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message
from app.keyboards.reply import main_menu_keyboard
from app.services.texts import (
    FAQ_BUTTON_TEXT,
    ABOUT_BUTTON_TEXT,
    CONTACT_BUTTON_TEXT,
    MENU_BUTTON_TEXT,
)
from app.services.menu_content import get_about_text, get_contacts_text
from app.keyboards.inline import ask_inline_keyboard



router = Router()


@router.message(F.text == FAQ_BUTTON_TEXT)
async def on_faq_button(message: Message):
    await message.reply(f'Выберите вопрос:...', reply_markup=main_menu_keyboard)
    await message.answer("Выбери кнопку для запроса.", reply_markup=ask_inline_keyboard)


@router.message(F.text == ABOUT_BUTTON_TEXT)
async def on_faq_button(message: Message):
    text = get_about_text()
    await message.reply(text, reply_markup=main_menu_keyboard)


@router.message(F.text == CONTACT_BUTTON_TEXT)
async def on_faq_button(message: Message):
    text = get_contacts_text()
    await message.reply(text, reply_markup=main_menu_keyboard)


@router.message(F.text == MENU_BUTTON_TEXT)
async def on_faq_button(message: Message):
    await message.reply(f'Главное меню:...', reply_markup=main_menu_keyboard)


@router.callback_query(F.data.in_({'ask_gpt_button', 'ask_yandex_button'}))
async def on_ask_inline_button_click(callback: CallbackQuery):
    action = callback.data or ''
    if action == 'ask_gpt_button':
        print(callback)
        await callback.answer('Хорошо, сделаем с использование ChatGPT')
        return
    if action == 'ask_yandex_button':
        print(callback)
        await callback.answer('Хорошо, сделаем с использование Yandex')
        return
    await callback.answer('Неизвестная кнопка')