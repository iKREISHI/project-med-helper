# ─── views/dialog_viewset.py ─────────────────────────────────────────────
from typing import Any, Dict, List

from django.http import HttpRequest
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes, OpenApiResponse,
)

from apps.chat.models import ChatSession, ChatMessage
from ..serializers.chat_basic_serializers import (
    DialogSerializer, DialogCreateSerializer,
    ChatMessageSerializer, DialogSendMessageSerializer,
    PaginatedChatMessageSerializer,
)
from ..pagination import DialogMessagePagination
from apps.chat.service.chat_service import ask_llm_and_save_once, sse_stream_and_save


@extend_schema(tags=["Чат-бот"])
class DialogViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    * **GET  /api/v0/chat/dialogs**               — список диалогов
    * **POST /api/v0/chat/dialogs**               — создать диалог
    * **GET  /api/v0/chat/dialogs/{id}/message**  — история сообщений
    * **POST /api/v0/chat/dialogs/{id}/message**  — отправить сообщение
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatSession.objects.all()
    pagination_class = DialogMessagePagination
    serializer_class = DialogSerializer  # default для list

    def get_serializer_class(self):
        if self.action == "create":
            return DialogCreateSerializer
        if self.action == "message":
            return (
                DialogSendMessageSerializer
                if self.request.method.lower() == "post"
                else ChatMessageSerializer
            )
        return super().get_serializer_class()

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    # POST /dialogs
    @extend_schema(
        request=DialogCreateSerializer,
        responses={201: DialogSerializer},
        examples=[OpenApiExample("Create dialog", value={"title": "Гипертония"})],
    )
    def create(self, request: HttpRequest, *args, **kwargs):
        ser = DialogCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dialog = ChatSession.objects.create(
            user=request.user, title=ser.validated_data.get("title", "")
        )
        return Response(DialogSerializer(dialog).data,
                        status=status.HTTP_201_CREATED)

    # /dialogs/{id}/message (GET + POST)
    @extend_schema(
        methods=["GET"],
        responses={200: PaginatedChatMessageSerializer},
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter("page_size", OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        description="Пагинированный список сообщений",
        examples=[
            OpenApiExample(
                "default",
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
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    @extend_schema(
        methods=["POST"],
        request=DialogSendMessageSerializer,
        responses={200: ChatMessageSerializer,
                   (200, "text/event-stream"):
                       OpenApiResponse(OpenApiTypes.STR,
                                       description="SSE-поток токенов (stream=true)")},
        examples=[
            OpenApiExample(
                "Send message",
                value={"content": "Какова доза статинов?", "stream": False},
                request_only=True,
            ),
        ],
    )
    @action(detail=True, methods=["get", "post"], url_path="message")
    def message(self, request: HttpRequest, pk: int | str = None):
        """GET → история; POST → отправка сообщения."""
        #  GET
        if request.method.lower() == "get":
            qs = (
                ChatMessage.objects
                .filter(session_id=pk, session__user=request.user)
                .order_by("created_at")
            )
            page = self.paginate_queryset(qs)
            ser = ChatMessageSerializer(page, many=True)
            return self.get_paginated_response(ser.data)

        # POST
        ser = DialogSendMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data: Dict[str, Any] = ser.validated_data

        llm_kwargs = dict(
            search_mode="vector", k=5, doc_id=None, section=None,
            provider_params=data.get("params") or {},
        )
        messages: List[Dict[str, str]] = [{"role": "user", "content": data["content"]}]

        if data.get("stream", False):
            return sse_stream_and_save(
                user=request.user,
                messages=messages,
                session_id=int(pk),
                llm_kwargs=llm_kwargs,
            )

        _, answer_msg = ask_llm_and_save_once(
            user=request.user,
            messages=messages,
            session_id=int(pk),
            llm_kwargs=llm_kwargs,
        )
        return Response(ChatMessageSerializer(answer_msg).data,
                        status=status.HTTP_200_OK)
