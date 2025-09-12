"""
ViewSet для регистрации нового пользователя.

Назначение:
- Принимает минимально необходимый набор полей для создания пользователя через `RegisterSerializer`.
- Создаёт пользователя, но НЕ проводит аутентификацию (сессию не создаём).
- Возвращает минимальные данные пользователя в ответе.

Примечания:
- Для входа после регистрации используйте эндпоинт логина.
- Все тексты и документация на русском языке, согласно общим правилам проекта.
"""
from __future__ import annotations

from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from ..serializers.register import RegisterSerializer
from ..serializers.minimal_user import MinimalUserSerializer


class RegisterViewSet(viewsets.ViewSet):
    """Регистрация нового пользователя.

    POST /auth/register/ — принимает необходимые данные пользователя и создаёт запись.
    Пароль сохраняется в захешированном виде. Сессия при этом не создаётся.
    """

    http_method_names = ["post"]
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Регистрация пользователя",
        description=(
            "Создаёт нового пользователя по переданным данным. Пароль сохраняется в хешированном виде.\n\n"
            "Аутентификация после регистрации не выполняется автоматически — используйте эндпоинт логина."
        ),
        request=RegisterSerializer,
        responses={
            201: MinimalUserSerializer,
            400: OpenApiResponse(description="Ошибки валидации входных данных"),
        },
        tags=["Аутентификация", "Пользователи"],
        operation_id="auth_register_create",
    )
    def create(self, request: Request) -> Response:
        """Обрабатывает POST-запрос на регистрацию пользователя.

        Тело запроса: поля согласно RegisterSerializer. Возвращает минимальные данные пользователя.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = MinimalUserSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)
