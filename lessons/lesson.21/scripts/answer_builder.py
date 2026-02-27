"""Сборка ответа с цитатой для fallback_chain."""
from __future__ import annotations
import os
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SYSTEM_PROMPT = "Ты отвечаешь только на основе контекста. Если ответа нет — «Не знаю». В конце: [Источник: чанк N]."
TEMPLATE = "Контекст:\n{context}\n\nВопрос: {question}\n\nОтвет:"

def get_answer_with_citation(chunks: list[dict], question: str, max_retries: int = 3) -> tuple[str, str | None]:
    try:
        from gigachat import GigaChat
        from gigachat.models import Chat, Messages, MessagesRole
    except ImportError:
        return "Ошибка: pip install gigachat", None
    creds = os.getenv("GIGACHAT_CREDENTIALS")
    if not creds:
        return "Задайте GIGACHAT_CREDENTIALS в .env", None
    print(f"[answer_builder] Получили {len(chunks)} чанков для вопроса {question!r}")
    context = "\n\n".join(f"[Чанк {c.get('chunk_id','?')}]\n{c.get('text','')}" for c in chunks)
    user_content = TEMPLATE.format(context=context, question=question)
    for attempt in range(max_retries):
        try:
            print(f"[answer_builder] Попытка вызова GigaChat {attempt + 1}/{max_retries}")
            with GigaChat(credentials=creds, verify_ssl_certs=False) as giga:
                r = giga.chat(Chat(messages=[
                    Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                    Messages(role=MessagesRole.USER, content=user_content),
                ], temperature=0.3, max_tokens=500))
            content = r.choices[0].message.content
            source = next(
                (
                    f"Чанк {c['chunk_id']}"
                    for c in chunks
                    if c.get("chunk_id") and f"чанк {c['chunk_id']}" in content.lower()
                ),
                None,
            )
            print(f"[answer_builder] Ответ получен, длина={len(content)} символов, source={source!r}")
            return content, source
        except Exception as e:
            if ("429" in str(e) or "rate" in str(e).lower()) and attempt < max_retries - 1:
                delay = 2 ** (attempt + 1)
                print(f"[answer_builder] 429 / rate limit, ждём {delay} секунд и пробуем ещё раз")
                time.sleep(delay)
                continue
            print(f"[answer_builder] Ошибка API: {e}")
            return f"Ошибка API: {e}", None
    return "Ошибка: исчерпаны повторы", None
