from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(button_texts: list[str]) -> ReplyKeyboardMarkup:
    row: list[KeyboardButton] = []

    for text in button_texts:
        row.append(KeyboardButton(text=text))

    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


back_menu_keyboard = make_row_keyboard(["Назад", "Главное меню"])