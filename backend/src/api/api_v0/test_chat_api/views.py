from __future__ import annotations
from typing import Any, Dict, Generator
from django.http import StreamingHttpResponse
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)

from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ChatMessageSerializer,
)
from apps.llm.mode.clinical_reference_llm import ClinicalLLM


@extend_schema(
    summary="Unified chat completions (clinical & generic)",
    tags=["chat"],
    request=ChatRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=ChatResponseSerializer,
            description="Полный ответ LLM при «stream = false»",
        ),
        (200, "text/event-stream"): OpenApiResponse(
            response=OpenApiTypes.STR,
            description="Поток токенов (SSE) при «stream = true»",
        ),
    },
    examples=[
        OpenApiExample(
            name="Simple request",
            value={
                "messages": [
                    {"role": "user", "content": "Какова доза статинов при высоком риске ИБС?"}
                ],
                "stream": False,
            },
            request_only=True,
        ),
    ],
)
class ChatViewSet(viewsets.ViewSet):
    """
    /api/test-chat/  (POST → create)

    Настраиваемые query-параметры:
        mode     – 'vector' | 'hybrid'  (по умолчанию 'vector')
        k        – int, количество фрагментов CONTEXT (по умолчанию 5)
        doc_id   – int | None, фильтр документа
        section  – str | None, фильтр секции/главы
    """

    permission_classes = [AllowAny]
    serializer_class = ChatRequestSerializer

    @staticmethod
    def _extract_question(messages: list[Dict[str, str]]) -> str:
        """
        Берём последний message с role='user' как вопрос.
        """
        for msg in reversed(messages):
            if msg["role"] == "user":
                return msg["content"].strip()
        return ""

    @staticmethod
    def _sse_iterator(tokens: Generator[str, None, None]) -> Generator[bytes, None, None]:
        """
        Преобразует plain-токены в поток SSE.
        """
        for token in tokens:
            yield f"data: {token}\n\n".encode("utf-8")
        yield b"event: end\ndata: [END]\n\n"

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        messages: list[Dict[str, str]] = data["messages"]
        params:    Dict[str, Any]      = data.get("params", {})
        stream:    bool                = data.get("stream", False)

        question = self._extract_question(messages)
        if not question:
            return Response(
                {"detail": "Не найден message с role='user'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mode     = (request.query_params.get("mode") or "vector").lower()
        try:
            k      = int(request.query_params.get("k") or 5)
        except ValueError:
            return Response({"detail": "k должен быть целым числом."}, status=400)

        doc_id_qp = request.query_params.get("doc_id")
        doc_id    = int(doc_id_qp) if doc_id_qp is not None else None
        section   = (request.query_params.get("section") or "").strip() or None

        llm = ClinicalLLM(
            search_mode="hybrid",
            k=k,
            doc_id=doc_id,
            section=section,
            provider_params=params,
        )

        if stream:
            token_gen = llm.ask(question, stream=True)
            return StreamingHttpResponse(
                self._sse_iterator(token_gen),
                content_type="text/event-stream",
                headers={"Cache-Control": "no-cache"},
            )

        answer: str = llm.ask(question)
        return Response({"answer": answer}, status=status.HTTP_200_OK)
