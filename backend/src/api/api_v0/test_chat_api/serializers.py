from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    role    = serializers.ChoiceField(choices=["system", "user", "assistant"])
    content = serializers.CharField()


class ChatRequestSerializer(serializers.Serializer):
    messages = ChatMessageSerializer(many=True)
    stream   = serializers.BooleanField(default=False)
    params   = serializers.DictField(
        child=serializers.JSONField(), required=False,
        help_text="Любые параметры, поддерживаемые моделью (temperature, top_p …)"
    )


class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField(help_text="Полный ответ LLM — возвращается, если stream=false")
