# ============================================================
# ЗАДАНИЕ 11.1 — Модульные тесты для эндпоинтов FastAPI
# Используется: pytest + TestClient (синхронные тесты)
# ============================================================

import pytest
from fastapi.testclient import TestClient

from app.main import app, db_memory


# ---- Фикстура: чистый клиент с очищенным хранилищем ----

@pytest.fixture(autouse=True)
def clear_db():
    """
    Автоматически очищает in-memory хранилище перед каждым тестом,
    чтобы тесты не влияли друг на друга (изоляция состояния).
    """
    db_memory.clear()
    yield
    db_memory.clear()


@pytest.fixture
def client():
    """Создаёт TestClient для приложения FastAPI."""
    return TestClient(app)


# ============================================================
# Тесты для кастомных исключений (Задание 10.1)
# ============================================================

class TestCustomExceptions:
    """Тесты для эндпоинтов с CustomExceptionA и CustomExceptionB."""

    def test_check_access_denied(self, client):
        """Уровень доступа < 5 → 403 + корректное тело ошибки."""
        response = client.get("/check-access/3")
        assert response.status_code == 403
        body = response.json()
        assert body["error_code"] == "CONDITION_NOT_MET"
        assert "message" in body

    def test_check_access_allowed(self, client):
        """Уровень доступа >= 5 → 200 OK."""
        response = client.get("/check-access/10")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_get_item_not_found(self, client):
        """Несуществующий item_id → 404 + корректное тело ошибки."""
        response = client.get("/items/999")
        assert response.status_code == 404
        body = response.json()
        assert body["error_code"] == "RESOURCE_NOT_FOUND"

    def test_get_item_found(self, client):
        """Существующий item_id → 200 + данные элемента."""
        response = client.get("/items/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Телефон"


# ============================================================
# Тесты для валидации данных (Задание 10.2)
# ============================================================

class TestUserValidation:
    """Тесты валидации эндпоинта POST /users/register."""

    def test_register_valid_user(self, client):
        """Корректные данные → 201 + данные пользователя."""
        payload = {
            "username": "testuser",
            "age": 25,
            "email": "test@example.com",
            "password": "securepass",
        }
        response = client.post("/users/register", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["username"] == "testuser"
        assert "password" not in body  # пароль не возвращается

    def test_register_underage_user(self, client):
        """Возраст <= 18 → 422 ошибка валидации."""
        payload = {
            "username": "young",
            "age": 17,
            "email": "young@example.com",
            "password": "securepass",
        }
        response = client.post("/users/register", json=payload)
        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

    def test_register_invalid_email(self, client):
        """Неверный email → 422 ошибка валидации."""
        payload = {
            "username": "user2",
            "age": 20,
            "email": "not-an-email",
            "password": "securepass",
        }
        response = client.post("/users/register", json=payload)
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Пароль короче 8 символов → 422."""
        payload = {
            "username": "user3",
            "age": 22,
            "email": "user3@example.com",
            "password": "123",
        }
        response = client.post("/users/register", json=payload)
        assert response.status_code == 422

    def test_register_long_password(self, client):
        """Пароль длиннее 16 символов → 422."""
        payload = {
            "username": "user4",
            "age": 22,
            "email": "user4@example.com",
            "password": "a" * 17,
        }
        response = client.post("/users/register", json=payload)
        assert response.status_code == 422

    def test_register_optional_phone_default(self, client):
        """Не передаём phone → в ответе 'Unknown'."""
        payload = {
            "username": "nophone",
            "age": 30,
            "email": "nophone@example.com",
            "password": "validpassword",
        }
        response = client.post("/users/register", json=payload)
        assert response.status_code == 201
        assert response.json()["phone"] == "Unknown"


# ============================================================
# Тесты для in-memory CRUD (Задания 11.1 / 11.2)
# ============================================================

class TestInMemoryUsers:
    """Тесты CRUD /users (in-memory хранилище)."""

    def test_create_user_success(self, client):
        """POST /users → 201 + корректная структура ответа."""
        response = client.post("/users", json={"username": "alice", "age": 30})
        assert response.status_code == 201
        body = response.json()
        assert "id" in body
        assert body["username"] == "alice"
        assert body["age"] == 30

    def test_get_existing_user(self, client):
        """Создаём пользователя и получаем его → 200."""
        create_resp = client.post("/users", json={"username": "bob", "age": 25})
        user_id = create_resp.json()["id"]

        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "bob"

    def test_get_nonexistent_user(self, client):
        """GET /users/9999 (не существует) → 404."""
        response = client.get("/users/9999")
        assert response.status_code == 404

    def test_delete_existing_user(self, client):
        """Создаём и удаляем пользователя → 204."""
        create_resp = client.post("/users", json={"username": "carol", "age": 28})
        user_id = create_resp.json()["id"]

        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204

    def test_delete_already_deleted_user(self, client):
        """Повторное удаление → 404."""
        create_resp = client.post("/users", json={"username": "dave", "age": 35})
        user_id = create_resp.json()["id"]

        client.delete(f"/users/{user_id}")
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 404

    def test_get_user_after_delete(self, client):
        """После удаления пользователь недоступен → 404."""
        create_resp = client.post("/users", json={"username": "eve", "age": 21})
        user_id = create_resp.json()["id"]

        client.delete(f"/users/{user_id}")
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 404
