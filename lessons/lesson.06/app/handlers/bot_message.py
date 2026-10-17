from aiogram import Router, types, F

from app.keyboards.reply import main_menu_keyboard
from app.keyboards.builders import back_menu_keyboard
from app.keyboards.inline import demo_inline_keyboard, build_faq_keyboard


router = Router()


FAQ_ITEMS = {
    "price": "Сколько стоит?",
    "support": "Как связаться с поддержкой?",
    "privacy": "Как вы храните данные?",
    "features": "Что умеет бот?",
}


FAQ_ANSWERS = {
    "price": "Базовая версия бесплатно",
    "support": "Пока используйте кнопку Связаться",
    "privacy": "Мы не храним данные",
    "features": "Много что умеет",
}


@router.message(F.text == "FAQ")
async def on_faq_button(message: types.Message):
    await message.answer(f"Выберите вопрос...", reply_markup=back_menu_keyboard)
    keyboard = build_faq_keyboard(FAQ_ITEMS)
    await message.answer(f"Можно спросить у ИИ, выберите кнопку", reply_markup=keyboard)


@router.message(F.text == "О нас")
async def on_about_button(message: types.Message):
    await message.answer(f"О проекте...", reply_markup=back_menu_keyboard)


@router.message(F.text == "Связаться")
async def on_contact_button(message: types.Message):
    await message.answer(f"Наши контакты...", reply_markup=back_menu_keyboard)


@router.message(F.text == "Информация")
async def on_info_button(message: types.Message):
    await message.answer(f"Информация о проекте...", reply_markup=back_menu_keyboard)


@router.message(F.text == "Помощь")
async def on_help_button(message: types.Message):
    await message.answer(f"Спроси у ИИ", reply_markup=demo_inline_keyboard)


@router.message(F.text == "Назад")
async def on_help_button(message: types.Message):
    await message.answer(f"Возвращаемся в главное меню...", reply_markup=main_menu_keyboard)


@router.message(F.text == "Главное меню")
async def on_help_button(message: types.Message):
    await message.answer(f"Главное меню", reply_markup=main_menu_keyboard)


@router.message(F.text & ~F.text.startswith('/'))
async def echo(message: types.Message):
    text = message.text
    if "казино" in text:
        await message.reply(f"Мне здесь не играем!")
    elif message.text == "Информация":
        await message.answer(f"Я информационный бот-помощник Клиники", reply_markup=main_menu_keyboard)
    else:
        await message.reply(f"{text}")
