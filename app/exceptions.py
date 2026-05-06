# ============================================================
# ЗАДАНИЕ 10.1 — Пользовательские классы исключений
# ============================================================

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# ---------- Модели ответов об ошибках (Pydantic) ----------

class ErrorResponse(BaseModel):
    """Единый формат ответа об ошибке для всего приложения."""
    error_code: str
    message: str
    detail: str | None = None


# ---------- Пользовательские исключения ----------

class CustomExceptionA(Exception):
    """
    Исключение A — бизнес-логика не выполнена.
    Например: условие доступа не соблюдено (403 Forbidden).
    """
    status_code = 403
    error_code = "CONDITION_NOT_MET"

    def __init__(self, message: str = "Условие не выполнено", detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class CustomExceptionB(Exception):
    """
    Исключение B — ресурс не найден.
    Например: запрошенная сущность отсутствует в БД (404 Not Found).
    """
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"

    def __init__(self, message: str = "Ресурс не найден", detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


# ---------- Обработчики исключений ----------

async def custom_exception_a_handler(request: Request, exc: CustomExceptionA) -> JSONResponse:
    """Обработчик CustomExceptionA — возвращает 403 с описанием ошибки."""
    print(f"[CustomExceptionA] path={request.url.path} | {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            detail=exc.detail,
        ).model_dump(),
    )


async def custom_exception_b_handler(request: Request, exc: CustomExceptionB) -> JSONResponse:
    """Обработчик CustomExceptionB — возвращает 404 с описанием ошибки."""
    print(f"[CustomExceptionB] path={request.url.path} | {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            detail=exc.detail,
        ).model_dump(),
    )
