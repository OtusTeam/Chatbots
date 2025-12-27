AVAILABLE_JOBS: tuple[str, ...] = (
    'Программист',
    'Менеджер',
    'Дизайнер',
    'Маркетолог',
)

AVAILABLE_GRADES: tuple[str, ...] = (
    'Junior',
    'Middle',
    'Senior',
)


def get_jobs() -> tuple[str, ...]:
    return AVAILABLE_JOBS


def get_grades() -> tuple[str, ...]:
    return AVAILABLE_GRADES