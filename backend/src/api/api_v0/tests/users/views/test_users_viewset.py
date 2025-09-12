"""
Тесты для UsersViewSet (эндпоинт GET /api/v0/users/me/).

Проверяем сценарии:
- Без аутентификации возвращается 401 Unauthorized.
- При аутентификации возвращаются подробные данные текущего пользователя по UserSerializer.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.users.models import Position
from api.api_v0.users.serializers.user import UserSerializer


class UsersViewSetTests(APITestCase):
    """Набор тестов для эндпоинта текущего пользователя /users/me/."""

    def setUp(self) -> None:
        # Создаём должность, т.к. она обязательна по модели пользователя
        self.position = Position.objects.create(name="Врач")
        self.username = "petrov"
        self.password = "StrongPass123"
        User = get_user_model()
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="Пётр",
            last_name="Петров",
            patronymic="Петрович",
            position=self.position,
        )
        self.client: APIClient
        self.url = "/api/v0/users/me/"

    def test_me_requires_authentication(self):
        """Запрос без аутентификации должен вернуть 401 Unauthorized (или 403, в зависимости от настроек)."""
        response = self.client.get(self.url)
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_me_returns_current_user_full_data(self):
        """Аутентифицированный пользователь получает свои полные данные по UserSerializer."""
        # Аутентифицируемся через серверную сессию
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in, msg="Не удалось залогиниться тестовым клиентом")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        # Ожидаемый набор полей совпадает с Meta.fields из UserSerializer
        expected_fields = set(UserSerializer.Meta.fields)
        self.assertEqual(set(data.keys()), expected_fields)

        # Базовые значения
        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], self.username)
        self.assertEqual(data["first_name"], "Пётр")
        self.assertEqual(data["last_name"], "Петров")
        self.assertEqual(data["patronymic"], "Петрович")

        # Поля, связанные с должностью
        self.assertEqual(data["position"], self.position.pk)
        self.assertEqual(data["position_id"], self.position.pk)
        self.assertEqual(data["position_name"], self.position.name)

        # Поле аватара по умолчанию отсутствует (None)
        self.assertIsNone(data["avatar"])