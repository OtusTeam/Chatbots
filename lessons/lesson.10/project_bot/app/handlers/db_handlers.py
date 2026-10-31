from aiogram import Router, types
from aiogram.filters import Command


router = Router()


@router.message(Command('dbping'))
async def pdb_ing(message: types.Message):
    await message.answer("DB-модуль подключен")