from typing import Any, Dict
from django.http import HttpRequest
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from apps.chat.models import ChatSession, ChatMessage
from ..serializers.chat_basic_serializers import (
    DialogCreateSerializer,
    DialogSerializer,
    ChatMessageSerializer,
    DialogSendMessageSerializer,
)
from ..pagination import DialogMessagePagination
from apps.chat.service.chat_service import ask_llm_and_save_once, sse_stream_and_save


@extend_schema(tags=["dialogs"])
class DialogMessageView(generics.GenericAPIView, generics.ListAPIView):
    """
    • GET  /api/v0/chat/dialogs/{id}/message      – история сообщений (пагинация)
    • POST /api/v0/chat/dialogs/{id}/message      – отправить сообщение & получить LLM-ответ
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatMessageSerializer
    pagination_class = DialogMessagePagination

    # Выбор сериализатора зависит от метода
    def get_serializer_class(self):
        if self.request.method.lower() == "post":
            return DialogSendMessageSerializer
        return ChatMessageSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter("page",      OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses={200: ChatMessageSerializer(many=True)},
    )
    def get(self, request: HttpRequest, dialog_id: int, *args, **kwargs):
        return super().get(request, dialog_id=dialog_id, *args, **kwargs)

    def get_queryset(self):
        dialog_id = self.kwargs["dialog_id"]
        return (
            ChatMessage.objects
            .filter(session__id=dialog_id, session__user=self.request.user)
            .order_by("created_at")
        )

    @extend_schema(
        request=DialogSendMessageSerializer,
        responses={
            200: ChatMessageSerializer,
            (200, "text/event-stream"): OpenApiResponse(
                OpenApiTypes.STR, description="SSE-поток токенов (stream=true)"
            ),
        },
        examples=[
            OpenApiExample(
                "Send message",
                value={"content": "Какова доза статинов?", "stream": False},
                request_only=True,
            )
        ],
    )
    def post(self, request: HttpRequest, dialog_id: int, *args, **kwargs):
        ser = DialogSendMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data: Dict[str, Any] = ser.validated_data

        llm_kwargs = dict(
            search_mode="vector",
            k=5,
            doc_id=None,
            section=None,
            provider_params=data.get("params") or {},
        )

        # текущее сообщение пользователя
        messages = [{"role": "user", "content": data["content"]}]

        if data.get("stream", False):
            return sse_stream_and_save(
                user=request.user,
                messages=messages,
                session_id=dialog_id,
                llm_kwargs=llm_kwargs,
            )

        _, answer_msg = ask_llm_and_save_once(
            user=request.user,
            messages=messages,
            session_id=dialog_id,
            llm_kwargs=llm_kwargs,
        )
        return Response(ChatMessageSerializer(answer_msg).data, status=status.HTTP_200_OK)
