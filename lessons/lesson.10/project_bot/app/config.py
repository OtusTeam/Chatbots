import os
from dotenv import load_dotenv


load_dotenv()

APP_NAME = "Clinic Assistant"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
LLM_KEY_TOKEN = os.getenv("TOKEN_LLM")
DATABASE_URL = os.getenv("DATABASE_URL")


if __name__ == '__main__':
    print(APP_NAME)
    print(TELEGRAM_BOT_TOKEN)
    print(LLM_KEY_TOKEN)
    print(DATABASE_URL)