"""
Поиск в Qdrant: эмбеддинг запроса -> top-k ближайших точек -> возврат с score.
Детект «нет ответа» по порогу score.
"""
from __future__ import annotations

from qdrant_client import QdrantClient

from config.config import (
    QDRANT_COLLECTION,
    QDRANT_HOST,
    QDRANT_PORT,
    SCORE_THRESHOLD,
    SEARCH_TOP_K,
)
from app.services.embeddings import get_embeddings

COLLECTION_NAME = QDRANT_COLLECTION


def search(
    query: str,
    top_k: int = SEARCH_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    collection: str = COLLECTION_NAME,
) -> tuple[list[dict], bool]:
    """
    Поиск по запросу в Qdrant.
    :return: (список чанков с text, chunk_id, score), no_answer (True если нет релевантных)
    """
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    [query_vector] = get_embeddings([query])
    response = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    results = response.points if hasattr(response, "points") else []

    out = []
    for r in results:
        payload = r.payload or {}
        out.append({
            "text": payload.get("text", ""),
            "chunk_id": payload.get("chunk_id", r.id),
            "score": r.score,
            **({"source": payload["source"]} if payload.get("source") else {}),
        })

    no_answer = not out or (out and out[0]["score"] < score_threshold)
    return out, no_answer


if __name__ == "__main__":
    chunks, no_answer = search("Как зовут друзей Гарри?")
    if no_answer:
        print("Нет релевантного ответа (низкий score или пусто).")
    else:
        for c in chunks:
            print(f"\n---\nchunk_id={c['chunk_id']} score={c['score']:.3f}\n{c['text']}")
