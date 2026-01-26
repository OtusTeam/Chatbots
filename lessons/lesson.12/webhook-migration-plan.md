# План миграции: Long Polling → Webhook

## Файлы для изменения

### 1. `config/config.py`
**Изменения:**
После строки:

```python
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
```

добавить:

```python
webhook_url = os.getenv("WEBHOOK_URL")  # Базовый URL вебхука
webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")  # Путь для webhook, по умолчанию /webhook
webhook_host = os.getenv("WEBHOOK_HOST", "0.0.0.0")  # Хост для FastAPI сервера
webhook_port = int(os.getenv("WEBHOOK_PORT", "8000"))  # Порт для FastAPI сервера
```

---

### 2. `.env.example`
**Изменения:**
После строки с `TELEGRAM_BOT_TOKEN` добавить:

```env
# Webhook настройки (для локальной работы используйте туннель: Ngrok/Cloudflared)
WEBHOOK_URL=https://abc123.ngrok.io/webhook  # Замените на URL от туннеля
WEBHOOK_PATH=/webhook
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
```

---

### 3. `main_webhook.py` (новый файл)

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from config.config import (
    telegram_bot_token,
    webhook_url,
    webhook_path,
    webhook_host,
    webhook_port,
)
from app.handlers.routers import root_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Инициализация бота и диспетчера
bot = Bot(token=telegram_bot_token)
dp = Dispatcher()
dp.include_router(root_router)


async def setup_webhook():
    """Установка webhook в Telegram."""
    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL not set. Проверьте .env файл")

    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для FastAPI."""
    # Startup
    await setup_webhook()
    yield
    # Shutdown
    await bot.session.close()


# FastAPI приложение с lifespan
app = FastAPI(title="Telegram Bot Webhook", lifespan=lifespan)


@app.post(webhook_path)
async def webhook_handler(request: Request):
    """Обработчик webhook от Telegram."""
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/health")
async def health_check():
    """Health-check endpoint."""
    return {
        "status": "healthy",
        "service": "telegram-bot",
        "webhook": "configured",
    }


if __name__ == "__main__":
    import uvicorn

    # Запуск FastAPI сервера
    # lifespan будет вызван автоматически при старте и остановке
    uvicorn.run(
        app,
        host=webhook_host,
        port=webhook_port,
    )
```
---

### 4. `requirements.txt`
```text
fastapi>=0.128.0
python-dotenv>=0.9.9
uvicorn[standard]>=0.40.0
```

---


**Для локальной разработки необходимо использовать туннелирование.**

#### Вариант A: Ngrok

1. **Установка Ngrok:**
   - Windows: `choco install ngrok` или скачать с [ngrok.com](https://ngrok.com)
   - Linux/Mac: `brew install ngrok` или скачать бинарник

2. **Запуск туннеля:**
   ```bash
   ngrok http 8000
   ```
   
3. **Получить публичный URL:**
   - В выводе ngrok найти строку: `Forwarding: https://abc123.ngrok.io -> http://localhost:8000`
   - Скопировать URL: `https://abc123.ngrok.io`

#### Вариант B: Cloudflared (Cloudflare Tunnel)

1. **Установка Cloudflared:**
   - Windows: `choco install cloudflared`
   - Linux/Mac: `brew install cloudflared`

2. **Запуск туннеля:**
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
   
3. **Получить публичный URL:**
   - В выводе найти строку: `https://random-subdomain.trycloudflare.com`
   - Скопировать этот URL

**Важно:** URL туннеля меняется при каждом перезапуске (бесплатный план). После каждого перезапуска туннеля нужно обновить `WEBHOOK_URL` в `.env` файле.

---
