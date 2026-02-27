"""
Прогон списка запросов через fallback_chain и вывод метрик.
Удобно для заполнения отчёта примеров (report_examples.md) и проверки качества.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_LESSON_DIR = _SCRIPT_DIR.parent
if str(_LESSON_DIR) not in sys.path:
    sys.path.insert(0, str(_LESSON_DIR))
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from fallback_chain import fallback_chain
from quality_metrics import QualityMetrics


# Примеры запросов для прогона (подставьте свои или передайте из файла)
DEFAULT_QUERIES = [
    "Привет",
    "Как дела?",
    "Где офис?",
    "Режим работы",
    "Что-нибудь не из базы документов",
]


def classify_response(answer: str, source: str | None) -> tuple[bool, bool, bool]:
    """(has_citation, no_answer, error)."""
    if "Попробуйте позже" in answer or (not answer.strip() and source is None):
        return False, False, True
    if source is not None:
        return True, False, False
    if "не нашёл" in answer.lower() or "не знаю" in answer.lower():
        return False, True, False
    # FAQ или ответ без явной цитаты
    return False, False, False


def main() -> None:
    queries = DEFAULT_QUERIES
    if len(sys.argv) > 1:
        # Читаем запросы из файла: один запрос на строку
        path = Path(sys.argv[1])
        if path.exists():
            queries = [q.strip() for q in path.read_text(encoding="utf-8").splitlines() if q.strip()]

    metrics = QualityMetrics()
    print("Запрос | Ответ (кратко) | Источник | Метка")
    print("-" * 80)

    for q in queries:
        answer, source = fallback_chain(q)
        has_citation, no_answer, error = classify_response(answer, source)
        metrics.record(has_citation=has_citation, no_answer=no_answer, error=error)

        if no_answer:
            label = "не знаю"
        elif error:
            label = "ошибка"
        elif has_citation:
            label = "с цитатой"
        else:
            label = "ответ без цитаты (например FAQ)"

        short = (answer[:50] + "…") if len(answer) > 50 else answer
        src_str = source if source else "—"
        print(f"{q!r} | {short!r} | {src_str} | {label}")

    print("-" * 80)
    print(metrics.summary())


if __name__ == "__main__":
    print("[run_queries_metrics] Прогон запросов через fallback_chain и сбор метрик качества.")
    main()
