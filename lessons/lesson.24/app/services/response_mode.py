"""
Состояние режима ответа пользователя: текст или голос.
Хранится в памяти (dict); для продакшена можно заменить на FSM/БД.
"""
from typing import Literal

ResponseMode = Literal["text", "voice"]

# user_id -> "text" | "voice"
_response_mode: dict[int, str] = {}

DEFAULT_MODE: ResponseMode = "text"


def get_response_mode(user_id: int) -> str:
    return _response_mode.get(user_id, DEFAULT_MODE)


def set_response_mode(user_id: int, mode: ResponseMode) -> None:
    _response_mode[user_id] = mode


def toggle_response_mode(user_id: int) -> str:
    """Переключает режим текст <-> голос и возвращает новый режим."""
    current = get_response_mode(user_id)
    new = "voice" if current == "text" else "text"
    set_response_mode(user_id, new)
    return new
