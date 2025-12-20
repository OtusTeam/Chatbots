# import logging
from aiogram import Router, types, F


# logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text)
async def echo(message: types.Message):
    text = message.text
    print(type(text))
    if text == '/stop':
        await message.answer(f'Ты хочешь завершить?')
    elif 'казино' in text:
        await message.answer(f'Ты написал запрещенное слово')
    else:
        await message.reply(f'Ты написал - {message.text}')
