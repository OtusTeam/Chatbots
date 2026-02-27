"""Поиск в Qdrant для fallback_chain."""
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
from qdrant_client import QdrantClient
from embeddings import get_embeddings

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "documents")
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.5"))


def search(
    query: str,
    top_k: int = 5,
    score_threshold: float = SCORE_THRESHOLD,
    collection: str = COLLECTION_NAME,
) -> tuple[list[dict], bool]:
    """Поиск в Qdrant по образцу vector_search.search из урока 20."""
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    client = QdrantClient(host=host, port=port)

    print(
        f"[search_qdrant] Поиск: query={query!r}, host={host}, port={port}, "
        f"collection={collection}, top_k={top_k}, threshold={score_threshold}"
    )

    [query_vector] = get_embeddings([query])
    response = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    results = response.points if hasattr(response, "points") else []
    out: list[dict] = []
    for r in results:
        payload = r.payload or {}
        out.append(
            {
                "text": payload.get("text", ""),
                "chunk_id": payload.get("chunk_id", r.id),
                "score": r.score,
                **({"source": payload["source"]} if payload.get("source") else {}),
            }
        )

    no_answer = not out or out[0]["score"] < score_threshold
    top_score = out[0]["score"] if out else None
    print(
        f"[search_qdrant] Найдено {len(out)} чанков, top_score={top_score}, "
        f"no_answer={no_answer}"
    )
    return out, no_answer
