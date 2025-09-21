"""
ViewSet для входа пользователя в систему.

Назначение:
- Принимает имя пользователя и пароль через `LoginSerializer`.
- Проводит аутентификацию и создаёт серверную сессию через `django.contrib.auth.login`.
- Возвращает минимальное представление пользователя.

Примечания:
- ViewSet ничего не знает про токены — только сессии. Для токен-авторизации потребуется отдельная реализация.
- Все сообщения и документация ориентированы на русскоязычную аудиторию.
"""
from __future__ import annotations

from django.contrib.auth import login as django_login
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from ..serializers.login import LoginSerializer
from ..serializers.minimal_user import MinimalUserSerializer


class LoginViewSet(viewsets.ViewSet):
    """Вход в систему (логин) по имени пользователя и паролю.

    POST /auth/login/ — принимает `username` и `password`.
    При успехе создаётся сессия и возвращаются основные данные пользователя.
    """
    http_method_names = ['post']
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Вход в систему (создание сессии)",
        description=(
            "Принимает имя пользователя и пароль. При успешной аутентификации создаёт "
            "серверную сессию и возвращает минимальные данные пользователя."
        ),
        request=LoginSerializer,
        responses={
            200: MinimalUserSerializer,
            400: OpenApiResponse(description="Ошибки валидации входных данных"),
        },
        tags=["Аутентификация",],
        operation_id="auth_login_create",
    )
    def create(self, request: Request) -> Response:
        """Обрабатывает POST-запрос на вход.

        Тело запроса:
        - username: str
        - password: str

        Ответ 200 OK: минимальные данные пользователя.
        Ответ 400: ошибки валидации.
        """
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        # Создаём серверную сессию
        django_login(request, user)

        data = MinimalUserSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)
