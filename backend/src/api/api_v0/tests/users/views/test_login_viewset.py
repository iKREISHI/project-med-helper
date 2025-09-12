"""
Тесты для LoginViewSet (эндпоинт POST /api/v0/auth/login/).

Проверяем сценарии:
- Успешный логин: создаётся серверная сессия и возвращаются минимальные данные пользователя.
- Неверные учётные данные: 400 и сообщение об ошибке в non_field_errors.
- Отсутствует имя пользователя: 400 и сообщение об ошибке в поле username.
- Отсутствует пароль: 400 и сообщение об ошибке в поле password.
- Неактивный пользователь: 400 и сообщение об ошибке в non_field_errors.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.users.models import Position


class LoginViewSetTests(APITestCase):
    """Набор тестов для эндпоинта логина."""

    def setUp(self) -> None:
        # Создаём должность, т.к. она обязательна по модели пользователя
        self.position = Position.objects.create(name="Врач")
        self.username = "ivan"
        self.password = "Passw0rd123"
        User = get_user_model()
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="Иван",
            last_name="Иванов",
            patronymic="Иванович",
            position=self.position,
        )
        self.client: APIClient
        self.url = "/api/v0/auth/login/"

    def test_login_success_creates_session_and_returns_minimal_user(self):
        """Успешный логин: 200 OK, есть cookie сессии, данные пользователя минимальные."""
        response = self.client.post(
            self.url,
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что создана сессия: обычно устанавливается cookie 'sessionid'
        self.assertIn("sessionid", response.cookies, msg="Ожидался cookie sessionid после логина")

        # Проверяем минимальные поля пользователя
        data = response.json()
        expected_keys = {"id", "username", "first_name", "last_name", "patronymic"}
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertEqual(data["username"], self.username)
        self.assertEqual(data["first_name"], "Иван")
        self.assertEqual(data["last_name"], "Иванов")
        self.assertEqual(data["patronymic"], "Иванович")

    def test_login_invalid_credentials(self):
        """Неверные учётные данные → 400 и non_field_errors с сообщением об ошибке."""
        response = self.client.post(
            self.url,
            {"username": self.username, "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        # Сообщение определено в LoginSerializer.default_error_messages['invalid_credentials']
        self.assertIn("non_field_errors", body)
        self.assertIsInstance(body["non_field_errors"], list)
        self.assertTrue(any("Неверное имя пользователя" in msg for msg in body["non_field_errors"]))

    def test_login_missing_username(self):
        """Отсутствует username → 400 и ошибка у поля username."""
        response = self.client.post(
            self.url,
            {"password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("username", body)
        # DRF по умолчанию вернёт стандартное сообщение об обязательности поля
        self.assertIn("Обязательное поле.", body["username"])

    def test_login_missing_password(self):
        """Отсутствует пароль → 400 и ошибка у поля password."""
        response = self.client.post(
            self.url,
            {"username": self.username},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("password", body)
        # DRF по умолчанию вернёт стандартное сообщение об обязательности поля
        self.assertIn("Обязательное поле.", body["password"])

    def test_login_inactive_user(self):
        """Пользователь неактивен → 400 и общее сообщение об ошибке (как при неверных данных).

        Примечание: стандартный бэкенд аутентификации Django не аутентифицирует неактивных
        пользователей и возвращает None, поэтому сообщение такое же, как при неверных данных,
        чтобы не раскрывать статус учётной записи.
        """
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            self.url,
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIn("non_field_errors", body)
        self.assertTrue(any("Неверное имя пользователя" in msg for msg in body["non_field_errors"]))
