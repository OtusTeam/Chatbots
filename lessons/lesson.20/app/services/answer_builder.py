"""Сборка ответа по контексту через LLM с цитатой."""
from __future__ import annotations

import time

from config.config import GIGACHAT_CREDENTIALS, GIGACHAT_MAX_TOKENS, GIGACHAT_TEMPERATURE

SYSTEM_PROMPT = """Ты отвечаешь только на основе приведённого контекста.
Если в контексте нет ответа — напиши «Не знаю»."""

TEMPLATE = "Контекст:\n{context}\n\nВопрос: {question}\n\nОтвет:"


def get_answer_with_citation(chunks: list[dict], question: str, max_retries: int = 3) -> tuple[str, str | None, str]:
    """Возвращает (ответ, источник — имя файла, текст чанка для вывода внизу)."""
    from gigachat import GigaChat
    from gigachat.models import Chat, Messages, MessagesRole

    if not GIGACHAT_CREDENTIALS:
        return "Задайте GIGACHAT_CREDENTIALS в .env", None, ""

    context = "\n\n".join(
        f"[Чанк {c.get('chunk_id', '?')}]\n{c.get('text', '')}" for c in chunks
    )
    user_content = TEMPLATE.format(context=context, question=question)

    for attempt in range(max_retries):
        try:
            with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
                r = giga.chat(Chat(
                    messages=[
                        Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                        Messages(role=MessagesRole.USER, content=user_content),
                    ],
                    temperature=GIGACHAT_TEMPERATURE,
                    max_tokens=GIGACHAT_MAX_TOKENS,
                ))
            content = r.choices[0].message.content
            source = None
            cited_chunk = None
            for c in chunks:
                cid = c.get("chunk_id")
                if cid and f"чанк {cid}" in content.lower():
                    source = c.get("source") or f"Чанк {cid}"
                    cited_chunk = c
                    break
            if source is None and chunks:
                first = chunks[0]
                source = first.get("source") or f"Чанк {first.get('chunk_id', '?')}"
                cited_chunk = first
            chunk_text = (cited_chunk.get("text", "") if cited_chunk else "").strip()
            return content, source, chunk_text
        except Exception as e:
            if ("429" in str(e) or "rate" in str(e).lower()) and attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            return f"Ошибка API: {e}", None, ""
    return "Ошибка: исчерпаны повторы", None, ""
