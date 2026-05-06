# ============================================================
# ЗАДАНИЕ 11.2 — Асинхронные тесты
# Используется: pytest-asyncio + httpx.AsyncClient + Faker
# ============================================================

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from faker import Faker

from app.main import app, db_memory

# Глобальный объект Faker для генерации реалистичных данных
fake = Faker("ru_RU")  # русская локаль для имён

# Указываем pytest-asyncio режим работы
pytestmark = pytest.mark.asyncio


# ---- Фикстуры ----

@pytest.fixture(autouse=True)
def isolate_db():
    """
    Изоляция состояния: очищаем словарь db_memory
    до и после каждого теста, чтобы тесты были независимы.
    """
    db_memory.clear()
    yield
    db_memory.clear()


@pytest_asyncio.fixture
async def async_client():
    """
    AsyncClient с ASGITransport — ходит в приложение напрямую,
    без запуска Uvicorn и реального HTTP-соединения.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# ---- Вспомогательная функция ----

def fake_user_payload() -> dict:
    """Генерирует валидные данные пользователя через Faker."""
    return {
        "username": fake.user_name(),
        "age": fake.random_int(min=19, max=80),  # > 18 (валидный)
    }


# ============================================================
# Тесты для POST /users — создание пользователя
# ============================================================

class TestAsyncCreateUser:
    """Тесты создания пользователя (асинхронные)."""

    async def test_create_user_201(self, async_client):
        """Валидные данные → 201 + структура ответа корректна."""
        payload = fake_user_payload()
        response = await async_client.post("/users", json=payload)

        assert response.status_code == 201
        body = response.json()
        assert "id" in body
        assert body["username"] == payload["username"]
        assert body["age"] == payload["age"]

    async def test_create_multiple_users_unique_ids(self, async_client):
        """Несколько пользователей получают уникальные ID."""
        r1 = await async_client.post("/users", json=fake_user_payload())
        r2 = await async_client.post("/users", json=fake_user_payload())
        assert r1.json()["id"] != r2.json()["id"]

    async def test_create_user_faker_name(self, async_client):
        """Имя из Faker корректно сохраняется."""
        name = fake.first_name()
        response = await async_client.post("/users", json={"username": name, "age": 25})
        assert response.status_code == 201
        assert response.json()["username"] == name


# ============================================================
# Тесты для GET /users/{user_id} — получение пользователя
# ============================================================

class TestAsyncGetUser:
    """Тесты получения пользователя (асинхронные)."""

    async def test_get_existing_user_200(self, async_client):
        """Получаем только что созданного пользователя → 200."""
        payload = fake_user_payload()
        create_resp = await async_client.post("/users", json=payload)
        user_id = create_resp.json()["id"]

        response = await async_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id
        assert response.json()["username"] == payload["username"]

    async def test_get_nonexistent_user_404(self, async_client):
        """Несуществующий ID → 404."""
        response = await async_client.get("/users/99999")
        assert response.status_code == 404

    async def test_get_user_boundary_id(self, async_client):
        """Граничный случай: ID=0 → 404 (такого не создавали)."""
        response = await async_client.get("/users/0")
        assert response.status_code == 404


# ============================================================
# Тесты для DELETE /users/{user_id} — удаление пользователя
# ============================================================

class TestAsyncDeleteUser:
    """Тесты удаления пользователя (асинхронные)."""

    async def test_delete_existing_user_204(self, async_client):
        """Удаляем существующего пользователя → 204 No Content."""
        create_resp = await async_client.post("/users", json=fake_user_payload())
        user_id = create_resp.json()["id"]

        response = await async_client.delete(f"/users/{user_id}")
        assert response.status_code == 204

    async def test_delete_twice_404(self, async_client):
        """Повторное удаление → 404."""
        create_resp = await async_client.post("/users", json=fake_user_payload())
        user_id = create_resp.json()["id"]

        await async_client.delete(f"/users/{user_id}")
        response = await async_client.delete(f"/users/{user_id}")
        assert response.status_code == 404

    async def test_get_after_delete_404(self, async_client):
        """После удаления GET по тому же ID → 404."""
        create_resp = await async_client.post("/users", json=fake_user_payload())
        user_id = create_resp.json()["id"]

        await async_client.delete(f"/users/{user_id}")
        response = await async_client.get(f"/users/{user_id}")
        assert response.status_code == 404

    async def test_delete_nonexistent_user_404(self, async_client):
        """Удаление несуществующего пользователя → 404."""
        response = await async_client.delete("/users/99999")
        assert response.status_code == 404


# ============================================================
# Тесты изоляции состояния
# ============================================================

class TestStateIsolation:
    """Проверяем, что каждый тест начинается с чистого хранилища."""

    async def test_db_is_empty_at_start(self, async_client):
        """В начале теста хранилище пустое."""
        assert len(db_memory) == 0

    async def test_db_has_one_user_after_create(self, async_client):
        """После создания одного пользователя в хранилище ровно 1 запись."""
        await async_client.post("/users", json=fake_user_payload())
        assert len(db_memory) == 1

    async def test_db_is_empty_again(self, async_client):
        """Снова проверяем изоляцию — хранилище снова пустое."""
        assert len(db_memory) == 0
