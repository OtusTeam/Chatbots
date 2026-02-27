"""
Простые метрики качества RAG: доля ответов с цитатой, доля «не знаю» / «не нашёл».
Для демонстрации и логирования.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QualityMetrics:
    total: int = 0
    with_citation: int = 0
    no_answer: int = 0
    errors: int = 0

    def record(self, has_citation: bool, no_answer: bool, error: bool = False) -> None:
        self.total += 1
        if error:
            self.errors += 1
        elif no_answer:
            self.no_answer += 1
        elif has_citation:
            self.with_citation += 1
        print(
            f"[metrics] total={self.total}, with_citation={self.with_citation}, "
            f"no_answer={self.no_answer}, errors={self.errors}"
        )

    @property
    def citation_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.with_citation / self.total

    @property
    def no_answer_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.no_answer / self.total

    def summary(self) -> str:
        return (
            f"Всего запросов: {self.total}, "
            f"с цитатой: {self.with_citation} ({self.citation_rate:.1%}), "
            f"«не знаю»/не нашёл: {self.no_answer} ({self.no_answer_rate:.1%}), "
            f"ошибок: {self.errors}"
        )


# Глобальный экземпляр для логирования (опционально)
_metrics: QualityMetrics | None = None


def get_metrics() -> QualityMetrics:
    global _metrics
    if _metrics is None:
        _metrics = QualityMetrics()
    return _metrics
