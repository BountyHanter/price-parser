# FastAPI FastStart Template

Этот проект представляет собой готовый шаблон для быстрого старта разработки на FastAPI с интегрированной базой данных PostgreSQL, системой миграций Alembic и контейнеризацией через Docker.

## Стек технологий (Обновляйте при необходимости)
- **Python 3.10+**
- **FastAPI** — высокопроизводительный веб-фреймворк.
- **PostgreSQL** — надежная реляционная СУБД.
- **SQLAlchemy 2.0** — асинхронная ORM.
- **Alembic** — инструмент для управления миграциями БД.
- **Pydantic V2** — валидация данных и настройки.
- **Docker & Docker Compose** — контейнеризация.

---

## Важное дополнение
Если вам нужен продвинутый логгер для FastAPI, рекомендую использовать:
👉 [fast-api-logger](https://github.com/BountyHanter/fast-api-logger)

---

## Быстрый старт

### 1. Настройка окружения
Создайте файл `.env` в корневом каталоге на основе `.env.example`:
```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
POSTGRES_PORT=6000
POSTGRES_HOST=localhost
```

### 2. Запуск базы данных через Docker
Если у вас нет локальной базы, запустите её из Docker:
```bash
docker-compose up -d
```

### 3. Установка зависимостей
Рекомендуется использовать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
# или
venv\Scripts\activate     # Для Windows

pip install -r requirements.txt
```

### 4. Миграции
Примените существующие миграции к базе данных:
```bash
alembic upgrade head
```

### 5. Запуск приложения
```bash
uvicorn app.main:app --reload
```
Приложение будет доступно по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)
Документация Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Структура проекта
- `app/main.py` — точка входа в приложение и регистрация роутов.
- `app/models/` — SQLAlchemy модели (описание таблиц БД).
- `app/schemas.py` — Pydantic схемы (валидация входных/выходных данных).
- `app/database.py` — конфигурация подключения к БД и создание сессий.
- `app/config.py` — управление настройками через Pydantic Settings.
- `app/migration/` — файлы и история миграций Alembic.

---

## Инструкция по расширению

### Добавление новой модели (таблицы в БД)
1. Создайте файл в `app/models/`, например `item.py`.
2. Опишите класс модели, наследуясь от `Base` из `app.database`.
3. Импортируйте новую модель в `app/models/__init__.py` (чтобы Alembic увидел её).
4. Создайте миграцию:
   ```bash
   alembic revision --autogenerate -m "Add items table"
   ```
5. Примените её:
   ```bash
   alembic upgrade head
   ```

### Добавление новых эндпоинтов (API)
1. Создайте роутер (например, `app/routers/items.py` — если планируете много эндпоинтов).
2. Подключите роутер в `app/main.py`:
   ```python
   app.include_router(your_router)
   ```

### Работа со схемами
Для каждого эндпоинта описывайте входные и выходные данные в `app/schemas.py`, используя `Pydantic`. Это обеспечит автоматическую валидацию и генерацию документации Swagger.
