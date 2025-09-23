from django.db import transaction
from rest_framework import serializers

from apps.semd_templates.models import (
    DocumentTemplate,
    FieldDefinition,
    DocumentInstance,
    DocumentFieldValue,
)


class FieldDefinitionSlimSerializer(serializers.ModelSerializer):
    """
    Короткое представление поля шаблона.
    Берём только реально существующие колонки модели, чтобы не падать,
    если в проекте нет, например, `type`.
    """
    class Meta:
        model = FieldDefinition
        fields = tuple(
            n
            for n in ("id", "key", "label", "type")
            if n in {f.name for f in FieldDefinition._meta.fields}
        )


class DocumentTemplateSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ("id", "name")


#  VALUES (CREATE / READ)
class DocumentFieldValueCreateSerializer(serializers.ModelSerializer):
    """ Используется ТОЛЬКО при создании документа. """
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldDefinition.objects.all(),
        source="field",
    )

    class Meta:
        model = DocumentFieldValue
        fields = ("field_id", "value")


class DocumentFieldValueSerializer(serializers.ModelSerializer):
    """Для чтения значений поля (GET‐запросы)"""
    field = FieldDefinitionSlimSerializer(read_only=True)

    class Meta:
        model = DocumentFieldValue
        fields = ("id", "field", "value")


# VALUES (UPDATE)
class DocumentFieldValueUpdateSerializer(serializers.ModelSerializer):
    """
    Для PATCH одного значения И для bulk-списка.
    * id — обязателен, чтобы знать какую строку изменять;
    * value — обязателен, иначе валидация упадёт (это нужно для теста
      `test_bulk_update_validation_error`).
    """
    id = serializers.IntegerField()
    value = serializers.JSONField(required=True)

    class Meta:
        model = DocumentFieldValue
        fields = ("id", "value")


class DocumentFieldValueBulkUpdateListSerializer(serializers.ListSerializer):
    """
    PATCH нескольких значений одним запросом.
    Сопоставляем по первичному ключу `id`.
    """
    child = DocumentFieldValueUpdateSerializer()

    def update(self, instances, validated_data):
        instance_map = {obj.id: obj for obj in instances}
        data_map = {item["id"]: item for item in validated_data}

        updated_objects = []
        for obj_id, obj in instance_map.items():
            item = data_map.get(obj_id)
            if item:
                obj.value = item["value"]
                obj.save(update_fields=["value"])
            updated_objects.append(obj)
        return updated_objects


# DOCUMENT (READ)
class DocumentInstanceSerializer(serializers.ModelSerializer):
    template = DocumentTemplateSlimSerializer(read_only=True)
    field_values = DocumentFieldValueSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentInstance
        fields = (
            "id",
            "template",
            "user",
            "created_at",
            "updated_at",
            "field_values",
        )


#  DOCUMENT (CREATE)
class DocumentInstanceCreateSerializer(serializers.ModelSerializer):
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentTemplate.objects.all(),
        source="template",
    )
    fields = DocumentFieldValueCreateSerializer(many=True, write_only=True)

    class Meta:
        model = DocumentInstance
        fields = ("template_id", "fields")

    def create(self, validated_data):
        fields_data = validated_data.pop("fields", [])
        user = self.context["request"].user

        with transaction.atomic():
            doc = DocumentInstance.objects.create(user=user, **validated_data)
            DocumentFieldValue.objects.bulk_create(
                [
                    DocumentFieldValue(document=doc, **item)
                    for item in fields_data
                ]
            )
        return doc

    def to_representation(self, instance):
        """Чтобы сразу вернуть полное представление документа."""
        return DocumentInstanceSerializer(instance, context=self.context).data
