"""
Минимальный сериализатор пользователя вынесен в отдельный модуль,
чтобы каждый файл отвечал за один класс сериализатора.
"""
from rest_framework import serializers

from apps.users.models import User


class MinimalUserSerializer(serializers.ModelSerializer):
    """
    Минимальный сериализатор пользователя для отображения основных атрибутов.

    Назначение:
    - Используется там, где нужен краткий профиль пользователя без служебных полей.
    - Все поля только для чтения, чтобы не допускать записи через этот сериализатор.
    """

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'patronymic',
        )
        read_only_fields = fields
