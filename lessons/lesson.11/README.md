## Установка alembic
pip install alembic  
  
## Посмотреть версию
alembic --version

## Инициализировать alembic в проекте в директорию alembic
alembic init alembic

## Текущая версия
alembic current

## Создаем первую ревизию\миграцию с сообщением "init"
alembic revision --autogenerate -m "init"

## История миграций
alembic history

## Расширенная история миграций
alembic history --verbose

## Применить последнюю миграцию 
alembic upgrade head

## Применить миграцию cb703f640bd3
alembic upgrade cb703f640bd3

## Откатиться на 1 шаг назад
alembic downgrade -1

## Откатиться к миграции cb703f640bd3
alembic downgrade cb703f640bd3

## Откатиться к базовому состоянию
alembic downgrade base
