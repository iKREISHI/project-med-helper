from rest_framework import serializers

from apps.semd_templates.models import FieldDefinition, TemplateField, DocumentTemplate


class FieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldDefinition
        fields = [
            "id",
            "key",
            "label",
            "field_type",
            "required",
            "server_validators",
            "validation_strategy",
        ]


class TemplateFieldSerializer(serializers.ModelSerializer):
    field = FieldDefinitionSerializer()

    class Meta:
        model = TemplateField
        fields = ["order", "field"]


class DocumentTemplateSerializer(serializers.ModelSerializer):
    fields = TemplateFieldSerializer(
        source="templatefield_set", many=True, read_only=True
    )

    class Meta:
        model = DocumentTemplate
        fields = ["id", "name", "slug", "description", "fields"]