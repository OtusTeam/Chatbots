# Методические указания к домашнему заданию (Урок 13)

## Цель домашнего задания

В рамках этого ДЗ вы научитесь:
1. Создавать FastAPI-приложение с маршрутами для webhook и health-check
2. Переводить Telegram-бота с Long Polling на Webhook режим
3. Использовать туннелирование (ngrok/cloudflared) для локальной разработки с webhook
4. Контейнеризировать бота с помощью Docker и Docker Compose
5. Настраивать персистентное хранение данных через Docker volumes (SQLite)
6. Рассматривать вариант перехода на PostgreSQL в Docker Compose

---

## Введение: зачем это нужно?

### Зачем Webhook вместо Long Polling?

**Long Polling** — это режим, когда ваш бот постоянно опрашивает серверы Telegram: "Есть ли новые сообщения?". Это работает, но имеет ограничения:
- Бот должен быть постоянно запущен и подключен к интернету
- При большом количестве ботов серверы Telegram получают много запросов
- Не подходит для масштабирования

**Webhook** — это режим, когда Telegram сам отправляет обновления на ваш сервер по HTTP. Преимущества:
- Telegram отправляет данные только когда есть обновления
- Ваш сервер может обрабатывать запросы асинхронно
- Лучше подходит для продакшена и масштабирования
- Можно использовать стандартные веб-инструменты (логирование, мониторинг, балансировка)

### Зачем endpoint `/health`?

Health-check endpoint нужен для:
- **Мониторинга**: внешние системы могут проверять, работает ли ваш сервис
- **Оркестрации**: Docker/Kubernetes используют health-check для автоматического перезапуска неработающих контейнеров
- **Отладки**: быстрая проверка, что сервер запущен и отвечает

### Зачем Docker и Docker Compose?

**Docker** решает проблему "у меня работает, у тебя нет":
- Изолированное окружение с фиксированными версиями зависимостей
- Одинаковая работа на Windows, Linux, macOS
- Простой деплой: собрал образ → перенёс → запустил

**Docker Compose** упрощает управление несколькими сервисами:
- Бот и база данных (SQLite/PostgreSQL) в одном файле конфигурации
- Автоматическое создание сетей и volumes
- Одна команда для запуска всего стека

### Зачем SQLite в volume?

SQLite хранит данные в файле. Если файл находится внутри контейнера:
- При удалении контейнера данные теряются
- Невозможно обновить код без потери данных

**Volume** — это способ сохранить данные вне контейнера:
- Данные переживают перезапуск и пересборку контейнера
- Можно делать бэкапы, просто копируя файл
- Можно монтировать один и тот же файл в разные контейнеры

---

## Шаг 1: Подготовка переменных окружения

### Что нужно сделать

1. Скопируйте файл `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Откройте `.env` в текстовом редакторе и заполните значения.

### Объяснение переменных

#### `TELEGRAM_BOT_TOKEN`
Токен вашего бота, полученный от [@BotFather](https://t.me/BotFather).

**Зачем**: Без токена бот не сможет авторизоваться в API Telegram.

**Пример**:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### `WEBHOOK_URL`
Публичный URL, на который Telegram будет отправлять обновления.

**Важно**: 
- URL должен быть **публично доступен** (не `localhost` или `127.0.0.1`)
- URL должен использовать **HTTPS** (Telegram требует SSL)
- URL должен **включать путь** webhook (например, `https://abc123.ngrok.io/webhook`)

**Зачем**: Telegram может отправлять обновления только на публичные HTTPS-адреса. Для локальной разработки используем туннель (см. Шаг 3).

**Пример** (будет заполнен после настройки туннеля):
```env
WEBHOOK_URL=https://abc123.ngrok.io/webhook
```

#### `WEBHOOK_PATH`
Путь, по которому FastAPI будет принимать обновления от Telegram.

**Зачем**: Позволяет иметь несколько эндпоинтов на одном домене (например, `/webhook` для бота, `/api` для другого сервиса).

**По умолчанию**: `/webhook`

#### `WEBHOOK_HOST` и `WEBHOOK_PORT`
Адрес и порт, на которых будет слушать FastAPI сервер.

**Зачем**: 
- `0.0.0.0` означает "слушать на всех сетевых интерфейсах" (нужно для Docker)
- Порт `8000` — стандартный для FastAPI, но можно изменить

**Важно**: В Docker Compose порт будет проброшен наружу, чтобы туннель мог к нему подключиться.

#### `DATABASE_URL`
Строка подключения к базе данных.

**Для SQLite**:
```env
DATABASE_URL=sqlite:////data/db.sqlite
```

**Важно**: 
- Четыре слэша `////` — это правильный формат для абсолютного пути в SQLAlchemy
- Путь `/data/db.sqlite` — это путь **внутри контейнера**, где будет монтирован volume

**Зачем**: SQLAlchemy и другие ORM используют эту строку для подключения к БД. Формат универсальный и позволяет легко переключиться на PostgreSQL (см. Шаг 7).

---

## Шаг 2: Создание FastAPI приложения с webhook и health-check

### Что нужно сделать

В вашем проекте уже должен быть файл `main_webhook.py`. Если его нет, создайте его на основе `main.py` (который использует Long Polling).

### Разбор структуры `main_webhook.py`

#### Импорты и настройка логирования

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
```

**Зачем**:
- `asynccontextmanager` — для управления жизненным циклом приложения (startup/shutdown)
- `FastAPI` — веб-фреймворк для создания API
- `Request`, `Response` — для работы с HTTP-запросами
- `Update` — тип данных от Telegram API

#### Инициализация бота и диспетчера

```python
bot = Bot(token=telegram_bot_token)
dp = Dispatcher()
dp.include_router(root_router)
```

**Зачем**: Та же логика, что и в Long Polling режиме. Диспетчер обрабатывает обновления через те же хэндлеры.

#### Функция установки webhook

```python
async def setup_webhook():
    """Установка webhook в Telegram."""
    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL not set. Проверьте .env файл")
    
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")
```

**Зачем**: 
- `bot.set_webhook()` сообщает Telegram: "Отправляй обновления на этот URL"
- После этого Telegram перестанет отправлять обновления через Long Polling
- Если webhook не установлен, бот не будет получать сообщения

**Важно**: Webhook устанавливается **один раз при старте приложения**. Если вы измените `WEBHOOK_URL`, нужно перезапустить приложение.

#### Lifecycle events (lifespan)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для FastAPI."""
    # Startup
    await setup_webhook()
    yield
    # Shutdown
    await bot.session.close()
```

**Зачем**:
- **Startup** (до `yield`): выполняется при запуске сервера. Здесь устанавливаем webhook.
- **Shutdown** (после `yield`): выполняется при остановке. Здесь закрываем сессию бота, чтобы освободить ресурсы.

**Почему это важно**: Без правильного закрытия сессии могут остаться "висящие" соединения, что приведёт к утечкам памяти.

#### Создание FastAPI приложения

```python
app = FastAPI(title="Telegram Bot Webhook", lifespan=lifespan)
```

**Зачем**: `lifespan=lifespan` связывает нашу функцию жизненного цикла с приложением.

#### Обработчик webhook

```python
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
```

**Как это работает**:
1. Telegram отправляет POST-запрос на `WEBHOOK_URL` с JSON-данными обновления
2. Мы парсим JSON в объект `Update`
3. Передаём обновление в диспетчер через `dp.feed_update()` — он вызывает нужные хэндлеры
4. Возвращаем `200 OK`, чтобы Telegram знал, что мы получили обновление

**Зачем try/except**: Если произойдёт ошибка, мы логируем её, но всё равно возвращаем ответ Telegram. Иначе Telegram может подумать, что сервер недоступен, и перестанет отправлять обновления.

#### Health-check endpoint

```python
@app.get("/health")
async def health_check():
    """Health-check endpoint."""
    return {"status": "ok"}
```

**Зачем**: Простой endpoint для проверки работоспособности сервера.

**Требование ДЗ**: Должен возвращать **ровно** `{"status": "ok"}`.

#### Запуск сервера

```python
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=webhook_host,
        port=webhook_port,
    )
```

**Зачем**: `uvicorn` — это ASGI-сервер, который запускает FastAPI приложение. В Docker это будет запускаться автоматически через `CMD` в Dockerfile.

---

## Шаг 3: Настройка туннеля для локальной разработки

### Зачем нужен туннель?

Telegram требует, чтобы webhook был доступен по **публичному HTTPS URL**. Ваш локальный сервер (`localhost:8000`) не публичен, поэтому нужен туннель.

**Туннель** — это сервис, который:
- Создаёт публичный HTTPS URL (например, `https://abc123.ngrok.io`)
- Перенаправляет все запросы на этот URL на ваш локальный сервер

### Вариант A: Ngrok

#### Установка

**Windows** (через Chocolatey):
```bash
choco install ngrok
```

**Linux/Mac** (через Homebrew):
```bash
brew install ngrok
```

Или скачайте с [ngrok.com](https://ngrok.com/download).

#### Регистрация (опционально, но рекомендуется)

1. Зарегистрируйтесь на [ngrok.com](https://ngrok.com)
2. Получите authtoken
3. Выполните:
   ```bash
   ngrok config add-authtoken YOUR_TOKEN
   ```

**Зачем**: Без регистрации туннель будет работать только 2 часа, URL будет меняться при каждом перезапуске.

#### Запуск туннеля

```bash
ngrok http 8000
```

**Что происходит**:
- Ngrok создаёт публичный URL (например, `https://abc123.ngrok.io`)
- Все запросы на этот URL перенаправляются на `http://localhost:8000`

**Важно**: Оставьте этот терминал открытым! Если закрыть, туннель прекратит работу.

#### Получение URL

В выводе ngrok найдите строку:
```
Forwarding: https://abc123.ngrok.io -> http://localhost:8000
```

Скопируйте URL: `https://abc123.ngrok.io`

#### Обновление `.env`

Добавьте путь webhook к URL:
```env
WEBHOOK_URL=https://abc123.ngrok.io/webhook
```

**Важно**: URL должен **включать путь** `/webhook`, так как это значение `WEBHOOK_PATH`.

### Вариант B: Cloudflared (Cloudflare Tunnel)

#### Установка

**Windows** (через Chocolatey):
```bash
choco install cloudflared
```

**Linux/Mac** (через Homebrew):
```bash
brew install cloudflared
```

Или скачайте с [developers.cloudflare.com](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/).

#### Запуск туннеля

```bash
cloudflared tunnel --url http://localhost:8000
```

**Что происходит**: Аналогично ngrok, создаётся публичный URL.

#### Получение URL

В выводе найдите строку:
```
https://random-subdomain.trycloudflare.com
```

Скопируйте этот URL и обновите `.env`:
```env
WEBHOOK_URL=https://random-subdomain.trycloudflare.com/webhook
```

### Важные замечания

1. **URL меняется при перезапуске** (на бесплатном плане). После каждого перезапуска туннеля нужно:
   - Получить новый URL
   - Обновить `WEBHOOK_URL` в `.env`
   - Перезапустить бота (чтобы webhook переустановился)

2. **Туннель должен работать постоянно**, пока работает бот. Если туннель упадёт, Telegram не сможет доставить обновления.

3. **Для продакшена** используйте постоянный домен и SSL-сертификат (например, через Let's Encrypt).

---

## Шаг 4: Переключение с Long Polling на Webhook

### Взаимоисключаемость режимов

**Важно**: Telegram не позволяет использовать Long Polling и Webhook одновременно. Если установлен webhook, Long Polling автоматически отключается, и наоборот.

### Как переключиться на Webhook

1. **Убедитесь, что `main.py` (Long Polling) не запущен**

2. **Запустите туннель** (см. Шаг 3)

3. **Обновите `.env`** с правильным `WEBHOOK_URL`

4. **Запустите `main_webhook.py`**:
   ```bash
   python main_webhook.py
   ```

5. **Проверьте логи**: Должна быть строка:
   ```
   INFO: Webhook установлен: https://abc123.ngrok.io/webhook
   ```

6. **Проверьте webhook в Telegram**:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
   ```
   
   Должен вернуться JSON с полем `"url"`, содержащим ваш webhook URL.

### Как вернуться к Long Polling (для отладки)

Если нужно временно вернуться к Long Polling:

1. **Удалите webhook**:
   ```python
   # Временный скрипт remove_webhook.py
   import asyncio
   from aiogram import Bot
   from config.config import telegram_bot_token
   
   async def remove():
       bot = Bot(token=telegram_bot_token)
       await bot.delete_webhook()
       print("Webhook удалён")
       await bot.session.close()
   
   asyncio.run(remove())
   ```

2. **Запустите `main.py`** (Long Polling)

**Зачем это нужно**: Иногда проще отлаживать бота через Long Polling (не нужен туннель), а затем переключаться на Webhook для тестирования в условиях, близких к продакшену.

---

## Шаг 5: Создание Dockerfile

### Что такое Dockerfile?

**Dockerfile** — это инструкция для сборки образа. Образ — это "снимок" вашего приложения со всеми зависимостями.

### Разбор Dockerfile (многостадийная сборка)

Ваш `Dockerfile` использует **многостадийную сборку** (multi-stage build):

#### Стадия 1: Builder

```dockerfile
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Build-time deps
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

# Install Python deps into a dedicated venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt
```

**Что происходит**:
- Используем образ `python:3.12-slim` (лёгкая версия Python)
- Устанавливаем `build-essential` (нужен для компиляции некоторых Python-пакетов)
- Создаём виртуальное окружение `/opt/venv`
- Устанавливаем все зависимости из `requirements.txt`

**Зачем venv внутри образа?**:
- Изоляция зависимостей от системного Python
- Легче управлять версиями пакетов
- Можно копировать venv между стадиями

**Зачем `--no-install-recommends` и `rm -rf`?**:
- Уменьшаем размер образа, удаляя ненужные пакеты и кэш

#### Стадия 2: Runtime

```dockerfile
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime deps
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# App code
COPY . /app

# Data directory for SQLite file
RUN mkdir -p /data

# Default: webhook mode
CMD ["python", "main_webhook.py"]
```

**Что происходит**:
- Создаём новый, чистый образ (без build-essential)
- Копируем только venv из стадии builder (без исходников компиляции)
- Копируем код приложения
- Создаём директорию `/data` для SQLite файла
- Устанавливаем команду запуска

**Зачем две стадии?**:
- **Builder** содержит инструменты компиляции (build-essential) — они нужны только при установке пакетов
- **Runtime** содержит только то, что нужно для работы приложения
- **Результат**: финальный образ меньше по размеру (экономия места и времени загрузки)

**Зачем `/data`?**:
- SQLite файл будет храниться в `/data/db.sqlite`
- Эта директория будет смонтирована как volume в docker-compose
- Данные сохранятся при пересборке образа

### Сборка образа

```bash
docker build -t telegram-bot .
```

**Что происходит**:
- Docker читает `Dockerfile` и выполняет все инструкции
- Создаётся образ с тегом `telegram-bot`

**Проверка**:
```bash
docker images
```

Должен появиться образ `telegram-bot`.

---

## Шаг 6: Настройка Docker Compose (SQLite)

### Что такое docker-compose.yml?

**Docker Compose** — это инструмент для запуска нескольких связанных контейнеров. В одном файле описываются все сервисы, их настройки, сети и volumes.

### Разбор docker-compose.yml

```yaml
services:
  bot:
    build:
      context: .
    env_file:
      - .env
    ports:
      - "${WEBHOOK_PORT:-8000}:${WEBHOOK_PORT:-8000}"
    volumes:
      - sqlite_data:/data
    restart: unless-stopped

volumes:
  sqlite_data:
```

#### Секция `services`

**`bot`** — имя сервиса (можете назвать как угодно).

**`build.context: .`**:
- Указывает, что образ нужно собрать из Dockerfile в текущей директории
- Альтернатива: `image: telegram-bot` (если образ уже собран)

**`env_file: - .env`**:
- Загружает все переменные из `.env` в контейнер
- Эквивалентно `docker run --env-file .env`

**`ports`**:
- Формат: `"HOST_PORT:CONTAINER_PORT"`
- `${WEBHOOK_PORT:-8000}` означает: "используй значение `WEBHOOK_PORT` из `.env`, если его нет — используй `8000`"
- Пробрасывает порт из контейнера на хост, чтобы туннель мог подключиться

**`volumes: - sqlite_data:/data`**:
- `sqlite_data` — имя volume (создаётся автоматически)
- `/data` — путь внутри контейнера, куда монтируется volume
- SQLite файл будет храниться в этом volume

**Зачем volume?**:
- Без volume данные хранятся внутри контейнера
- При удалении контейнера (`docker compose down`) данные теряются
- С volume данные сохраняются в Docker и переживают пересоздание контейнера

**`restart: unless-stopped`**:
- Автоматически перезапускает контейнер при падении
- Не перезапускает, если контейнер был остановлен вручную

#### Секция `volumes`

**`sqlite_data:`** — объявляет именованный volume. Docker создаст его автоматически при первом запуске.

**Где хранится volume?**:
- На Linux: `/var/lib/docker/volumes/`
- На Windows/Mac: внутри Docker Desktop VM

**Как посмотреть volumes?**:
```bash
docker volume ls
```

**Как удалить volume?**:
```bash
docker compose down -v
```

Флаг `-v` удаляет volumes вместе с контейнерами. **Внимание**: это удалит все данные в SQLite!

### Запуск стека

1. **Убедитесь, что туннель запущен** (см. Шаг 3)

2. **Проверьте `.env`**:
   - `WEBHOOK_URL` должен содержать URL туннеля
   - `DATABASE_URL=sqlite:////data/db.sqlite`

3. **Запустите контейнеры**:
   ```bash
   docker compose up -d
   ```

   Флаг `-d` запускает в фоновом режиме (detached).

4. **Проверьте логи**:
   ```bash
   docker compose logs -f bot
   ```

   Должны увидеть:
   ```
   INFO: Webhook установлен: https://abc123.ngrok.io/webhook
   INFO: Application startup complete.
   ```

5. **Проверьте health-check**:
   ```bash
   curl http://localhost:8000/health
   ```

   Должен вернуться:
   ```json
   {"status":"ok"}
   ```

6. **Проверьте, что бот отвечает**: Отправьте сообщение боту в Telegram.

### Полезные команды Docker Compose

**Просмотр логов**:
```bash
docker compose logs -f bot
```

**Остановка**:
```bash
docker compose down
```

**Перезапуск** (после изменения кода):
```bash
docker compose restart bot
```

**Пересборка образа** (после изменения Dockerfile или requirements.txt):
```bash
docker compose build bot
docker compose up -d
```

**Просмотр запущенных контейнеров**:
```bash
docker compose ps
```

**Вход в контейнер** (для отладки):
```bash
docker compose exec bot bash
```

**Проверка SQLite файла**:
```bash
docker compose exec bot ls -la /data
```

Должен быть файл `db.sqlite` (если бот уже создал БД).

---

## Шаг 7: Вариант с PostgreSQL

### Зачем переходить на PostgreSQL?

**SQLite** подходит для:
- Небольших проектов
- Одного пользователя/процесса
- Прототипирования

**PostgreSQL** нужен для:
- Многопользовательских приложений
- Высокой нагрузки
- Сложных запросов и транзакций
- Горизонтального масштабирования

### Создание docker-compose.postgres.yml

Создайте файл `docker-compose.postgres.yml`:

```yaml
services:
  bot:
    build:
      context: .
    env_file:
      - .env
    ports:
      - "${WEBHOOK_PORT:-8000}:${WEBHOOK_PORT:-8000}"
    volumes:
      - sqlite_data:/data  # Можно оставить для совместимости или убрать
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-telegram_bot}
      POSTGRES_USER: ${POSTGRES_USER:-bot_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-bot_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    ports:
      - "5432:5432"  # Опционально, для доступа с хоста

volumes:
  sqlite_data:
  postgres_data:
```

### Разбор конфигурации PostgreSQL

**`image: postgres:16-alpine`**:
- Официальный образ PostgreSQL версии 16
- `alpine` — лёгкая версия на базе Alpine Linux (меньший размер)

**`environment`**:
- `POSTGRES_DB` — имя базы данных
- `POSTGRES_USER` — пользователь
- `POSTGRES_PASSWORD` — пароль

**Важно**: В продакшене **никогда** не храните пароли в `.env` файле, который попадает в git! Используйте секреты (Docker secrets, Kubernetes secrets, etc.).

**`volumes: - postgres_data:/var/lib/postgresql/data`**:
- PostgreSQL хранит данные в `/var/lib/postgresql/data`
- Volume обеспечивает персистентность данных

**`depends_on: - postgres`**:
- Указывает, что контейнер `bot` должен запускаться **после** `postgres`
- Docker Compose автоматически ждёт, пока PostgreSQL станет доступен

### Обновление .env для PostgreSQL

Добавьте в `.env`:

```env
# PostgreSQL настройки
POSTGRES_DB=telegram_bot
POSTGRES_USER=bot_user
POSTGRES_PASSWORD=bot_password

# DATABASE_URL для PostgreSQL
# Формат: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
# В Docker Compose имя сервиса (postgres) используется как hostname
DATABASE_URL=postgresql://bot_user:bot_password@postgres:5432/telegram_bot
```

**Важно**: 
- `postgres` в URL — это имя сервиса из docker-compose (Docker автоматически создаёт DNS-запись)
- Порт `5432` — стандартный порт PostgreSQL

### Запуск с PostgreSQL

```bash
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d
```

Или создайте отдельный файл `docker-compose.override.yml` (Docker Compose автоматически подхватит его):

```bash
docker compose up -d
```

### Что нужно изменить в коде для работы с PostgreSQL?

**Текущий код** (предполагается, что используется SQLAlchemy или аналогичная ORM):

1. **Установить драйвер PostgreSQL**:
   ```bash
   pip install psycopg2-binary
   # или
   pip install asyncpg  # для асинхронного доступа
   ```

2. **Обновить `requirements.txt`**:
   ```
   psycopg2-binary>=2.9.0
   ```

3. **Код подключения к БД** обычно не требует изменений, если используется `DATABASE_URL`:
   ```python
   from sqlalchemy import create_engine
   
   engine = create_engine(database_url)  # Работает и для SQLite, и для PostgreSQL
   ```

4. **Миграции схемы БД**:
   - SQLite и PostgreSQL имеют разные типы данных
   - Нужно будет создать миграции (например, через Alembic) для переноса схемы
   - Это выходит за рамки данного ДЗ, но важно понимать

**Зачем это важно знать**: При переходе на PostgreSQL в реальном проекте нужно будет:
- Обновить зависимости
- Создать миграции
- Протестировать на тестовой БД перед продакшеном

### Проверка работы PostgreSQL

1. **Проверьте логи PostgreSQL**:
   ```bash
   docker compose logs postgres
   ```

   Должна быть строка:
   ```
   database system is ready to accept connections
   ```

2. **Подключитесь к PostgreSQL из контейнера бота**:
   ```bash
   docker compose exec bot python -c "from config.config import database_url; print(database_url)"
   ```

   Должен вывести правильный `DATABASE_URL`.

3. **Подключитесь к PostgreSQL напрямую** (если порт проброшен):
   ```bash
   docker compose exec postgres psql -U bot_user -d telegram_bot
   ```

---

## Чек-лист сдачи домашнего задания

### Что должно быть в репозитории

1. ✅ Файл `main_webhook.py` с маршрутами:
   - `POST /webhook` (или путь из `WEBHOOK_PATH`)
   - `GET /health` (возвращает `{"status": "ok"}`)

2. ✅ Файл `.env` (не должен попадать в git! Проверьте `.gitignore`)

3. ✅ Файл `Dockerfile` для сборки образа бота

4. ✅ Файл `docker-compose.yml` с:
   - Сервисом `bot`
   - Volume для SQLite
   - Переменными окружения из `.env`

5. ✅ Файл `docker-compose.postgres.yml` (опционально, но рекомендуется) с конфигурацией PostgreSQL

6. ✅ Обновлённый `.env.example` с примерами для PostgreSQL

### Как проверить, что всё работает

1. **Запустите туннель** (ngrok или cloudflared)

2. **Обновите `.env`** с URL туннеля

3. **Запустите через Docker Compose**:
   ```bash
   docker compose up -d
   ```

4. **Проверьте health-check**:
   ```bash
   curl http://localhost:8000/health
   ```
   
   Ожидаемый ответ:
   ```json
   {"status":"ok"}
   ```

5. **Проверьте логи**:
   ```bash
   docker compose logs bot
   ```
   
   Должна быть строка об установке webhook.

6. **Отправьте сообщение боту** в Telegram — бот должен ответить.

7. **Проверьте webhook в Telegram API**:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
   ```

8. **Проверьте SQLite файл** (если используете SQLite):
   ```bash
   docker compose exec bot ls -la /data
   ```

### Типичные проблемы и решения

**Проблема**: `WEBHOOK_URL not set`
- **Решение**: Проверьте, что `.env` файл существует и содержит `WEBHOOK_URL`

**Проблема**: `Connection refused` при запросе к `/health`
- **Решение**: Проверьте, что контейнер запущен (`docker compose ps`) и порт проброшен правильно

**Проблема**: Бот не отвечает на сообщения
- **Решение**: 
  1. Проверьте логи: `docker compose logs bot`
  2. Проверьте webhook: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
  3. Убедитесь, что туннель работает

**Проблема**: Данные в SQLite теряются после `docker compose down`
- **Решение**: Проверьте, что volume правильно смонтирован в `docker-compose.yml`

**Проблема**: PostgreSQL не запускается
- **Решение**: 
  1. Проверьте логи: `docker compose logs postgres`
  2. Убедитесь, что переменные `POSTGRES_*` установлены в `.env`

---

## Дополнительные материалы

- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Документация aiogram](https://docs.aiogram.dev/)
- [Документация Docker](https://docs.docker.com/)
- [Документация Docker Compose](https://docs.docker.com/compose/)
- [Ngrok Documentation](https://ngrok.com/docs)
- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

---

## Заключение

После выполнения этого ДЗ вы:
- ✅ Понимаете разницу между Long Polling и Webhook
- ✅ Умеете создавать FastAPI приложения с health-check
- ✅ Знаете, как использовать туннелирование для локальной разработки
- ✅ Можете контейнеризировать приложение с Docker
- ✅ Понимаете, как настраивать персистентное хранение данных через volumes
- ✅ Рассмотрели вариант перехода на PostgreSQL

Удачи в выполнении домашнего задания! 🚀
