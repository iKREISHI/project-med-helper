"""
Тесты для LogoutViewSet (эндпоинт POST /api/v0/auth/logout/).

Проверяем сценарии:
- Успешный выход из системы для аутентифицированного пользователя: возвращается 204, а
  последующий запрос к защищённому эндпоинту /users/me/ возвращает 401/403.
- Вызов без аутентификации: также возвращается 204 (идемпотентность операции).
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.users.models import Position


class LogoutViewSetTests(APITestCase):
    """Набор тестов для эндпоинта выхода из системы."""

    def setUp(self) -> None:
        # Создаём должность, т.к. она обязательна по модели пользователя
        self.position = Position.objects.create(name="Врач")
        self.username = "logout_user"
        self.password = "StrongPass123"
        User = get_user_model()
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            first_name="Лог",
            last_name="Аут",
            patronymic="Тестовый",
            position=self.position,
        )
        self.client: APIClient
        self.url = "/api/v0/auth/logout/"
        self.me_url = "/api/v0/users/me/"

    def test_logout_success_and_protected_endpoint_denied_after(self):
        """Аутентифицированный пользователь выходит: 204, затем /users/me/ недоступен."""
        # Логинимся через серверную сессию
        self.assertTrue(self.client.login(username=self.username, password=self.password))

        # Проверяем, что до выхода доступ есть
        pre_resp = self.client.get(self.me_url)
        self.assertEqual(pre_resp.status_code, status.HTTP_200_OK)

        # Выходим
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Теперь защищённый эндпоинт должен отказать (сессия уничтожена)
        post_resp = self.client.get(self.me_url)
        self.assertIn(post_resp.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_logout_unauthenticated_is_idempotent(self):
        """Без аутентификации тоже возвращается 204 (идемпотентно)."""
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
