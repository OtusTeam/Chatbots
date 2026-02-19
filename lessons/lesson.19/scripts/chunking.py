"""
Разбиение текста на чанки по разделителю с ограничением максимального размера.
Используется в RAG-лайт для поиска по ключевым словам.

Сценарии:
- По абзацам: separator="\\n\\n", части склеиваются до chunk_size, крупный абзац режется по размеру.
- По предложениям: separator=". " (или "."), аналогично с учётом chunk_size.
- По размеру: separator=None — разрез только по chunk_size символов.
"""
DEFAULT_CHUNK_SIZE = 500
DEFAULT_SEPARATOR = "\n\n"


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    separator: str | None = DEFAULT_SEPARATOR,
) -> list[dict]:
    """
    Разбивает текст на чанки.

    :param text: исходный текст (или содержимое файла)
    :param chunk_size: максимальный размер чанка в символах
    :param separator: разделитель (абзац "\\n\\n", предложение ". "; None — только по размеру)
    :return: список словарей с ключами text, chunk_id для каждого чанка
    """
    if not text or not text.strip():
        return []

    # По размеру: без разделителя, режем строго по chunk_size
    if separator is None or separator == "":
        return _chunk_by_size(text, chunk_size)

    parts = text.split(separator)
    chunks: list[dict] = []
    current: list[str] = []
    current_len = 0

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Длина части с учётом разделителя при склейке (между current и part будет separator)
        part_len = len(part) + (len(separator) if current else 0)
        if current and (current_len + part_len <= chunk_size):
            current.append(part)
            current_len += part_len
        else:
            if current:
                chunk_text_val = separator.join(current).strip()
                if chunk_text_val:
                    chunks.append({
                        "text": chunk_text_val,
                        "chunk_id": len(chunks) + 1,
                    })
                current = []
                current_len = 0
            if len(part) > chunk_size:
                # Крупная часть — режем по размеру (граница по символам)
                for i in range(0, len(part), chunk_size):
                    sub = part[i : i + chunk_size]
                    if sub.strip():
                        chunks.append({
                            "text": sub.strip(),
                            "chunk_id": len(chunks) + 1,
                        })
            else:
                current = [part]
                current_len = len(part)

    if current:
        chunk_text_val = separator.join(current).strip()
        if chunk_text_val:
            chunks.append({
                "text": chunk_text_val,
                "chunk_id": len(chunks) + 1,
            })

    return chunks


def _chunk_by_size(text: str, chunk_size: int) -> list[dict]:
    """Чанкование строго по размеру (без разделителя)."""
    if chunk_size <= 0:
        return []
    chunks = []
    for i in range(0, len(text), chunk_size):
        sub = text[i : i + chunk_size]
        if sub.strip():
            chunks.append({"text": sub, "chunk_id": len(chunks) + 1})
    return chunks


def chunk_file(
    path: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    separator: str | None = DEFAULT_SEPARATOR,
    encoding: str = "utf-8",
) -> list[dict]:
    """
    Читает файл и разбивает его на чанки.

    :param path: путь к файлу
    :param chunk_size: максимальный размер чанка
    :param separator: разделитель
    :param encoding: кодировка файла
    :return: список чанков с text и chunk_id
    """
    with open(path, encoding=encoding) as f:
        text = f.read()
    return chunk_text(text, chunk_size=chunk_size, separator=separator)


if __name__ == "__main__":
    sample = (
        "Первый абзац документа. Здесь несколько предложений.\n\n"
        "Второй абзац. Ещё текст для демонстрации чанкования.\n\n"
        "Третий абзац."
    )
    result = chunk_text(sample, chunk_size=50, separator="\n\n")
    for c in result:
        #print(f"[{c['chunk_id']}] {c['text'][:60]}...")
        print(f"[{c['chunk_id']}] {c['text']}")
    print(f"Всего чанков: {len(result)}")
