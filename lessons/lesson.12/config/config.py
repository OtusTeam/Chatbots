import os
from dotenv import load_dotenv


load_dotenv()

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")  # Базовый URL вебхука
webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")  # Путь для webhook, по умолчанию /webhook
webhook_host = os.getenv("WEBHOOK_HOST", "0.0.0.0")  # Хост для FastAPI сервера
webhook_port = int(os.getenv("WEBHOOK_PORT", "8000"))  # Порт для FastAPI сервера
database_url = os.getenv("DATABASE_URL")
llm_api_key = os.getenv("LLM_API_KEY", 'defaut_key_llm')


if __name__ == '__main__':
    print(telegram_bot_token)
    print(database_url)
    print(llm_api_key)