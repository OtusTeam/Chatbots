"""
Загружает .env из директории lesson.20 при первом импорте.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_LESSON_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_LESSON_DIR / ".env")

# Пути
DOCS_DIR = _LESSON_DIR / "docs"

# Эмбеддинги; переменные в .env
EMBEDDING_BASE_URL = os.getenv("BASE_URL", "http://localhost:1234/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "local")
EMBEDDING_API_KEY = os.getenv("API_KEY", "lm-studio")

# Индексация: батчи и чанкование
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")
QDRANT_UPSERT_BATCH_SIZE = int(os.getenv("QDRANT_UPSERT_BATCH_SIZE", "100"))

# Поиск (RAG)
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", "15"))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.5"))

# LLM (сборка ответа)
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_MAX_TOKENS = int(os.getenv("GIGACHAT_MAX_TOKENS", "500"))
GIGACHAT_TEMPERATURE = float(os.getenv("GIGACHAT_TEMPERATURE", "0.2"))

# Telegram-бот
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
