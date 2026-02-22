"""CLI индексации: загрузка документов из docs и запись в Qdrant."""
import sys

from config.config import CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR
from app.services.index_documents import load_docs_from_dir, index_chunks


if __name__ == "__main__":
    chunks = load_docs_from_dir(DOCS_DIR, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    if not chunks:
        print("Нет документов в", DOCS_DIR)
        sys.exit(1)
    print(f"Загружено чанков из docs: {len(chunks)}")
    index_chunks(chunks)
    print("Векторная база (Qdrant) построена.")
