## Занятие 5: клавиатуры и меню в aiogram


## 1) Структура проекта (куда что класть)

**Папки/файлы (минимум):**

* `/app/keyboards/`

  * `reply.py` — Reply-клавиатуры 
  * `inline.py` — Inline-клавиатуры
  * `builders.py` — функции-сборщики клавиатур

* `/app/handlers/`

  * `common.py` — команды `/start /help /menu`
  * `menu.py` — обработка **Reply-кнопок** и **callback** 
  
* /main.py` — подключение роутеров в правильном порядке

---

## 2) Reply vs Inline

### ReplyKeyboard (кнопки “снизу”)

* Отправляется как `reply_markup=...` в `message.answer(...)`
* Нажатие приходит как **обычный текст** (`message.text`)
* Хорошо для “разделов” меню

### InlineKeyboard (кнопки “внутри сообщения”)

* Тоже `reply_markup=...`, но кнопки живут в сообщении
* Нажатие приходит как **callback_query** с `callback_data`
* Для сценариев: список → выбор → ответ → назад/меню

---

## 3) Мини-шаблоны клавиатур

### Reply главное меню 

Файл: `app/keyboards/reply.py`

* `main_menu_keyboard = ReplyKeyboardMarkup(...)`
* Кнопки: `"FAQ"`, `"О нас"`, `"Связаться"`

### Inline 2 кнопки 

Файл: `app/keyboards/inline.py`

* `InlineKeyboardMarkup(inline_keyboard=[[...],[...]])`
* `InlineKeyboardButton(text="...", callback_data="action_1")`

---

## 4) Обработчики: что где ловим

### Команды (/start /help /menu)

Файл: `app/handlers/common.py`

* `@router.message(CommandStart())` → приветствие + `main_menu_keyboard`
* `@router.message(Command("help"))` → подсказка + `main_menu_keyboard`
* `@router.message(Command("menu"))` → “Главное меню” + `main_menu_keyboard`

### Reply-кнопки (меню)

Файл: `app/handlers/menu.py`

* `@router.message(F.text == "FAQ")` → “Выберите вопрос…” + inline-список вопросов
* `@router.message(F.text == "О нас")` → текст + inline (Сайт/Меню)
* `@router.message(F.text == "Связаться")` → текст + inline (Написать/Контакты/Меню)

### Callback (inline)

Файл: `app/handlers/menu.py` (или отдельный `callbacks.py`)

* `@router.callback_query()` или фильтр по `F.data`
* **обязательно**: `await callback.answer()` (иначе “крутилка”)

### Эхобот (последним)

Файл: `app/handlers/bot_message.py`

* `@router.message(F.text)` → “не понял” + `main_menu_keyboard`

---

## 5) Порядок роутеров

Файл: `main.py`

Правило:

1. `common_router` (команды)
2. `menu_router` (Reply + callback)
3. `media_router` (фото/видео)
4. `message_router` (**всегда последним**)

Иначе:

* Reply-кнопки будут улетать в эхо
* Команды могут работать нестабильно


---

## 6) Типовые ошибки и быстрые фиксы

* **Inline “крутится”** → забыли `await callback.answer()`
* **Reply-кнопки попадают в эхо/фоллбек** → неправильный порядок роутеров
* **Ничего не ловится** → фильтр `F.text == "FAQ"` не совпадает с текстом кнопки
* **Клавиатура не показывается** → не передали `reply_markup=...` в `answer()`
* **URL-кнопка не работает** → для ссылки нужен `url=...`, а не `callback_data`

---

