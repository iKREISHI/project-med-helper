"""
Тесты для RegisterViewSet (эндпоинт POST /api/v0/auth/register/).

Проверяем сценарии:
- Успешная регистрация: 201 Created, возвращаются минимальные данные пользователя (без пароля).
- Отсутствует имя пользователя: 400 и сообщение об обязательности поля username.
- Отсутствует пароль: 400 и сообщение об обязательности поля password.
- Отсутствует позиция: 400 и сообщение об обязательности поля position.
- Дублирование имени пользователя: 400 и ошибка у поля username.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.users.models import Position


class RegisterViewSetTests(APITestCase):
    """Набор тестов для эндпоинта регистрации пользователя."""

    def setUp(self) -> None:
        self.position = Position.objects.create(name="Врач")
        self.client: APIClient
        self.url = "/api/v0/auth/register/"

    def test_register_success_returns_minimal_user(self):
        """Успешная регистрация возвращает 201 и минимальные данные пользователя."""
        payload = {
            "username": "new_user",
            "password": "StrongPass123",
            "first_name": "Новый",
            "last_name": "Пользователь",
            "patronymic": "Тестовый",
            "position": self.position.pk,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        expected_keys = {"id", "username", "first_name", "last_name", "patronymic"}
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertEqual(data["username"], payload["username"])
        self.assertEqual(data["first_name"], payload["first_name"])
        self.assertEqual(data["last_name"], payload["last_name"])
        self.assertEqual(data["patronymic"], payload["patronymic"])
        self.assertNotIn("password", data)

    def test_register_missing_username(self):
        """Отсутствует username → 400 и ошибка у поля username."""
        payload = {
            "password": "StrongPass123",
            "position": self.position.pk,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("username", body)
        self.assertIn("Обязательное поле.", body["username"])

    def test_register_missing_password(self):
        """Отсутствует пароль → 400 и ошибка у поля password."""
        payload = {
            "username": "new_user2",
            "position": self.position.pk,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("password", body)
        self.assertIn("Обязательное поле.", body["password"])

    def test_register_missing_position(self):
        """Отсутствует позиция → 400 и ошибка у поля position."""
        payload = {
            "username": "new_user3",
            "password": "StrongPass123",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("position", body)
        self.assertIn("Обязательное поле.", body["position"])

    def test_register_duplicate_username(self):
        """Дублирование username → 400 и сообщение у поля username о нарушении уникальности."""
        User = get_user_model()
        User.objects.create_user(
            username="dupe",
            password="StrongPass123",
            position=self.position,
        )
        payload = {
            "username": "dupe",
            "password": "AnotherStrong123",
            "position": self.position.pk,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("username", body)
        # DRF стандартно вернёт сообщение о нарушении уникальности
        self.assertTrue(any("уже существует" in msg or "already exists" in msg for msg in body["username"]))
