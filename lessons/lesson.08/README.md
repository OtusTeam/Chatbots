## Создаём/меняем структуру таблиц

### CREATE TABLE — создать таблицу

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tg_user_id INTEGER NOT NULL UNIQUE,
  username TEXT
);
```

### DROP TABLE — удалить таблицу

```sql
DROP TABLE IF EXISTS users;
```

### ALTER TABLE — изменить таблицу

```sql
-- добавить новое поле
ALTER TABLE users ADD COLUMN first_name TEXT;

-- переименовать таблицу
ALTER TABLE users RENAME TO bot_users;

-- переименовать колонку (если SQLite поддерживает вашу версию)
ALTER TABLE bot_users RENAME COLUMN username TO tg_username;
```

### CREATE INDEX — ускорить выборки

```sql
CREATE INDEX idx_messages_user_created_at
ON messages(user_id, created_at);
```

### DROP INDEX — удалить индекс

```sql
DROP INDEX IF EXISTS idx_messages_user_created_at;
```

---

## Вставка/обновление/удаление данных (CRUD)

### INSERT — добавить запись

```sql
INSERT INTO users (tg_user_id, username)
VALUES (1001, 'alex_dev');
```

### INSERT…SELECT — вставка с подзапросом

```sql
INSERT INTO messages (user_id, chat_id, direction, text, created_at)
VALUES (
  (SELECT id FROM users WHERE tg_user_id=1001),
  (SELECT id FROM chats WHERE tg_chat_id=2001),
  'inbound',
  'Привет! Хочу узнать статус.',
  '2025-12-26 10:00:00'
);
```

### UPDATE — изменить запись

```sql
UPDATE users
SET username = 'alex_new'
WHERE tg_user_id = 1001;
```

### DELETE — удалить запись

```sql
DELETE FROM messages
WHERE id = 10;
```

---

## SELECT: выборка данных (самое частое в боте)

### SELECT + WHERE — фильтрация

```sql
SELECT id, text, created_at
FROM messages
WHERE user_id = 1;
```

### ORDER BY + LIMIT — “последние N”

```sql
SELECT text, created_at
FROM messages
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 10;
```

### DISTINCT — уникальные значения

```sql
SELECT DISTINCT direction
FROM messages;
```

### LIKE — поиск по подстроке

```sql
SELECT text, created_at
FROM messages
WHERE text LIKE '%оплата%'
ORDER BY created_at DESC
LIMIT 20;
```

### IN — “одно из”

```sql
SELECT text
FROM messages
WHERE direction IN ('inbound', 'outbound');
```

### BETWEEN — диапазон (по датам/числам)

```sql
SELECT text, created_at
FROM messages
WHERE created_at BETWEEN '2025-12-24 00:00:00' AND '2025-12-26 23:59:59';
```

---

## JOIN: склеиваем таблицы (история “красиво”)

### INNER JOIN — только совпавшие связи

```sql
SELECT
  u.tg_user_id,
  u.username,
  c.tg_chat_id,
  m.direction,
  m.text,
  m.created_at
FROM messages m
JOIN users u ON u.id = m.user_id
JOIN chats c ON c.id = m.chat_id
ORDER BY m.created_at DESC
LIMIT 20;
```

---

## GROUP BY: аналитика и “топы”

### COUNT + GROUP BY — считаем по дням

```sql
SELECT
  date(created_at) AS day,
  COUNT(*) AS inbound_count
FROM messages
WHERE direction = 'inbound'
GROUP BY date(created_at)
ORDER BY day DESC;
```

### GROUP BY + ORDER BY + LIMIT — топ пользователей

```sql
SELECT
  u.tg_user_id,
  u.username,
  COUNT(*) AS inbound_count
FROM messages m
JOIN users u ON u.id = m.user_id
WHERE m.direction = 'inbound'
GROUP BY u.tg_user_id, u.username
ORDER BY inbound_count DESC
LIMIT 5;
```

### HAVING — фильтр после группировки

```sql
SELECT
  u.tg_user_id,
  COUNT(*) AS inbound_count
FROM messages m
JOIN users u ON u.id = m.user_id
WHERE m.direction = 'inbound'
GROUP BY u.tg_user_id
HAVING COUNT(*) > 1
ORDER BY inbound_count DESC;
```

---

## Транзакции: “либо всё, либо ничего”

```sql
BEGIN;

INSERT INTO users (tg_user_id, username) VALUES (2001, 'test_user');
INSERT INTO chats (tg_chat_id, chat_type) VALUES (9001, 'private');

COMMIT;

-- если что-то пошло не так
-- ROLLBACK;
```

---


