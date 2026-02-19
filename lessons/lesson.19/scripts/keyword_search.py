"""
Поиск по ключевым словам среди чанков.
Запрос пользователя нормализуется (нижний регистр, разбиение на слова),
подсчитываются совпадения с текстом чанка, возвращаются top-N чанков.
"""
import re


def normalize_query(query: str) -> list[str]:
    """
    Нормализация запроса: нижний регистр, разбиение на слова (без пунктуации).

    :param query: строка запроса от пользователя
    :return: список слов для поиска
    """
    if not query or not query.strip():
        return []
    text = query.lower().strip()
    words = re.findall(r"[а-яёa-z0-9]+", text, re.IGNORECASE)
    return [w for w in words if len(w) > 1]


def score_chunk(chunk_text: str, words: list[str]) -> int:
    """
    Подсчёт совпадений: сколько слов из запроса встречается в чанке.

    :param chunk_text: текст чанка (нормализованный к нижнему регистру)
    :param words: список слов запроса
    :return: количество совпадающих слов
    """
    if not words:
        return 0
    lower = chunk_text.lower()
    return sum(1 for w in words if w in lower)


def search_chunks(
    chunks: list[dict],
    query: str,
    top_n: int = 5,
) -> list[dict]:
    """
    Поиск наиболее релевантных чанков по ключевым словам.

    :param chunks: список чанков с ключом "text" (и опционально "chunk_id")
    :param query: запрос пользователя
    :param top_n: сколько чанков вернуть
    :return: список чанков с добавленным полем "score", отсортированный по score
    """
    words = normalize_query(query)
    if not words:
        return []

    scored: list[dict] = []
    for ch in chunks:
        text = ch.get("text", "")
        score = score_chunk(text, words)
        if score > 0:
            scored.append({**ch, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


if __name__ == "__main__":
    from chunking import chunk_text

    doc = "Офис компании находится на улице Ленина. Режим работы: пн-пт 9-18."
    chunks = chunk_text(doc, chunk_size=100)
    results = search_chunks(chunks, "Где офис? Адрес")
    for r in results:
        print(f"chunk_id={r.get('chunk_id')} score={r.get('score')} text={r['text'][:50]}...")
