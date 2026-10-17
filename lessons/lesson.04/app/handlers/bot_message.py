from aiogram import Router, types, F


router = Router()


@router.message(F.text == "FAQ")
async def on_faq_button(message: types.Message):
    await message.answer(f"Выберите вопрос...")
    await message.answer(f"Можно спросить у ИИ, выберите кнопку")


@router.message(F.text == "О нас")
async def on_about_button(message: types.Message):
    await message.answer(f"О проекте...")


@router.message(F.text == "Связаться")
async def on_contact_button(message: types.Message):
    await message.answer(f"Наши контакты...")


@router.message(F.text == "Информация")
async def on_info_button(message: types.Message):
    await message.answer(f"Информация о проекте...")


@router.message(F.text == "Помощь")
async def on_help_button(message: types.Message):
    await message.answer(f"Спроси у ИИ")


@router.message(F.text == "Назад")
async def on_help_button(message: types.Message):
    await message.answer(f"Возвращаемся в главное меню...")


@router.message(F.text == "Главное меню")
async def on_help_button(message: types.Message):
    await message.answer(f"Главное меню")


@router.message(F.text & ~F.text.startswith('/'))
async def echo(message: types.Message):
    text = message.text
    if "казино" in text:
        await message.reply(f"Мне здесь не играем!")
    elif message.text == "Информация":
        await message.answer(f"Я информационный бот-помощник Клиники")
    else:
        await message.reply(f"{text}")
