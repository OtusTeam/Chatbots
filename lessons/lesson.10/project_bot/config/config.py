import os
from dotenv import load_dotenv


load_dotenv()

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
database_url = os.getenv("DATABASE_URL")
llm_api_key = os.getenv("LLM_API_KEY", 'defaut_key_llm')


if __name__ == '__main__':
    print(telegram_bot_token)
    print(database_url)
    print(llm_api_key)