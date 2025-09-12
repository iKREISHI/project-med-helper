"""
Тесты для UsersViewSet (эндпоинт GET /api/v0/users/me/minimal/).

Проверяем сценарии:
- Без аутентификации возвращается 401 Unauthorized или 403 Forbidden (в зависимости от настроек).
- При аутентификации возвращаются минимальные данные текущего пользователя по MinimalUserSerializer.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.users.models import Position


class UsersMinimalViewSetTests(APITestCase):
    """Набор тестов для эндпоинта текущего пользователя /users/me/minimal/."""

    def setUp(self) -> None:
        # Создаём должность, т.к. она обязательна по модели пользователя
        self.position = Position.objects.create(name="Врач")
        self.username = "sidorov"
        self.password = "StrongPass123"
        User = get_user_model()
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="Сидор",
            last_name="Сидоров",
            patronymic="Сидорович",
            position=self.position,
        )
        self.client: APIClient
        self.url = "/api/v0/users/me/minimal/"

    def test_me_minimal_requires_authentication(self):
        """Запрос без аутентификации должен вернуть 401 или 403."""
        response = self.client.get(self.url)
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_me_minimal_returns_minimal_user_data(self):
        """Аутентифицированный пользователь получает минимальные данные."""
        # Логинимся через серверную сессию
        self.assertTrue(self.client.login(username=self.username, password=self.password))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        expected_fields = {"id", "username", "first_name", "last_name", "patronymic"}
        self.assertEqual(set(data.keys()), expected_fields)

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], self.username)
        self.assertEqual(data["first_name"], "Сидор")
        self.assertEqual(data["last_name"], "Сидоров")
        self.assertEqual(data["patronymic"], "Сидорович")
