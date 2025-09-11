"""
Тесты для сериализатора пользователя UserSerializer.

Цели:
- Проверить, что сериализатор отдаёт ровно ожидаемый набор полей и не отдаёт пароль.
- Проверить вычисляемые поля position_id и position_name.
- Проверить сериализацию пустого аватара.
- Проверить read-only поведение при попытке записи через сериализатор.
"""
from django.test import TestCase

from apps.users.models import User
from apps.users.models.position import Position
from api.api_v0.users.serializers.user import UserSerializer


class UserSerializerTests(TestCase):
    """Набор тестов для проверки корректной работы UserSerializer."""

    def setUp(self):
        """Готовим общие объекты для тестов: должность и пользователя."""
        self.position = Position.objects.create(name="Врач")
        self.user = User.objects.create_user(
            username="ivanov",
            password="StrongPass123",
            first_name="Иван",
            last_name="Иванов",
            patronymic="Иванович",
            position=self.position,
        )

    def test_user_serializer_output_fields(self):
        """Сериализатор должен возвращать ожидаемые поля и не возвращать пароль."""
        data = UserSerializer(self.user).data

        # Ожидаемый набор полей согласно Meta.fields сериализатора
        expected_fields = {
            'id', 'username', 'first_name', 'last_name', 'patronymic',
            'position', 'position_id', 'position_name', 'date_joined',
            'is_active', 'is_staff', 'avatar'
        }
        self.assertEqual(set(data.keys()), expected_fields)

        # Проверяем базовые значения
        self.assertEqual(data['username'], "ivanov")
        self.assertEqual(data['first_name'], "Иван")
        self.assertEqual(data['last_name'], "Иванов")
        self.assertEqual(data['patronymic'], "Иванович")

        # Пароль отсутствует в сериализации
        self.assertNotIn('password', data)

    def test_user_serializer_position_fields(self):
        """Поле position должно содержать PK, а вычисляемые поля должны соответствовать связанной модели."""
        data = UserSerializer(self.user).data

        self.assertEqual(data['position'], self.position.pk)
        self.assertEqual(data['position_id'], self.position.pk)
        self.assertEqual(data['position_name'], self.position.name)

    def test_user_serializer_avatar_none(self):
        """Если аватар не задан, сериализуется как None (пустое значение)."""
        data = UserSerializer(self.user).data
        # Для ImageField с null=True DRF возвращает None, если файл не задан
        self.assertIsNone(data['avatar'])

    def test_user_serializer_is_read_only(self):
        """Все поля read-only: попытка обновить данные через сериализатор не должна менять модель."""
        orig_first_name = self.user.first_name

        serializer = UserSerializer(instance=self.user, data={
            'first_name': 'Пётр',
            'last_name': 'Петров',
        }, partial=True)

        # Валидный, но все переданные поля read-only, поэтому validated_data пустой
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertEqual(serializer.validated_data, {})

        updated = serializer.save()
        updated.refresh_from_db()

        # Имя и фамилия не изменились
        self.assertEqual(updated.first_name, orig_first_name)
        self.assertEqual(updated.last_name, self.user.last_name)
