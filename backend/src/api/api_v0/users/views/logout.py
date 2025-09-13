"""
ViewSet для выхода пользователя из системы (разлогин).

Назначение:
- Уничтожает серверную сессию текущего пользователя через `django.contrib.auth.logout`.
- Эндпоинт идемпотентный: если пользователь не был залогинен, всё равно возвращается 204 No Content.

Примечания:
- Эндпоинт реализован «похожим образом», как логин: отдельный ViewSet с методом `create` (POST).
- Для документации используется `drf-spectacular` через декоратор `@extend_schema`.
"""
from __future__ import annotations

from django.contrib.auth import logout as django_logout
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse


class LogoutViewSet(viewsets.ViewSet):
    """Выход из системы (разлогин).

    POST /auth/logout/ — уничтожает серверную сессию пользователя.
    Возвращает 204 No Content вне зависимости от исходного состояния (идемпотентно).
    """

    http_method_names = ["post"]
    # Разрешим вызов без аутентификации, чтобы поведение было идемпотентным
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Выход из системы (уничтожение сессии)",
        description=(
            "Завершает серверную сессию текущего пользователя. Операция идемпотентна: "
            "если пользователь не был аутентифицирован, также возвращается 204."
        ),
        request=None,
        responses={
            204: OpenApiResponse(description="Сессия уничтожена (или отсутствовала)"),
        },
        tags=["Аутентификация", "Пользователи"],
        operation_id="auth_logout_create",
    )
    def create(self, request: Request) -> Response:
        """Обрабатывает POST-запрос на выход из системы.

        Ответ 204 No Content.
        """
        # Уничтожаем текущую сессию пользователя (если есть)
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
