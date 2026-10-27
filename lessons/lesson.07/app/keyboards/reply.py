from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.services.texts import (
    FAQ_BUTTON_TEXT,
    ABOUT_BUTTON_TEXT,
    CONTACT_BUTTON_TEXT,
    MENU_BUTTON_TEXT,
    HELP_BUTTON_TEXT,
    INFO_BUTTON_TEXT,
)



faq_button = KeyboardButton(text=FAQ_BUTTON_TEXT)
about_button = KeyboardButton(text=ABOUT_BUTTON_TEXT)
contact_button = KeyboardButton(text=CONTACT_BUTTON_TEXT)
menu_button = KeyboardButton(text=MENU_BUTTON_TEXT)
help_button = KeyboardButton(text=HELP_BUTTON_TEXT)
info_button = KeyboardButton(text=INFO_BUTTON_TEXT)

main_menu_layout = [
    [faq_button, about_button, contact_button],
]

help_menu_layout = [
    [faq_button, info_button, help_button],
    [faq_button, menu_button, contact_button],
    [about_button, help_button],
]

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=main_menu_layout,
    resize_keyboard=True,
)

help_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=help_menu_layout,
    resize_keyboard=True,
)