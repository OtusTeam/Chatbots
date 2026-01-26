from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from app.services.texts import (
    FAQ_BUTTON_TEXT,
    PROF_BUTTON_TEXT,
    ABOUT_BUTTON_TEXT,
    CONTACT_BUTTON_TEXT,
    MENU_BUTTON_TEXT,
)

# FAQ_BUTTON_TEXT = 'FAQ'
# PROF_BUTTON_TEXT = '/prof'
# ABOUT_BUTTON_TEXT = 'О нас'
# CONTACT_BUTTON_TEXT = 'Связаться'
# MENU_BUTTON_TEXT = 'Главное меню'


faq_button = KeyboardButton(text=FAQ_BUTTON_TEXT)
prof_button = KeyboardButton(text=PROF_BUTTON_TEXT)
about_button = KeyboardButton(text=ABOUT_BUTTON_TEXT)
contact_button = KeyboardButton(text=CONTACT_BUTTON_TEXT)
menu_button = KeyboardButton(text=MENU_BUTTON_TEXT)

main_menu_layout = [
    [prof_button, faq_button, about_button, contact_button],
]

help_menu_layout = [
    [faq_button, contact_button, about_button],
    [faq_button, about_button, contact_button],
    [about_button, faq_button, contact_button],
]

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=main_menu_layout,
    resize_keyboard=True,
)

help_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=help_menu_layout,
    resize_keyboard=True,
)