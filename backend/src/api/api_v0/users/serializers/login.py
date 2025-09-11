"""
Сериализатор для входа пользователя (аутентификация по имени пользователя и паролю).

Назначение:
- Принимает имя пользователя и пароль.
- Пытается аутентифицировать пользователя через стандартные бекенды Django.
- Возвращает объект пользователя в validated_data по ключу "user" при успехе.

Примечания:
- Сериализатор сам по себе не создаёт токены/сессии, этим должен заниматься View.
- Все сообщения об ошибках ориентированы на русскоязычную аудиторию.
"""
from typing import Any, Dict

from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Простой сериализатор логина по username и password."""

    username = serializers.CharField(label='Имя пользователя', allow_blank=False)
    password = serializers.CharField(
        label='Пароль', write_only=True, style={'input_type': 'password'}, trim_whitespace=False
    )

    default_error_messages = {
        'invalid_credentials': 'Неверное имя пользователя или пароль.',
        'inactive': 'Учётная запись отключена. Обратитесь к администратору.',
        'required_username': 'Необходимо указать имя пользователя.',
        'required_password': 'Необходимо указать пароль.',
    }

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Проводит аутентификацию пользователя.
        Возвращает словарь с ключом "user" при успешной проверке.
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if not username:
            raise serializers.ValidationError({'username': self.error_messages['required_username']})
        if not password:
            # Сообщение для поля пароля, чтобы фронту было проще подсветить нужное поле
            raise serializers.ValidationError({'password': self.error_messages['required_password']})

        user = authenticate(self.context.get('request'), username=username, password=password)
        if user is None:
            # Унифицированное сообщение, чтобы не раскрывать причину (безопасность)
            raise serializers.ValidationError({'non_field_errors': [self.error_messages['invalid_credentials']]})

        if not getattr(user, 'is_active', True):
            raise serializers.ValidationError({'non_field_errors': [self.error_messages['inactive']]})

        attrs['user'] = user
        return attrs
