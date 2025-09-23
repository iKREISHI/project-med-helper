from typing import Any, Dict
from django.http import HttpRequest
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes
)

from apps.chat.models import ChatMessage
from ..serializers.chat_basic_serializers import (
    ChatMessageSerializer,
    DialogSendMessageSerializer,
    PaginatedChatMessageSerializer,
)
from ..pagination import DialogMessagePagination
from apps.chat.service.chat_service import ask_llm_and_save_once, sse_stream_and_save


@extend_schema(tags=["dialogs"])
class DialogMessageView(generics.GenericAPIView, generics.ListAPIView):
    """
    • GET  /api/v0/chat/dialogs/{id}/message  – история сообщений (пагинация)
    • POST /api/v0/chat/dialogs/{id}/message  – отправить сообщение & получить LLM-ответ
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ChatMessageSerializer
    pagination_class   = DialogMessagePagination

    def get_serializer_class(self):
        return (DialogSendMessageSerializer
                if self.request.method.lower() == "post"
                else ChatMessageSerializer)

    @extend_schema(
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        responses={200: PaginatedChatMessageSerializer},
        examples=[
            OpenApiExample(
                "Пример ответа",
                response_only=True,
                status_codes=["200"],
                value={
                    "count": 2,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "role": "user",
                            "content": "Привет!",
                            "created_at": "2025-09-21T10:00:00Z"
                        },
                        {
                            "id": 2,
                            "role": "assistant",
                            "content": "Здравствуйте!",
                            "created_at": "2025-09-21T10:00:01Z"
                        }
                    ]
                },
            )
        ],
        description="Пагинированный список сообщений",
    )
    def get(self, request: HttpRequest, dialog_id: int, *args, **kwargs):
        return super().get(request, dialog_id=dialog_id, *args, **kwargs)

    def get_queryset(self):
        dialog_id = self.kwargs["dialog_id"]
        return (ChatMessage.objects
                .filter(session__id=dialog_id, session__user=self.request.user)
                .order_by("created_at"))

    @extend_schema(
        request=DialogSendMessageSerializer,
        responses={200: ChatMessageSerializer},
        examples=[
            OpenApiExample(
                "Send message",
                value={"content": "Как и чем лечить пневмонию?", "stream": False},
                request_only=True,
            ),
        ],
    )
    def post(self, request: HttpRequest, dialog_id: int, *args, **kwargs):
        ser = DialogSendMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data: Dict[str, Any] = ser.validated_data

        llm_kwargs = dict(
            search_mode="hybrid",
            k=10,
            doc_id=None,
            section=None,
            provider_params=data.get("params") or {},
        )
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
        return Response(ChatMessageSerializer(answer_msg).data,
                        status=status.HTTP_200_OK)
