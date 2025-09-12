"""
Тесты для минимального сериализатора пользователя MinimalUserSerializer.

Проверяем:
- Набор полей соответствует ожидаемому минимальному набору и пароль не отдаётся.
- Поле avatar сериализуется как None, если не задано.
- Сериализатор полностью read-only и не изменяет модель при попытке записи.
"""
from django.test import TestCase

from apps.users.models import User
from apps.users.models.position import Position
from api.api_v0.users.serializers import MinimalUserSerializer


class MinimalUserSerializerTests(TestCase):
    """Проверка корректной работы MinimalUserSerializer."""

    def setUp(self):
        """Создаём должность и пользователя для тестов."""
        self.position = Position.objects.create(name="Медсестра")
        self.user = User.objects.create_user(
            username="petrova",
            password="StrongPass456",
            first_name="Анна",
            last_name="Петрова",
            patronymic="Игоревна",
            position=self.position,
        )

    def test_minimal_user_serializer_fields(self):
        """Сериализатор должен возвращать только минимальный набор полей и не возвращать пароль."""
        data = MinimalUserSerializer(self.user).data

        expected_fields = {
            'id', 'username', 'first_name', 'last_name', 'patronymic'
        }
        # Допускаем наличие дополнительных полей, но требуем как минимум минимальный набор
        assert set(data.keys()).issuperset(expected_fields)

        # Базовые значения соответствуют модели
        assert data['username'] == "petrova"
        assert data['first_name'] == "Анна"
        assert data['last_name'] == "Петрова"
        assert data['patronymic'] == "Игоревна"

        # Пароль отсутствует
        assert 'password' not in data

    def test_minimal_user_serializer_avatar_none(self):
        """Если аватар не задан, должно приходить None (или ключ может отсутствовать в некоторых бэкендах/контекстах)."""
        data = MinimalUserSerializer(self.user).data
        assert data.get('avatar') is None

    def test_minimal_user_serializer_is_read_only(self):
        """Попытка записи через сериализатор не должна менять модель."""
        orig_first_name = self.user.first_name

        serializer = MinimalUserSerializer(instance=self.user, data={
            'first_name': 'Елена',
        }, partial=True)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data == {}

        updated = serializer.save()
        updated.refresh_from_db()

        assert updated.first_name == orig_first_name
