"""Получение эмбеддингов через OpenAI‑совместимый API (локальный endpoint).

Финальная схема как в уроке 20: берём BASE_URL / EMBEDDING_MODEL / API_KEY
из .env и ходим в локальный сервис (например, LM Studio).
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv

_LESSON_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_LESSON_DIR / ".env")

# Настройки эмбеддингов — те же имена переменных, что в lesson.20/.env.example
EMBEDDING_BASE_URL = os.getenv("BASE_URL", "http://localhost:1234/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-qwen3-embedding-4b")
EMBEDDING_API_KEY = os.getenv("API_KEY", "lm-studio")


def get_embeddings(texts: list[str], max_retries: int = 3) -> list[list[float]]:
    """
    Возвращает эмбеддинги для списка текстов через OpenAI‑совместимый API.
    Повторяет подход из lesson.20/app/services/embeddings.py.
    """
    print(f"[embeddings] Запрос эмбеддингов: {len(texts)} текст(ов)")

    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Установите openai: pip install openai")

    client = OpenAI(base_url=EMBEDDING_BASE_URL, api_key=EMBEDDING_API_KEY)
    # Нормализуем вход: убираем переводы строк, не даём пустые строки
    inputs = [t.replace("\n", " ").strip() or " " for t in texts]

    for attempt in range(max_retries):
        try:
            print(
                f"[embeddings] Попытка {attempt + 1}/{max_retries} "
                f"(model={EMBEDDING_MODEL}, base_url={EMBEDDING_BASE_URL})"
            )
            resp = client.embeddings.create(input=inputs, model=EMBEDDING_MODEL)
            vectors = [item.embedding for item in resp.data]
            print(f"[embeddings] Успешно получили {len(vectors)} векторов")
            return vectors
        except Exception as e:
            err_str = str(e).lower()
            if ("429" in err_str or "rate" in err_str or "connection" in err_str) and attempt < max_retries - 1:
                delay = 2 ** (attempt + 1)
                print(
                    f"[embeddings] Временная ошибка ({e}), "
                    f"ждём {delay} секунд и пробуем ещё раз"
                )
                time.sleep(delay)
                continue
            raise RuntimeError(f"Embeddings API: {e}") from e

    return []