"""Получение эмбеддингов через OpenAI-совместимый API."""
from __future__ import annotations

import time

from config.config import EMBEDDING_API_KEY, EMBEDDING_BASE_URL, EMBEDDING_MODEL


def get_embeddings(texts: list[str], max_retries: int = 3) -> list[list[float]]:
    """
    Возвращает эмбеддинги для списка текстов.
    :param texts: список строк
    :param max_retries: повторы при ошибках
    :return: список векторов (списков float)
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Установите openai: pip install openai")

    client = OpenAI(base_url=EMBEDDING_BASE_URL, api_key=EMBEDDING_API_KEY)
    inputs = [t.replace("\n", " ").strip() or " " for t in texts]

    for attempt in range(max_retries):
        try:
            r = client.embeddings.create(input=inputs, model=EMBEDDING_MODEL)
            return [item.embedding for item in r.data]
        except Exception as e:
            err_str = str(e).lower()
            if ("429" in err_str or "rate" in err_str or "connection" in err_str) and attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise RuntimeError(f"Embeddings API: {e}") from e
