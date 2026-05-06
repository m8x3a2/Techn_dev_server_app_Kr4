# ============================================================
# ЗАДАНИЕ 10.2 — Pydantic-схемы с валидацией данных
# ============================================================

from typing import Optional
from pydantic import BaseModel, EmailStr, conint, constr


# ---------- Схемы пользователя (Задание 10.2) ----------

class UserCreate(BaseModel):
    """
    Модель входящих данных пользователя с валидацией.
    Используется в эндпоинте POST /users/register.
    """
    username: str
    age: conint(gt=18)           # целое число, строго больше 18
    email: EmailStr              # строка в формате email
    password: constr(min_length=8, max_length=16)  # от 8 до 16 символов
    phone: Optional[str] = "Unknown"               # необязательное поле


class UserOut(BaseModel):
    """Модель ответа — не возвращает пароль."""
    id: int
    username: str
    age: int
    email: str
    phone: str


# ---------- Схемы товара (Задание 9.1) ----------

class ProductCreate(BaseModel):
    title: str
    price: float
    count: int
    description: str = ""


class ProductOut(BaseModel):
    id: int
    title: str
    price: float
    count: int
    description: str

    model_config = {"from_attributes": True}
