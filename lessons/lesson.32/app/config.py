import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    webhook_url: str
    webhook_path: str
    webhook_host: str
    webhook_port: int
    database_url: str
    redis_url: str


settings = Settings(
    telegram_bot_token=_get_required("TELEGRAM_BOT_TOKEN"),
    webhook_url=_get_required("WEBHOOK_URL"),
    webhook_path=os.getenv("WEBHOOK_PATH", "/webhook"),
    webhook_host=os.getenv("WEBHOOK_HOST", "0.0.0.0"),
    webhook_port=int(os.getenv("WEBHOOK_PORT", "8000")),
    database_url=_get_required("DATABASE_URL"),
    redis_url=_get_required("REDIS_URL"),
)
