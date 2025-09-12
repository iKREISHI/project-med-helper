"""
ViewSet для работы с данными текущего пользователя.

Назначение:
- Возвращает подробную информацию о текущем (аутентифицированном) пользователе.
- Использует полноценный сериализатор пользователя `UserSerializer`.

Примечания:
- Эндпоинт доступен только для аутентифицированных пользователей (cookie-сессия/Django auth).
- Роут: GET /api/v0/users/me/
"""
from __future__ import annotations

from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ..serializers.user import UserSerializer
from ..serializers.minimal_user import MinimalUserSerializer


class UsersViewSet(viewsets.ViewSet):
    """Набор представлений, связанный с пользователями.

    В рамках API v0 содержит действие `me` для получения данных текущего пользователя.
    """

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    @extend_schema(
        summary="Текущий пользователь",
        description=(
            "Возвращает подробные данные текущего аутентифицированного пользователя.\n\n"
            "Требуется активная сессия (cookie) или другая совместимая схема аутентификации."
        ),
        responses={200: UserSerializer},
        tags=["Пользователи"],
        operation_id="users_me_retrieve",
    )
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request: Request) -> Response:
        """Возвращает сериализованные данные текущего пользователя.

        Ответ 200 OK: тело соответствует `UserSerializer`.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Текущий пользователь (минимально)",
        description=(
            "Возвращает минимальный набор данных текущего аутентифицированного пользователя.\n\n"
            "Требуется активная сессия (cookie) или другая совместимая схема аутентификации."
        ),
        responses={200: MinimalUserSerializer},
        tags=["Пользователи"],
        operation_id="users_me_minimal_retrieve",
    )
    @action(detail=False, methods=["get"], url_path="me/minimal")
    def me_minimal(self, request: Request) -> Response:
        """Возвращает минимальные данные текущего пользователя.

        Ответ 200 OK: тело соответствует `MinimalUserSerializer`.
        """
        serializer = MinimalUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
