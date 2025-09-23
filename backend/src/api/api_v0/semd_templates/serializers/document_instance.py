from django.db import transaction
from rest_framework import serializers
from apps.semd_templates.models import (
    DocumentTemplate,
    FieldDefinition,
    DocumentInstance,
    DocumentFieldValue,
)


class FieldDefinitionSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = tuple(
            n for n in ("id", "key", "label", "type")
            if n in {f.name for f in FieldDefinition._meta.fields}
        )


class DocumentTemplateSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ("id", "name")


#  VALUES (CREATE / READ)
class DocumentFieldValueCreateSerializer(serializers.ModelSerializer):
    field_id = serializers.PrimaryKeyRelatedField(
        queryset=FieldDefinition.objects.all(), source="field"
    )

    class Meta:
        model = DocumentFieldValue
        fields = ("field_id", "value")


class DocumentFieldValueSerializer(serializers.ModelSerializer):
    field = FieldDefinitionSlimSerializer(read_only=True)

    class Meta:
        model = DocumentFieldValue
        fields = ("id", "field", "value")


class DocumentFieldValueUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    value = serializers.JSONField(required=True)

    class Meta:
        model = DocumentFieldValue
        fields = ("id", "value")


class DocumentFieldValueBulkUpdateListSerializer(serializers.ListSerializer):
    """PATCH many."""

    child = DocumentFieldValueUpdateSerializer()

    def validate(self, data):
        instance_ids = {inst.id for inst in self.instance}
        payload_ids = {item["id"] for item in data}

        # лишние ids (не принадлежат документу)
        unknown = payload_ids - instance_ids
        if unknown:
            raise serializers.ValidationError(
                f"IDs {sorted(unknown)} do not belong to this document."
            )
        return data

    def update(self, instances, validated_data):
        inst_map = {obj.id: obj for obj in instances}
        data_map = {obj["id"]: obj for obj in validated_data}

        updated = []
        for obj_id, obj in inst_map.items():
            if obj_id in data_map:
                obj.value = data_map[obj_id]["value"]
                obj.save(update_fields=["value"])
            updated.append(obj)
        return updated


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
        queryset=DocumentTemplate.objects.all(), source="template"
    )
    fields = DocumentFieldValueCreateSerializer(many=True, write_only=True)

    class Meta:
        model = DocumentInstance
        fields = ("template_id", "fields")

    def validate(self, attrs):
        fields_data = attrs.get("fields", [])
        ids = [item["field"].id for item in fields_data]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                {"fields": "Duplicate field_id in payload."}
            )
        return attrs

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
        return DocumentInstanceSerializer(instance, context=self.context).data
