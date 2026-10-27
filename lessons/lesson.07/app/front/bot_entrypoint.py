import logging


def setup_logging() -> None:
    """Настройка логов."""
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        force=True
    )
    logging.getLogger("aiogram").setLevel(logging.WARNING)


logger = logging.getLogger('ChatBots')
