from rest_framework import serializers
from apps.semd_templates.models.semd_fields import FieldDefinition


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
