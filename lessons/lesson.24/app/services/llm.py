"""Ответ через GigaChat API."""
from __future__ import annotations

import time

from config.config import (
    GIGACHAT_CREDENTIALS,
    GIGACHAT_MAX_TOKENS,
    GIGACHAT_TEMPERATURE,
)

SYSTEM_PROMPT = "Ты — полезный голосовой и текстовый ассистент. Отвечай кратко и по делу на русском языке."


def get_llm_reply(user_text: str, max_retries: int = 3) -> str:
    """
    Отправляет запрос в GigaChat, возвращает текст ответа или сообщение об ошибке.
    """
    if not (user_text or "").strip():
        return "Напишите или скажите что-нибудь."

    if not GIGACHAT_CREDENTIALS:
        return "Не заданы GIGACHAT_CREDENTIALS в .env. Добавьте учётные данные GigaChat API."

    try:
        from gigachat import GigaChat
        from gigachat.models import Chat, Messages, MessagesRole
    except ImportError:
        return "Установите пакет gigachat: pip install gigachat"

    for attempt in range(max_retries):
        try:
            with GigaChat(
                credentials=GIGACHAT_CREDENTIALS,
                verify_ssl_certs=False,
            ) as giga:
                r = giga.chat(
                    Chat(
                        messages=[
                            Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                            Messages(role=MessagesRole.USER, content=user_text.strip()),
                        ],
                        temperature=GIGACHAT_TEMPERATURE,
                        max_tokens=GIGACHAT_MAX_TOKENS,
                    )
                )
            return (r.choices[0].message.content or "").strip() or "Пустой ответ от модели."
        except Exception as e:
            if ("429" in str(e) or "rate" in str(e).lower()) and attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            return f"Ошибка API: {e!s}"
    return "Не удалось получить ответ. Попробуйте позже."
