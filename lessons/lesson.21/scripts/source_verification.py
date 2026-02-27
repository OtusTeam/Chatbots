"""
Проверка источников: извлечь из ответа LLM упомянутые чанки/источники,
проверить, что каждый есть в переданном контексте (результатах поиска).
При отсутствии — пометка «неподтверждённый источник» или отказ.
"""
from __future__ import annotations

import re


def extract_cited_chunk_ids(answer: str) -> list[int]:
    """
    Извлекает из текста ответа упомянутые номера чанков.
    Ищем паттерны вида «чанк 1», «[Источник: чанк 2]», «(чанк 3)».
    """
    ids = []
    text = answer.lower()
    for m in re.finditer(r"чанк\s*[:\s]*(\d+)", text):
        ids.append(int(m.group(1)))
    for m in re.finditer(r"источник[:\s]*(\d+)", text):
        ids.append(int(m.group(1)))
    unique_ids = list(dict.fromkeys(ids))
    print(f"[source_verification] Упомянутые id в ответе: {unique_ids}")
    return unique_ids


def verify_sources(
    answer: str,
    context_chunks: list[dict],
) -> tuple[bool, list[int], list[int]]:
    """
    Проверяет, что все упомянутые в ответе источники есть в контексте.
    :return: (все_подтверждены, список_подтверждённых_id, список_неподтверждённых_id)
    """
    cited = extract_cited_chunk_ids(answer)
    allowed_ids = {c.get("chunk_id") for c in context_chunks if c.get("chunk_id") is not None}
    confirmed = [i for i in cited if i in allowed_ids]
    unconfirmed = [i for i in cited if i not in allowed_ids]
    print(
        f"[source_verification] allowed_ids={sorted(allowed_ids)}, "
        f"confirmed={confirmed}, unconfirmed={unconfirmed}"
    )
    return len(unconfirmed) == 0, confirmed, unconfirmed


def format_answer_with_verification(
    answer: str,
    context_chunks: list[dict],
) -> str:
    """
    Возвращает ответ с пометкой, если есть неподтверждённые источники.
    """
    all_ok, confirmed, unconfirmed = verify_sources(answer, context_chunks)
    if all_ok:
        print("[source_verification] Все источники подтверждены")
        return answer
    suffix = " [Внимание: в ответе упомянуты источники, которых нет в контексте поиска.]"
    print(f"[source_verification] Неподтверждённые источники: {unconfirmed}")
    return answer + suffix


if __name__ == "__main__":
    print("[source_verification] Демонстрация проверки источников в ответе LLM.")
    context = [{"text": "Офис на Ленина, 10.", "chunk_id": 1}, {"text": "Телефон 8-495-123.", "chunk_id": 2}]
    ok_answer = "Офис на ул. Ленина, 10. [Источник: чанк 1]"
    bad_answer = "Офис на Ленина. Подробнее в чанке 5."
    print("OK:", format_answer_with_verification(ok_answer, context))
    print("Unverified:", format_answer_with_verification(bad_answer, context))
