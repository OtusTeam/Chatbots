## 1. Виртуальное окружение: зачем и как создать

**Зачем нужно**

* Изолировать зависимости проекта от системы и других проектов.
* Чтобы разные проекты могли использовать разные версии библиотек.
* Чтобы не ломать “системный” Python.

**Создание окружения (стандартный `venv`)**

В корне проекта (например, папка `assistant_bot`):

```bash
# создание виртуального окружения
python -m venv venv
```

Активация:

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (cmd)
venv\Scripts\activate.bat

# Linux / macOS (bash/zsh)
source venv/bin/activate
```

Деактивация:

```bash
deactivate
```

Признак, что окружение активно: в начале строки терминала видно `(venv)`.

---

## 2. `pip`: основные команды

Перед командами активируй `venv`.

Установка пакетов:

```bash
# установить пакет
pip install package_name

# установить конкретную версию
pip install package_name==1.2.3
```

Просмотр установленных пакетов:

```bash
pip list
```

Информация о пакете:

```bash
pip show package_name
```

Удаление пакета:

```bash
pip uninstall package_name
```

Работа с `requirements.txt`:

```bash
# зафиксировать текущие зависимости в файл
pip freeze > requirements.txt

# установить зависимости из файла
pip install -r requirements.txt
```

---

## 3. Poetry 2.0: установка и базовые команды

**Идея:** Poetry — менеджер зависимостей и виртуальных окружений “всё в одном”.

### Установка

1 способ (через `pipx`):

```bash
# установить pipx, если ещё нет
python -m pip install --user pipx
python -m pipx ensurepath

# установить poetry
pipx install poetry
```

2 способ (через терминал):


 Linux/macOS/Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

 Windows (PowerShell):
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```


Проверка установки:

```bash
poetry --version
```

### Инициализация проекта

В корне проекта:

```bash
# создать pyproject.toml и настроить проект
poetry init
# далее отвечаем на вопросы мастера (или используем флаг --no-interaction для быстрого варианта)
```

Создание виртуального окружения и установка зависимостей:

```bash
# установить зависимости из pyproject.toml
poetry install
```

Управление пакетами:

```bash
# добавить зависимость
poetry add package_name

# добавить dev-зависимость (для разработки)
poetry add --group dev package_name

# удалить пакет
poetry remove package_name
```

Запуск команд в окружении Poetry:

```bash
# запустить python внутри окружения poetry
poetry run python main.py

# открыть shell внутри окружения poetry
poetry shell
```

---

## 4. Базовая структура проекта бота

Рекомендуемый каркас (корень: `assistant_bot`):

```text
assistant_bot/
  app/
    front/          # входные точки: Telegram, VK, web, HTTP-эндпоинты
  core/             # бизнес-логика, сценарии, правила
  infra/            # инфраструктура: БД, кеш, внешние API, очереди
  config/           # конфигурация, шаблоны .env, настройки
  tests/            # автотесты
  .env              # реальные секреты (локально, не в Git)
  .gitignore        # файлы и папки, которые игнорирует Git
  README.md         # описание проекта
  pyproject.toml    # (если используем Poetry)
  requirements.txt  # (если работаем через pip)
```

Главная мысль: **не один файл `bot.py`, а разделение по слоям**.

---

## 5. Git: основные команды

Выполняются в корне проекта (`assistant_bot`).

Инициализация репозитория:

```bash
git init
```

Проверка состояния:

```bash
git status
```

Добавление файлов в индекс:

```bash
git add filename
git add .
```

Коммит:

```bash
git commit -m "init project"
```

История коммитов:

```bash
git log
```

Работа с ветками:

```bash
# создать и перейти в новую ветку
git checkout -b feature-branch

# перейти в существующую ветку
git checkout main
# или
git switch main
```

Просмотр изменений:

```bash
git diff
```

---

## 6. GitHub: основы работы

### Создание удалённого репозитория

1. На GitHub нажимаем “New repository”.
2. Задаём имя (например, `assistant_bot`).
3. Создаём пустой репозиторий (без начального README, если локальный уже есть).

### Связка локального и удалённого репозиториев

В терминале:

```bash
# добавить remote
git remote add origin https://github.com/username/assistant_bot.git

# задать основную ветку (если нужно)
git branch -M main

# первый push
git push -u origin main
```

Дальнейшие обновления:

```bash
git add .
git commit -m "some changes"
git push
```

Клонирование чужого или своего репозитория:

```bash
git clone https://github.com/username/repo_name.git
```

---

## 7. README: создание, структура, зачем нужен

**Зачем:**

* Быстро объяснить, что это за проект и для кого.
* Подсказать, как запустить локально.
* Сделать проект понятным для преподавателя, коллег и работодателей.

**Создание**

Файл в корне проекта: `assistant_bot/README.md`.

Простейшая структура:

```markdown
# Assistant Bot

Краткое описание:
Телеграм-ассистент для [целевой аудитории], который помогает [основная задача].

## Функциональность (план)

- [ ] Основная команда /start
- [ ] Регистрация пользователя
- [ ] Запись на услугу
- [ ] Личный кабинет

## Стек

- Python 3.11+
- aiogram
- FastAPI
- SQLAlchemy
- Redis

## Как запустить локально

1. Клонировать репозиторий.
2. Создать и активировать виртуальное окружение.
3. Установить зависимости.
4. Заполнить `.env`.
5. Запустить бота / сервис.
```

Минимум: **название, для кого, что делает, как запустить**.

---

