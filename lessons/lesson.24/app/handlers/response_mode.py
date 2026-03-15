"""
Команда /mode и /voice — переключатель режима ответа (текст / голос).
Inline-кнопка для переключения без ввода команды.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from app.services.response_mode import get_response_mode, toggle_response_mode

router = Router()


def _mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ответ текстом / голосом", callback_data="toggle_response_mode")],
    ])


@router.message(Command("mode"))
@router.message(Command("voice"))
async def cmd_response_mode(message: Message) -> None:
    """Переключает режим ответа и сообщает текущий."""
    user_id = message.from_user.id if message.from_user else 0
    new_mode = toggle_response_mode(user_id)
    label = "голос" if new_mode == "voice" else "текст"
    desc = "только голосом" if new_mode == "voice" else "только текстом"
    await message.reply(
        f"Режим ответа: {label}. Ответы бота будут приходить {desc}.",
        reply_markup=_mode_keyboard(),
    )


@router.callback_query(F.data == "toggle_response_mode")
async def cb_toggle_response_mode(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    new_mode = toggle_response_mode(user_id)
    label = "голос" if new_mode == "voice" else "текст"
    await callback.answer(f"Режим ответа: {label}")
    desc = "только голосом" if new_mode == "voice" else "только текстом"
    await callback.message.edit_text(
        f"Режим ответа: {label}. Ответы бота будут приходить {desc}.",
        reply_markup=_mode_keyboard(),
    )
