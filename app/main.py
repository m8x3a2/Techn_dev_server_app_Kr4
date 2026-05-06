# ============================================================
# Главный файл приложения FastAPI
# Объединяет задания 9.1, 10.1, 10.2, 11.1, 11.2
# ============================================================

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models import Base, Product
from app.schemas import ProductCreate, ProductOut, UserCreate, UserOut
from app.exceptions import (
    CustomExceptionA,
    CustomExceptionB,
    ErrorResponse,
    custom_exception_a_handler,
    custom_exception_b_handler,
)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """
    При старте приложения создаём таблицы если их нет.
    В production таблицы создаются через alembic upgrade head.
    Это — страховка, чтобы /products не падал с 500 без миграций.
    """
    Base.metadata.create_all(bind=engine)
    yield


# ---- Инициализация приложения ----
app = FastAPI(
    title="Контрольная работа №4",
    description="FastAPI: Alembic, кастомные исключения, валидация, тесты",
    version="1.0.0",
    lifespan=lifespan,
)

# ---- Регистрация обработчиков исключений (Задание 10.1) ----
app.add_exception_handler(CustomExceptionA, custom_exception_a_handler)
app.add_exception_handler(CustomExceptionB, custom_exception_b_handler)


# ============================================================
# ЗАДАНИЕ 10.2 — Обработчик ошибок валидации Pydantic
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Перехватывает ошибки валидации Pydantic и возвращает
    понятное сообщение вместо стандартного ответа FastAPI.
    """
    errors = exc.errors()
    print(f"[ValidationError] path={request.url.path} | errors={errors}")
    # Собираем читаемые сообщения об ошибках
    messages = []
    for err in errors:
        field = " -> ".join(str(loc) for loc in err["loc"])
        messages.append(f"{field}: {err['msg']}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Ошибка валидации данных",
            detail="; ".join(messages),
        ).model_dump(),
    )


# ============================================================
# ЗАДАНИЕ 10.1 — Эндпоинты, вызывающие кастомные исключения
# ============================================================

@app.get(
    "/check-access/{level}",
    summary="Задание 10.1 — проверка уровня доступа",
    tags=["Задание 10.1"],
)
async def check_access(level: int):
    """
    Возвращает 403 CustomExceptionA, если уровень доступа < 5.
    Иначе возвращает подтверждение.
    """
    if level < 5:
        raise CustomExceptionA(
            message="Недостаточный уровень доступа",
            detail=f"Требуется уровень >= 5, передан {level}",
        )
    return {"status": "ok", "level": level, "message": "Доступ разрешён"}


@app.get(
    "/items/{item_id}",
    summary="Задание 10.1 — получение элемента по ID",
    tags=["Задание 10.1"],
)
async def get_item(item_id: int):
    """
    Симулирует поиск ресурса. Если ID > 100 — ресурс «не найден» (404).
    """
    fake_db = {1: "Телефон", 2: "Ноутбук", 3: "Планшет"}
    if item_id not in fake_db:
        raise CustomExceptionB(
            message="Элемент не найден",
            detail=f"Элемент с ID={item_id} отсутствует в базе",
        )
    return {"id": item_id, "name": fake_db[item_id]}


# ============================================================
# ЗАДАНИЕ 10.2 — Эндпоинт с валидацией пользователя
# ============================================================

@app.post(
    "/users/register",
    response_model=UserOut,
    status_code=201,
    summary="Задание 10.2 — регистрация пользователя с валидацией",
    tags=["Задание 10.2"],
)
async def register_user(user: UserCreate):
    """
    Принимает данные пользователя. Pydantic автоматически валидирует:
    - age > 18
    - email в правильном формате
    - password длиной 8–16 символов
    """
    # В реальном приложении здесь было бы сохранение в БД
    return UserOut(
        id=1,
        username=user.username,
        age=user.age,
        email=user.email,
        phone=user.phone or "Unknown",
    )


# ============================================================
# ЗАДАНИЕ 9.1 — CRUD для Product (через Alembic-миграции)
# ============================================================

@app.get(
    "/products",
    response_model=list[ProductOut],
    summary="Задание 9.1 — список всех товаров",
    tags=["Задание 9.1"],
)
def list_products(db: Session = Depends(get_db)):
    """Возвращает все товары из таблицы products."""
    return db.query(Product).all()


@app.post(
    "/products",
    response_model=ProductOut,
    status_code=201,
    summary="Задание 9.1 — создание товара",
    tags=["Задание 9.1"],
)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Создаёт новый товар в базе данных."""
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# ============================================================
# ЗАДАНИЕ 11.1 / 11.2 — In-memory CRUD для пользователей
# (используется в юнит-тестах)
# ============================================================

from itertools import count as _count
from threading import Lock as _Lock

_id_seq = _count(start=1)
_id_lock = _Lock()
# Глобальное хранилище в памяти (словарь id -> данные пользователя)
db_memory: dict[int, dict] = {}


def _next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)


from pydantic import BaseModel as _BM


class _UserIn(_BM):
    username: str
    age: int


class _UserOut(_BM):
    id: int
    username: str
    age: int


@app.post(
    "/users",
    response_model=_UserOut,
    status_code=201,
    summary="Задание 11.2 — создание пользователя (in-memory)",
    tags=["Задание 11.1 / 11.2"],
)
def create_user(user: _UserIn):
    """Создаёт пользователя в in-memory хранилище."""
    user_id = _next_user_id()
    db_memory[user_id] = user.model_dump()
    return {"id": user_id, **db_memory[user_id]}


@app.get(
    "/users/{user_id}",
    response_model=_UserOut,
    summary="Задание 11.2 — получение пользователя по ID",
    tags=["Задание 11.1 / 11.2"],
)
def get_user(user_id: int):
    """Возвращает пользователя по ID или 404."""
    if user_id not in db_memory:
        raise CustomExceptionB(message="Пользователь не найден", detail=f"ID={user_id}")
    return {"id": user_id, **db_memory[user_id]}


@app.delete(
    "/users/{user_id}",
    status_code=204,
    summary="Задание 11.2 — удаление пользователя",
    tags=["Задание 11.1 / 11.2"],
)
def delete_user(user_id: int):
    """Удаляет пользователя по ID или возвращает 404."""
    if db_memory.pop(user_id, None) is None:
        raise CustomExceptionB(message="Пользователь не найден", detail=f"ID={user_id}")
    from fastapi import Response
    return Response(status_code=204)
