from __future__ import annotations

from rest_framework import serializers
from apps.semd_templates.models import DocumentInstance


class DocumentFieldValidationSerializer(serializers.Serializer):
    """
    Результат проверки одного поля.
    """
    server_errors = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="Ошибки серверных валидаторов.",
    )
    llm_errors = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="Ошибки LLM-валидации.",
    )
    status = serializers.ChoiceField(
        choices=[("valid", "valid"), ("invalid", "invalid")],
        read_only=True,
        help_text="Итоговый статус поля.",
    )


class DocumentInstanceValidationResponseSerializer(serializers.Serializer):
    """
    Ответ на POST /documents/{id}/validate/
    """
    overall_status = serializers.ChoiceField(
        choices=[("valid", "valid"), ("invalid", "invalid")],
        read_only=True,
        help_text="Сводный статус документа.",
    )
    fields = serializers.DictField(
        child=DocumentFieldValidationSerializer(),
        read_only=True,
        help_text="Подробные результаты по каждому полю.",
    )
    llm_payload = serializers.CharField(
        read_only=True,
        allow_blank=True,
        help_text=(
            "JSON, отправляемый LLM-сервису (показывается только если "
            "в документе есть поля со стратегией 'llm' или 'both')."
        ),
    )


class DocumentInstanceSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для retrieve (GET /documents/{id}/).
    """
    template = serializers.SlugRelatedField(
        read_only=True, slug_field="slug"
    )
    user = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        model = DocumentInstance
        fields = (
            "id",
            "template",
            "user",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
