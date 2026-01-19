HELP_TEXT: str = """
    Что я умею:
    1) /start - запуск бота и приветствие
    2) /help - помощь
    3) /prof - анкета выбора профессии
    4) Эхо бот - отвечаю на любое сообщение
"""

ABOUT_TEXT: str  = """
    О нас:
    Это инфо-бот на aiogram
    OTUS Chatbots
"""

CONTACTS_TEXT: str  = """
    Контакты:
    Поддержка: @support_user
    Email: user@gmail.com
"""


def get_help_text() -> str:
    return HELP_TEXT


def get_about_text() -> str:
    return ABOUT_TEXT


def get_contacts_text() -> str:
    return CONTACTS_TEXT