from rest_framework import serializers
from apps.docs_ingest.models import Document

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id","title","file","source","language"]
        read_only_fields = ["id"]


class DocumentOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["id"]
