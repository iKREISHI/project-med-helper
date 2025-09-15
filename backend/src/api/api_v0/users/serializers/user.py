from rest_framework import serializers
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления основных полей пользователя.

    Примечания:
    - Поле `position` отдаётся как первичный ключ связанной модели (по умолчанию
      поведения DRF для ForeignKey). При необходимости можно заменить на
      вложенный сериализатор или строковое представление.
    - Дополнительно отдаем «похожим образом» отдельные поля `position_id` и
      `position_name`, получая их из связанной модели `Position`.
    - Поле `avatar` будет сериализовано как относительный путь/URL к файлу.
    """

    # «Похожим образом» на предложенный пример: вычисляемые поля из связанной должности
    position_id = serializers.IntegerField(source='position.id', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)

    class Meta:
        model = User
        # Минимально достаточный набор полей для отображения информации о пользователе
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'patronymic',
            'position',
            'position_id',
            'position_name',
            'date_joined',
            'is_active',
            'is_staff',
            'avatar',
        )
        read_only_fields = fields
