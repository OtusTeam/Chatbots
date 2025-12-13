## На занятии

Мы делаем **первую версию Telegram-бота на aiogram**, чтобы он:

* запускался локально в режиме **Long Polling**;
* отвечал на **/start** и **/help**;
* отвечал на любой обычный текст (**fallback**);
* принимал **фото и видео**, показывал метаданные;
* писал **логи через logging**, чтобы отлаживать как в реальных проектах.

---

## 1) Регистрация бота в BotFather 

1. В Telegram найдите **@BotFather**
2. Отправьте команду:

* `/newbot`

3. BotFather спросит:

* **Name** (любое отображаемое имя)
* **Username** (должен оканчиваться на `bot`, например `my_assistant_bot`)

4. В ответ получите **TOKEN** вида:

* `1234567890:AA...`

Это **секрет**, его нельзя выкладывать в GitHub.

(Опционально) меню команд в Telegram:

* `/setcommands`
* выбираем бота
* задаём:

  * `start - Запуск`
  * `help - Справка`

---

## 2) Секреты проекта: `.env`, `.env.example`, `.gitignore`

### Файл: `lesson.04/.env`

Создаём `.env` и кладём туда токен:

```env
TELEGRAM_BOT_TOKEN=1234567890:AA...ваш_токен...
```

### Файл: `lesson.04/.env.example`

Шаблон без секретов (его коммитим):

```env
TELEGRAM_BOT_TOKEN=
```

### Файл: `lesson.04/.gitignore`

Проверяем/добавляем (чтобы секреты и медиа не попадали в Git):

```gitignore
.env
data/media/
```

---

## 3) Установка aiogram (Poetry или pip)

### Вариант A — Poetry (рекомендуется)

```bash
poetry add aiogram
```

### Вариант B — pip (если проект на venv/pip)

```bash
pip install aiogram
```

---

## 4) Основные сущности aiogram 

* **Bot** — клиент Telegram API (отправляет/получает данные через Telegram).
* **Handler (хендлер)** — функция, которая реагирует на событие (сообщение, фото, видео, команду).
* **Router** — “набор правил” (хендлеров), которые подключаются к Dispatcher.
* **Dispatcher** — “движок”, который получает апдейты и раздаёт их нужным хендлерам.
* **Long Polling** — бот сам регулярно спрашивает Telegram “есть ли новые сообщения?”.
* * **Message** — объект входящего сообщения (текст/фото/видео/команда).
* **Filters** — условия “на что реагируем” (команда, текст, фото, видео).
* **file_id** — идентификатор файла в Telegram. По нему можно скачать файл.

---

### 5.1. Минимальная схема Long Polling 

Файл: `lesson.04/app/front/bot_entrypoint.py`

```python
# создаём Bot, Dispatcher
bot = Bot(token=telegram_bot_token)
dp = Dispatcher()

# подключаем router с хендлерами
dp.include_router(router)

# запускаем Long Polling — бот ждёт апдейты
await dp.start_polling(bot)
```

---

### 5.2. Команды `/start` и `/help` (Command-фильтр)

```python
@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    await message.answer("Привет! Напиши /help.")

@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer("Команды: /start, /help. Отправь текст/фото/видео.")
```

Что важно:

* `Command("start")` — фильтр “это команда /start”.
* `message.answer(...)` — отправить ответ пользователю.

---

### 5.3. Fallback на обычный текст (не команда)

Идея: **обрабатываем только текст, который не начинается с `/`**, чтобы не ломать команды.

```python
@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message) -> None:
    await message.answer("Я получил текст. Напиши /help.")
```

Что важно:

* `F.text` — “у сообщения есть текст”.
* `~F.text.startswith("/")` — “и это не команда”.

---


### 5.4. Логи вместо print 

```python
logging.basicConfig(level=logging.INFO)
logger.info("Бот запущен")
logger.info("Получили фото: %s", best_photo.file_id)
```

Правило:

* **токены и секреты не логируем**.

---


---

## 6) Как запустить и проверить


Проверка в Telegram:

1. `/start` → приветствие
2. `/help` → список возможностей
3. Написать любой текст → fallback-ответ
4. Отправить фото → “Фото получено…” + `file_id`, размер
5. Отправить видео → “Видео получено…” + метаданные + (если включено) “скачано локально”

Проверка в консоли:

* должны быть понятные логи `INFO ... Обработали /start`, `Получили фото...` и т.д.

---

## 7) Что коммитим в репозиторий (минимум)

Команды:

```bash
git status
git add .
git commit -m "Lesson 04: aiogram bot skeleton"
```

Проверяем, что НЕ попало:

* `.env` (секреты)
* `data/media/` (скачанные файлы)

---

