from rest_framework.permissions import AllowAny

from apps.llm.llm_providers  import get_provider
from .serializers import ChatRequestSerializer, ChatResponseSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="Unified chat completions",
    tags=["chat"],
    request=ChatRequestSerializer,
    responses={
        # обычный JSON-ответ
        200: OpenApiResponse(
            response=ChatResponseSerializer,
            description="Полный ответ LLM при «stream = false»",
        ),
        # поток SSE — ключ-кортеж задаёт media-type
        (200, "text/event-stream"): OpenApiResponse(
            response=OpenApiTypes.STR,          # заглушка-схема
            description="Поток токенов (SSE) при «stream = true»",
        ),
    },
    examples=[
        OpenApiExample(
            name="Simple request",
            value={
                "messages": [
                    {"role": "user", "content": "Почему небо голубое?"}
                ],
                "stream": False,
            },
            request_only=True,
        ),
    ],
)
class ChatViewSet(viewsets.ViewSet):
    """
    /api/chat/  (POST → create)
    Провайдер выбирается через переменную окружения **LLM_PROVIDER**.
    """

    permission_classes = [AllowAny]
    serializer_class = ChatRequestSerializer

    def create(self, request):
        """
        POST данные валидируются сериализатором.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        provider = get_provider()
        messages = data["messages"]
        params   = data.get("params", {})

        if data.get("stream"):
            iterator = provider.chat(messages, stream=True, **params)
            return StreamingHttpResponse(
                iterator,
                content_type="text/event-stream",
                headers={"Cache-Control": "no-cache"},
            )

        answer = provider.chat(messages, **params)
        return Response({"answer": answer}, status=status.HTTP_200_OK)

