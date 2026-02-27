"""
Fallback-логика: сначала проверка правил (FAQ), затем RAG, затем «не знаю».
Обработка таймаутов и 429 в цепочке.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_LESSON_DIR = _SCRIPT_DIR.parent
if str(_LESSON_DIR) not in sys.path:
    sys.path.insert(0, str(_LESSON_DIR))
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from dotenv import load_dotenv
load_dotenv(_LESSON_DIR / ".env")

# Простой FAQ: вопрос (нормализованный) -> ответ
FAQ = {
    "привет": "Привет! Чем могу помочь?",
    "как дела": "Спасибо, хорошо. Задайте вопрос по документам.",
}


def normalize(s: str) -> str:
    return " ".join(s.lower().split()).strip() if s else ""


def check_faq(query: str) -> str | None:
    """Если запрос совпадает с ключом FAQ — возвращаем ответ, иначе None."""
    q = normalize(query)
    for key, answer in FAQ.items():
        if key in q or q in key:
            print(f"[fallback_chain] FAQ сработал: key={key!r}, query={query!r}")
            return answer
    return None


def call_rag(query: str, timeout_sec: float = 30) -> tuple[str, str | None, bool]:
    """
    Вызов RAG (поиск + LLM). Возвращает (ответ, источник, успех).
    При ошибке/таймауте возвращает ("", None, False).
    """
    print(f"[fallback_chain] RAG: запускаем поиск для запроса {query!r}")
    try:
        from search_qdrant import search
        from answer_builder import get_answer_with_citation
    except ImportError:
        print("[fallback_chain] Не удалось импортировать search_qdrant или answer_builder")
        return "", None, False
    try:
        chunks, no_answer = search(query, top_k=5)
        if no_answer or not chunks:
            print("[fallback_chain] RAG: no_answer=True или пустые chunks — возвращаем 'не нашёл'")
            return "Не нашёл подходящего ответа в документах.", None, True
        answer, source = get_answer_with_citation(chunks, query)
        print(f"[fallback_chain] RAG: получили ответ длиной {len(answer)} символов, source={source!r}")
        return answer, source, True
    except Exception:
        print("[fallback_chain] Ошибка при вызове RAG, переходим к запасному ответу", flush=True)
        return "", None, False


def fallback_chain(query: str) -> tuple[str, str | None]:
    """
    Цепочка: FAQ -> RAG -> «не знаю».
    :return: (ответ пользователю, источник или None)
    """
    print(f"[fallback_chain] Новый запрос: {query!r}")
    faq_answer = check_faq(query)
    if faq_answer is not None:
        print("[fallback_chain] Ответ найден в FAQ")
        return faq_answer, None

    answer, source, ok = call_rag(query)
    if ok:
        print(f"[fallback_chain] Ответ от RAG (ok=True), source={source!r}")
        return answer, source
    print("[fallback_chain] Ни FAQ, ни RAG не сработали — возвращаем 'Попробуйте позже'")
    return "Извините, не могу ответить сейчас. Попробуйте позже.", None


if __name__ == "__main__":
    print("[fallback_chain] Демонстрация работы цепочки FAQ -> RAG -> 'не знаю'.")
    print(fallback_chain("Привет"))
    print(fallback_chain("Где офис?"))
