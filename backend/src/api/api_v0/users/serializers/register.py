"""
Сериализатор для регистрации нового пользователя.

Назначение:
- Принимает минимально необходимый набор полей для создания пользователя.
- Создаёт пользователя через менеджер модели (`create_user`), корректно хешируя пароль.
- Пароль доступен только на запись (write-only) и не попадает в выходные данные сериализатора.

Примечание:
- Поле `position` является обязательным по модели пользователя и должно указывать на существующую должность.
- Сериализатор не возвращает токены/сессии — только создаёт пользователя. Аутентификация выполняется отдельно.
"""
from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя.

    Ожидаемые входные поля:
    - username: строка, обязательна
    - password: строка, обязательна (write-only)
    - first_name, last_name, patronymic: необязательные строки
    - position: первичный ключ существующей должности (обязателен)

    На выходе не содержит поле `password`.
    """

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "first_name",
            "last_name",
            "patronymic",
            "position",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data: dict[str, Any]) -> User:
        """Создаёт пользователя через менеджер модели, хешируя пароль.

        Важно: используем `objects.create_user`, чтобы пароль был захеширован
        и применялись все внутренние политики создания пользователя.
        """
        password: str = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
