"""Разбиение текста на чанки для индексации в Qdrant."""
from __future__ import annotations

DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 50
DEFAULT_SEPARATOR = "\n\n"


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    separator: str = DEFAULT_SEPARATOR,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict]:
    """
    Разбивает текст на чанки. Возвращает список с ключами text, chunk_id.
    overlap: число символов пересечения между любыми соседними чанками.
    """
    if not text or not text.strip():
        return []
    overlap = max(0, min(overlap, chunk_size - 1))  # 0 <= overlap < chunk_size
    parts = text.split(separator)
    chunks: list[dict] = []
    current: list[str] = []
    current_len = 0
    last_tail = ""

    def emit(text: str) -> None:
        nonlocal last_tail
        if not text.strip():
            return
        if last_tail and overlap:
            text = last_tail + text
        chunks.append({"text": text, "chunk_id": len(chunks) + 1})
        last_tail = text[-overlap:] if overlap else ""

    for part in parts:
        part = part.strip()
        if not part:
            continue
        part_len = len(part) + (len(separator) if current else 0)
        if current_len + part_len <= chunk_size and current:
            current.append(part)
            current_len += part_len
        else:
            if current:
                joined = separator.join(current).strip()
                if joined:
                    emit(joined)
            if len(part) > chunk_size:
                step = max(1, chunk_size - overlap)
                for i in range(0, len(part), step):
                    sub = part[i : i + chunk_size].strip()
                    if sub:
                        emit(sub)
                current = []
                current_len = 0
            else:
                current = [part]
                current_len = len(part)
    if current:
        joined = separator.join(current).strip()
        if joined:
            emit(joined)
    return chunks
