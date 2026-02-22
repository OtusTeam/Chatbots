"""
Индексация документов в Qdrant: тексты -> чанки -> эмбеддинги -> запись в коллекцию.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm

from config.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCS_DIR,
    EMBEDDING_BATCH_SIZE,
    QDRANT_COLLECTION,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_UPSERT_BATCH_SIZE,
)
from app.services.chunking import chunk_text
from app.services.embeddings import get_embeddings

COLLECTION_NAME = QDRANT_COLLECTION
BATCH_SIZE = EMBEDDING_BATCH_SIZE
UPSERT_BATCH_SIZE = QDRANT_UPSERT_BATCH_SIZE


def load_docs_from_dir(
    docs_dir: Path | str = DOCS_DIR,
    extensions: tuple[str, ...] = (".txt",),
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    encoding: str = "utf-8",
) -> list[dict]:
    """
    Загружает все документы из директории, разбивает на чанки (с перекрытием overlap).
    :return: список чанков с ключами text, chunk_id, source (имя файла)
    """
    docs_dir = Path(docs_dir)
    if not docs_dir.is_dir():
        return []

    all_chunks: list[dict] = []
    files = [p for p in sorted(docs_dir.iterdir()) if p.suffix.lower() in extensions]
    for path in tqdm(files, desc="Загрузка документов", unit="файл"):
        try:
            text = path.read_text(encoding=encoding)
        except Exception as e:
            tqdm.write(f"Пропуск {path.name}: {e}")
            continue
        file_chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        for c in file_chunks:
            c["source"] = path.name
            c["chunk_id"] = len(all_chunks) + 1
            all_chunks.append(c)
    return all_chunks


def index_chunks(
    chunks: list[dict],
    collection: str = COLLECTION_NAME,
    host: str | None = None,
    port: int | None = None,
) -> None:
    """
    Удаляет старую коллекцию, создаёт новую, получает эмбеддинги для чанков, записывает точки в Qdrant.
    """
    host = host or QDRANT_HOST
    port = port or QDRANT_PORT
    client = QdrantClient(host=host, port=port)

    if not chunks:
        return

    texts = [c["text"] for c in chunks]
    all_vectors = []
    num_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Эмбеддинги", unit="батч", total=num_batches):
        batch = texts[i : i + BATCH_SIZE]
        vectors = get_embeddings(batch)
        all_vectors.extend(vectors)

    vector_size = len(all_vectors[0])
    tqdm.write(f"Размерность вектора: {vector_size}")

    collections = client.get_collections().collections
    if any(c.name == collection for c in collections):
        tqdm.write(f"Удаление старой коллекции {collection!r}...")
        client.delete_collection(collection)
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    points = [
        PointStruct(
            id=c["chunk_id"],
            vector=all_vectors[i],
            payload={
                "text": c["text"],
                "chunk_id": c["chunk_id"],
                **({"source": c["source"]} if c.get("source") else {}),
            },
        )
        for i, c in enumerate(chunks)
    ]
    max_retries = 3
    for start in tqdm(
        range(0, len(points), UPSERT_BATCH_SIZE),
        desc="Запись в Qdrant",
        unit="батч",
    ):
        batch_points = points[start : start + UPSERT_BATCH_SIZE]
        for attempt in range(max_retries):
            try:
                client.upsert(collection_name=collection, points=batch_points)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** (attempt + 1))
                else:
                    raise RuntimeError(f"Qdrant upsert после {max_retries} попыток: {e}") from e
