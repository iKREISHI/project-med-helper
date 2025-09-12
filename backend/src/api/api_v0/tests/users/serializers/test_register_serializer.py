"""
Тесты для сериализатора регистрации пользователя RegisterSerializer.

Покрываем сценарии:
- Успешная регистрация: пользователь создаётся, пароль хешируется, пароль не возвращается в data.
- Ошибки валидации: отсутствие обязательных полей (username, password, position).
- Ошибка при несуществующей должности (position).
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.users.models.position import Position
from api.api_v0.users.serializers import RegisterSerializer


User = get_user_model()


class RegisterSerializerTests(TestCase):
    """Набор тестов для проверки корректной работы RegisterSerializer."""

    def setUp(self):
        self.position = Position.objects.create(name="Врач-терапевт")

    def test_success_register_creates_user_and_hashes_password(self):
        """Сериализатор должен создать пользователя, захешировать пароль и не выводить его в ответе."""
        payload = {
            "username": "new_user",
            "password": "StrongPass123",
            "first_name": "Иван",
            "last_name": "Петров",
            "patronymic": "Сергеевич",
            "position": self.position.pk,
        }
        serializer = RegisterSerializer(data=payload)
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()
        assert isinstance(user, User)

        # Обновим из БД и проверим, что пароль захеширован
        user.refresh_from_db()
        assert user.username == payload["username"]
        assert user.check_password(payload["password"]) is True
        assert user.password != payload["password"]  # в БД хранится не в открытом виде

        # Пароля нет в сериализованном выводе
        data = serializer.data
        assert "password" not in data

    def test_missing_required_fields_errors(self):
        """Отсутствие обязательных полей должно приводить к ошибкам валидации."""
        serializer = RegisterSerializer(data={})
        assert not serializer.is_valid()
        errors = serializer.errors
        # Обязательные поля: username, password, position
        assert "username" in errors
        assert "password" in errors
        assert "position" in errors

    def test_invalid_position_id_errors(self):
        """Неверный PK должности должен приводить к ошибке валидации поля position."""
        payload = {
            "username": "user2",
            "password": "StrongPass456",
            "position": 999999,  # несуществующая должность
        }
        serializer = RegisterSerializer(data=payload)
        assert not serializer.is_valid()
        assert "position" in serializer.errors
