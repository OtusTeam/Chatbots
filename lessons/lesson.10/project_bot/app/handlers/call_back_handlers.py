from aiogram import Router, types, F
from aiogram.filters.command import Command

from app.keyboards.reply import main_menu_keyboard, help_menu_keyboard
from app.keyboards.inline import demo_inline_keyboard


FAQ_ANSWERS = {
    "price": "Базовая версия бесплатно",
    "support": "Пока используйте кнопку Связаться",
    "privacy": "Мы не храним данные",
    "features": "Много что умеет",
}


router = Router()


@router.callback_query(F.data == "demo_ask_gpt")
async def ask_gpt_callback(callback: types.CallbackQuery):
    action = callback.data

    await callback.answer("Вы выбрали ChatGPT") # всплывающее уведомление
    await callback.message.answer("Вы нажали  ChatGPT") # Сообщение


@router.callback_query(F.data == "demo_ask_yandex")
async def ask_gpt_callback(callback: types.CallbackQuery):
    action = callback.data

    await callback.answer("Вы выбрали Yandex") # всплывающее уведомление
    await callback.message.answer("Вы нажали  Yandex")  # Сообщение


@router.callback_query(F.data.startswith("faq_"))
async def on_faq_callback(callback: types.CallbackQuery):
    data = callback.data
    await callback.answer()

    if data == "faq_price":
        await callback.message.answer(FAQ_ANSWERS.get("price"))
    elif data == "faq_support":
        await callback.message.answer(FAQ_ANSWERS.get("support"))
    elif data == "faq_privacy":
        await callback.message.answer(FAQ_ANSWERS.get("privacy"))
    elif data == "faq_features":
        await callback.message.answer(FAQ_ANSWERS.get("features"))

