"""
Тесты для сериализатора входа LoginSerializer.

Проверяем:
- Успешную аутентификацию по корректным учётным данным и возврат пользователя в validated_data.
- Ошибку при неверных учётных данных.
- Ошибки при отсутствии имени пользователя или пароля.
- Отказ для неактивного пользователя.
"""
from django.test import TestCase

from apps.users.models import User
from apps.users.models.position import Position
from api.api_v0.users.serializers import LoginSerializer


class LoginSerializerTests(TestCase):
    """Проверка корректной работы LoginSerializer."""

    def setUp(self):
        self.position = Position.objects.create(name="Регистратор")
        self.password = "VeryStrongPass123"
        self.user = User.objects.create_user(
            username="tester",
            password=self.password,
            first_name="Тест",
            last_name="Тестов",
            position=self.position,
        )

    def test_valid_credentials(self):
        """При корректных данных serializer.is_valid() True и возвращается объект пользователя."""
        serializer = LoginSerializer(data={
            'username': 'tester',
            'password': self.password,
        })
        assert serializer.is_valid(), serializer.errors
        assert 'user' in serializer.validated_data
        assert serializer.validated_data['user'].pk == self.user.pk

    def test_invalid_credentials(self):
        """Неверные данные приводят к ошибке валидации с ненавязчивым сообщением."""
        serializer = LoginSerializer(data={
            'username': 'tester',
            'password': 'wrong',
        })
        assert not serializer.is_valid()
        # Ожидаем общее сообщение об ошибке без раскрытия причины
        assert 'non_field_errors' in serializer.errors

    def test_missing_username(self):
        """Отсутствие имени пользователя вызывает соответствующую ошибку по полю username."""
        serializer = LoginSerializer(data={
            'password': self.password,
        })
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_missing_password(self):
        """Отсутствие пароля вызывает соответствующую ошибку по полю password."""
        serializer = LoginSerializer(data={
            'username': 'tester',
        })
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_inactive_user(self):
        """Неактивный пользователь не должен проходить аутентификацию."""
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        serializer = LoginSerializer(data={
            'username': 'tester',
            'password': self.password,
        })
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
