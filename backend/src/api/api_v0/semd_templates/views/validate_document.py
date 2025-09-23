from __future__ import annotations

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
)

from apps.semd_templates.models import DocumentInstance
from apps.semd_templates.validators.services import validate_document_instance
from ..serializers.validator_serializers import (
    DocumentInstanceSerializer,
    DocumentInstanceValidationResponseSerializer,
)

@extend_schema(tags=["SEMD module"])
@extend_schema_view(
    retrieve=extend_schema(
        summary="Получить документ",
        responses={200: DocumentInstanceSerializer},
    ),
)
class DocumentValidatorViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Только read-доступ + отдельное действие `validate`.

    Право на доступ — владелец документа или staff-пользователь.
    """
    queryset = (
        DocumentInstance.objects.select_related("template", "user").all()
    )
    serializer_class = DocumentInstanceSerializer
    permission_classes = [IsAuthenticated]

    # кастомное действие
    @extend_schema(
        tags=["SEMD module"],
        methods=["POST"],
        summary="Проверить документ",
        description=(
            "Запускает серверную и/или LLM-валидацию всех полей в "
            "документе.\n\n"
            "- Если стратегия поля = `server`, проверяется только сервер.\n"
            "- `llm` — только ИИ (пока заглушка).\n"
            "- `both` — и сервер, и ИИ.\n"
            "- `none` — ничего.\n\n"
            "В ответе возвращается JSON с подробными результатами и, при "
            "наличии, сформированный payload для LLM-сервиса."
        ),
        responses={
            200: DocumentInstanceValidationResponseSerializer,
            403: {"description": "Недостаточно прав."},
            404: {"description": "Документ не найден."},
        },
        examples=[
            OpenApiExample(
                "Успешная валидация",
                value={
                    "overall_status": "valid",
                    "fields": {
                        "anamnesis": {
                            "server_errors": [],
                            "llm_errors": [],
                            "status": "valid",
                        }
                    },
                    "llm_payload": "",
                },
                response_only=True,
            ),
            OpenApiExample(
                "Документ с ошибками",
                value={
                    "overall_status": "invalid",
                    "fields": {
                        "blood_pressure": {
                            "server_errors": [
                                "Значение должно быть ≤ 200."
                            ],
                            "llm_errors": [],
                            "status": "invalid",
                        }
                    },
                    "llm_payload": "{\n  \"template_slug\": \"epicrisis\",\n  "
                    "\"document_id\": 42,\n  \"fields\": {\n    \"anamnesis\": "
                    "\"Пациент жалуется ...\"\n  }\n}",
                },
                response_only=True,
            ),
        ],
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="validate",
        permission_classes=[IsAuthenticated],
    )
    def validate(self, request, pk: int | str = None):
        instance = self.get_object()

        # Проверка прав доступа
        if instance.user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Недостаточно прав."},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_valid, details, llm_payload_json = validate_document_instance(
            instance
        )

        serializer = DocumentInstanceValidationResponseSerializer(
            {
                "overall_status": "valid" if is_valid else "invalid",
                "fields": details,
                "llm_payload": llm_payload_json,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
