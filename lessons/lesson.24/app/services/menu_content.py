HELP_TEXT: str = """
Что я умею:
• /start — приветствие
• /help — эта справка
• /mode или /voice — переключить режим ответа (только текст / только голос)
• Текст или голосовое — отвечаю через GigaChat (текстом или голосом по режиму)
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