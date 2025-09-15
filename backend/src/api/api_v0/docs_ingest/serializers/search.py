from rest_framework import serializers

class SearchHitSerializer(serializers.Serializer):
    score = serializers.FloatField()
    doc_id = serializers.IntegerField()
    owner_id = serializers.IntegerField(required=False)
    idx = serializers.IntegerField()
    section = serializers.CharField(allow_blank=True)
    page_from = serializers.IntegerField(allow_null=True)
    page_to = serializers.IntegerField(allow_null=True)
    text = serializers.CharField()

class SearchResponseSerializer(serializers.Serializer):
    q = serializers.CharField()
    mode = serializers.ChoiceField(choices=["vector", "hybrid"])
    results = SearchHitSerializer(many=True)
