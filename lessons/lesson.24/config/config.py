import os
from dotenv import load_dotenv


load_dotenv()

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")  # Базовый URL вебхука
webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")  # Путь для webhook, по умолчанию /webhook
webhook_host = os.getenv("WEBHOOK_HOST", "0.0.0.0")  # Хост для FastAPI сервера
webhook_port = int(os.getenv("WEBHOOK_PORT", "8000"))  # Порт для FastAPI сервера
database_url = os.getenv("DATABASE_URL")

# GigaChat LLM
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_MAX_TOKENS = int(os.getenv("GIGACHAT_MAX_TOKENS", "500"))
GIGACHAT_TEMPERATURE = float(os.getenv("GIGACHAT_TEMPERATURE", "0.2"))


if __name__ == '__main__':
    print(telegram_bot_token)
    print(database_url)
    print("GIGACHAT_CREDENTIALS:", "set" if GIGACHAT_CREDENTIALS else "not set")