"""
Сборка ответа с цитатой: контекст (найденные чанки) + вопрос -> промпт -> GigaChat -> ответ + источник.
Правило: отвечай только по контексту; если ответа нет — скажи «не знаю».
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Ты отвечаешь только на основе приведённого ниже контекста.
Если в контексте нет ответа на вопрос — напиши «Не знаю» или «В контексте нет информации».
В конце ответа обязательно укажи источник: номер фрагмента из контекста в формате [Источник: чанк N]."""

USER_PROMPT_TEMPLATE = """Контекст:
{context}

Вопрос: {question}

Ответ (с указанием источника в конце):"""


def build_prompt(context: str, question: str) -> str:
    """Формирует пользовательский промпт с контекстом и вопросом."""
    return USER_PROMPT_TEMPLATE.format(context=context.strip(), question=question.strip())


def get_answer_with_citation(
    chunks: list[dict],
    question: str,
    max_retries: int = 3,
) -> tuple[str, str | None]:
    """
    Отправляет контекст и вопрос в GigaChat, возвращает ответ и источник (цитату).

    :param chunks: список чанков с ключами text, chunk_id
    :param question: вопрос пользователя
    :param max_retries: число повторов при 429
    :return: (текст ответа, источник — например "чанк 1" или None)
    """
    try:
        from gigachat import GigaChat
        from gigachat.models import Chat, Messages, MessagesRole
    except ImportError:
        return (
            "Ошибка: установите gigachat (pip install gigachat).",
            None,
        )

    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        return "Ошибка: задайте GIGACHAT_CREDENTIALS в .env", None

    context_parts = []
    for c in chunks:
        cid = c.get("chunk_id", "?")
        context_parts.append(f"[Чанк {cid}]\n{c.get('text', '')}")
    context = "\n\n".join(context_parts)

    user_content = build_prompt(context, question)

    for attempt in range(max_retries):
        try:
            with GigaChat(credentials=credentials, verify_ssl_certs=False) as giga:
                payload = Chat(
                    messages=[
                        Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT),
                        Messages(role=MessagesRole.USER, content=user_content),
                    ],
                    temperature=0.3,
                    max_tokens=500,
                )
                response = giga.chat(payload)
            break
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "rate" in err_str:
                if attempt < max_retries - 1:
                    time.sleep(2 ** (attempt + 1))
                    continue
            return f"Ошибка API: {e}", None

    content = response.choices[0].message.content
    source = None
    if "[Источник:" in content or "чанк" in content.lower():
        for c in chunks:
            cid = c.get("chunk_id")
            if cid and f"чанк {cid}" in content.lower():
                source = f"Чанк {cid}"
                break
    return content, source


if __name__ == "__main__":
    chunks = [
        {"text": "Офис находится на ул. Ленина, 10. Режим работы пн-пт 9-18.", "chunk_id": 1},
    ]
    answer, source = get_answer_with_citation(chunks, "Где офис и когда открыт?")
    print("Ответ:", answer)
    print("Источник:", source)
