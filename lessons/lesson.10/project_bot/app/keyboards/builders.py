from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(buttons: list[str]) -> ReplyKeyboardMarkup:
    # len(buttons)
    row_keyboard = [KeyboardButton(text=button) for button in buttons]
    return ReplyKeyboardMarkup(keyboard=[row_keyboard], resize_keyboard=True)