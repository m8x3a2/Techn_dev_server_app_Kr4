# Контрольная работа №4 — FastAPI

Технологии разработки серверных приложений  


---

## Структура проекта

```
kr4/
├── app/
│   ├── __init__.py
│   ├── main.py          # Главное приложение (все задания)
│   ├── models.py        # SQLAlchemy-модели (Задание 9.1)
│   ├── schemas.py       # Pydantic-схемы (Задание 10.2)
│   ├── database.py      # Подключение к БД
│   └── exceptions.py    # Кастомные исключения (Задание 10.1)
├── alembic_migrations/
│   ├── env.py           # Настройки Alembic
│   ├── script.py.mako   # Шаблон миграций
│   └── versions/
│       ├── 0001_create_products.py   # Создание таблицы products
│       └── 0002_add_description.py   # Добавление поля description
├── tests/
│   ├── test_sync.py     # Задание 11.1 — синхронные тесты
│   └── test_async.py    # Задание 11.2 — асинхронные тесты (httpx + Faker)
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Быстрый старт в PyCharm

### 1. Создать виртуальное окружение

В PyCharm: `File venv
Или в терминале (внутри папки проекта):

```bash
python -m venv .venv
```

Активировать (Windows):
```bash
.venv\Scripts\activate
```

Активировать (macOS/Linux):
```bash
source .venv/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Настроить переменные окружения (опционально)

```bash
cp .env.example .env
```

По умолчанию используется SQLite — ничего настраивать не нужно.

### 4. Применить миграции Alembic (Задание 9.1)

```bash
# Применить все миграции (создаст файл kr4.db и таблицу products)
alembic upgrade head
```

Что произойдёт:
- Создастся файл `kr4.db`
- Создастся таблица `products` с полями `id, title, price, count`
- Добавятся 2 тестовые записи (Ноутбук и Смартфон)
- Добавится поле `description` (NOT NULL)

### 5. Запустить приложение

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: **http://127.0.0.1:8000**

---

## Проверка функциональности

### Swagger UI (интерактивная документация)

Откройте в браузере: **http://127.0.0.1:8000/docs**

Там можно протестировать все эндпоинты прямо из браузера.

### Проверка вручную (curl / браузер)

#### Задание 9.1 — Товары (Alembic + SQLAlchemy)

```bash
# Список всех товаров (должно вернуть 2 записи из миграции)
curl http://127.0.0.1:8000/products

# Создать новый товар
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{"title": "Планшет", "price": 25000, "count": 5, "description": "Отличный планшет"}'
```

#### Задание 10.1 — Кастомные исключения

```bash
# 403 — уровень доступа недостаточен
curl http://127.0.0.1:8000/check-access/3

# 200 — доступ разрешён
curl http://127.0.0.1:8000/check-access/10

# 404 — элемент не найден
curl http://127.0.0.1:8000/items/999

# 200 — элемент найден
curl http://127.0.0.1:8000/items/1
```

#### Задание 10.2 — Валидация пользователя

```bash
# 201 — успешная регистрация
curl -X POST http://127.0.0.1:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan", "age": 25, "email": "ivan@example.com", "password": "mypassword"}'

# 422 — возраст не больше 18
curl -X POST http://127.0.0.1:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "junior", "age": 16, "email": "a@b.com", "password": "mypassword"}'

# 422 — некорректный email
curl -X POST http://127.0.0.1:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "bad", "age": 20, "email": "not-email", "password": "mypassword"}'
```

#### Задание 11.2 — In-memory CRUD пользователей

```bash
# Создать пользователя
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "age": 30}'

# Получить пользователя (замените 1 на реальный ID)
curl http://127.0.0.1:8000/users/1

# Удалить пользователя
curl -X DELETE http://127.0.0.1:8000/users/1
```

---

## Запуск тестов

### Все тесты (синхронные + асинхронные)

```bash
pytest
```

### Только синхронные тесты (Задание 11.1)

```bash
pytest tests/test_sync.py -v
```

### Только асинхронные тесты (Задание 11.2)

```bash
pytest tests/test_async.py -v
```

### С подробным выводом и отображением print()

```bash
pytest -v -s
```

### Ожидаемый результат

```
tests/test_sync.py::TestCustomExceptions::test_check_access_denied      PASSED
tests/test_sync.py::TestCustomExceptions::test_check_access_allowed      PASSED
tests/test_sync.py::TestCustomExceptions::test_get_item_not_found        PASSED
tests/test_sync.py::TestCustomExceptions::test_get_item_found            PASSED
tests/test_sync.py::TestUserValidation::test_register_valid_user         PASSED
...
tests/test_async.py::TestAsyncCreateUser::test_create_user_201           PASSED
tests/test_async.py::TestAsyncGetUser::test_get_existing_user_200        PASSED
tests/test_async.py::TestAsyncDeleteUser::test_delete_existing_user_204  PASSED
...
========================= X passed in X.Xs =========================
```

---

## Работа с миграциями Alembic (Задание 9.1)

```bash
# Применить все миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Откатить все миграции
alembic downgrade base

# Посмотреть историю миграций
alembic history

# Посмотреть текущую версию БД
alembic current
```

---

## Описание заданий

| Задание | Файл | Что реализовано |
|---------|------|-----------------|
| 9.1 | `app/models.py`, `alembic_migrations/` | Модель `Product`, 2 миграции Alembic |
| 10.1 | `app/exceptions.py`, `app/main.py` | `CustomExceptionA` (403), `CustomExceptionB` (404), обработчики |
| 10.2 | `app/schemas.py`, `app/main.py` | Валидация `UserCreate` через Pydantic, кастомный `@exception_handler` |
| 11.1 | `tests/test_sync.py` | Синхронные pytest-тесты через `TestClient` |
| 11.2 | `tests/test_async.py` | Асинхронные тесты: `pytest-asyncio` + `httpx.AsyncClient` + `Faker` |

---


- Python 3.14

