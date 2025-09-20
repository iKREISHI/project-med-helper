from rest_framework import serializers
from apps.chat.models import ChatMessage, ChatSession


class RoleContentSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[
        (ChatMessage.ROLE_USER, "user"),
        (ChatMessage.ROLE_ASSISTANT, "assistant"),
        (ChatMessage.ROLE_SYSTEM, "system"),
    ])
    content = serializers.CharField(max_length=8_000)


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("id", "role", "content", "created_at")


class DialogCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120, required=False, allow_blank=True)


class DialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ("id", "title", "created_at")


class DialogSendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=8_000)
    params  = serializers.DictField(required=False)
    stream  = serializers.BooleanField(default=False)
