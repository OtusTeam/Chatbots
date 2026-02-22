"""RAG: сообщение -> поиск в Qdrant -> сборка ответа через LLM -> отправка с цитатой."""
from __future__ import annotations

import traceback

from aiogram import F, Router, types
from aiogram.filters import Command

from config.config import SEARCH_TOP_K
from app.services.vector_search import search
from app.services.answer_builder import get_answer_with_citation

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Задай вопрос — я поищу ответ в проиндексированных документах и отвечу с указанием источника."
    )


@router.message(F.text)
async def on_text(message: types.Message):
    query = (message.text or "").strip()
    if not query:
        return
    user_id = message.from_user.id if message.from_user else "?"
    print(f"[RAG] Запрос (user={user_id}): {query!r}")
    await message.answer("Ищу...")
    try:
        chunks, no_answer = search(query, top_k=SEARCH_TOP_K)
        print(f"[RAG] Поиск: no_answer={no_answer}, найдено чанков={len(chunks)}")
        for i, c in enumerate(chunks):
            score = c.get("score")
            score_str = f"{score:.3f}" if isinstance(score, (int, float)) else str(score)
            src = c.get("source", "—")
            text_preview = (c.get("text", "") or "")[:60].replace("\n", " ")
            print(f"  [{i+1}] score={score_str} source={src} | {text_preview}...")
        if no_answer or not chunks:
            await message.answer("По документам не нашёл подходящего ответа.")
            return
        answer, source, _chunk_text = get_answer_with_citation(chunks, query)
        print(f"[RAG] Источник: {source!r}")
        text = answer
        answer_lower = (answer or "").strip().lower()
        if source and not answer_lower.startswith("не знаю"):
            text += f"\n\n📎 Источник: {source}"
        await message.answer(text)
    except Exception as e:
        print(f"[RAG] Ошибка: {e}")
        traceback.print_exc()
        await message.answer(f"Ошибка: {e}")
