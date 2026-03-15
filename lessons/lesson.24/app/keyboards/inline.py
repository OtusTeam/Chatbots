from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


ask_gpt_button = InlineKeyboardButton(text='Спросить у GPT', callback_data='ask_gpt_button')
ask_yandex_button = InlineKeyboardButton(text='Спросить у Yandex', callback_data='ask_yandex_button')

keyboard_rows_ask = [
    [ask_gpt_button, ask_yandex_button],
]

ask_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows_ask)