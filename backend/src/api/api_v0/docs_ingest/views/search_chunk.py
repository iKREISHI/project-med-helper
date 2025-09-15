from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample

from apps.docs_ingest.vectors import vector_search, hybrid_search
from api.api_v0.docs_ingest.serializers.search import SearchResponseSerializer, SearchHitSerializer

class SearchViewSet(viewsets.ViewSet):
    """
    GET /search/?q=...&k=5&mode=vector&doc_id=123&section=...
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Search"],
        summary="Поиск по эмбеддингам (vector/hybrid) в Qdrant",
        description=(
            "Ищет релевантные чанки по запросу `q`. "
            "`mode=vector` — чисто векторный поиск, `mode=hybrid` — гибридный (вектор + полнотекст, если настроен индекс). "
            "По умолчанию результаты ограничены документами текущего пользователя."
        ),
        parameters=[
            OpenApiParameter(name="q", type=OpenApiTypes.STR, required=True, description="Поисковый запрос"),
            OpenApiParameter(name="k", type=OpenApiTypes.INT, required=False, description="Количество результатов (top-k)", default=5),
            OpenApiParameter(name="mode", type=OpenApiTypes.STR, required=False,
                             description="Режим поиска: vector | hybrid", default="vector"),
            OpenApiParameter(name="doc_id", type=OpenApiTypes.INT, required=False,
                             description="(опц.) Фильтр по конкретному документу"),
            OpenApiParameter(name="section", type=OpenApiTypes.STR, required=False,
                             description="(опц.) Фильтр по названию/части названия раздела (payload.section)"),
        ],
        responses={200: SearchResponseSerializer},
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={"q": "Противопоказания ингаляционных ГКС", "mode": "vector", "k": 5}
            )
        ],
    )
    def list(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"detail": "Parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            k = int(request.query_params.get("k", 5))
        except ValueError:
            k = 5

        mode = (request.query_params.get("mode") or "vector").lower()
        doc_id = request.query_params.get("doc_id")
        section = (request.query_params.get("section") or "").strip() or None

        extra_filters = {}
        if section:
            # точное совпадение; если хотите contains — надо фильтровать на приложении
            extra_filters["section"] = section

        owner_id = request.user.id

        if mode == "hybrid":
            results = hybrid_search(q, top_k=k, owner_id=owner_id, doc_id=int(doc_id) if doc_id else None,
                                    extra_filters=extra_filters or None)
        else:
            results = vector_search(q, top_k=k, owner_id=owner_id, doc_id=int(doc_id) if doc_id else None,
                                    extra_filters=extra_filters or None)

        payload = {"q": q, "mode": mode if mode in ("vector", "hybrid") else "vector", "results": results}
        # валидируем через сериализатор для корректной схемы
        resp_ser = SearchResponseSerializer(payload)
        return Response(resp_ser.data, status=200)
