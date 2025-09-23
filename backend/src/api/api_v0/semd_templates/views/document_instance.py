from django.http import Http404
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from apps.semd_templates.models import DocumentInstance, DocumentFieldValue
from api.api_v0.semd_templates.serializers.document_instance import (
    DocumentInstanceSerializer,
    DocumentInstanceCreateSerializer,
    DocumentFieldValueSerializer,
    DocumentFieldValueUpdateSerializer,
    DocumentFieldValueBulkUpdateListSerializer,
)


# ──────────────────── пагинация c упорядочиванием ──────────────────────
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# ──────────────────── DocumentInstanceViewSet ───────────────────────────
@extend_schema(tags=["SEMD module"])
@extend_schema_view(
    list=extend_schema(summary="Список документов", responses=DocumentInstanceSerializer),
    retrieve=extend_schema(summary="Получить документ", responses=DocumentInstanceSerializer),
    create=extend_schema(summary="Создать документ", request=DocumentInstanceCreateSerializer,
                         responses=DocumentInstanceSerializer),
    destroy=extend_schema(summary="Удалить документ",
                          responses={204: OpenApiResponse(description="Deleted")}),
)
class DocumentInstanceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # порядок гарантирует стабильную пагинацию → нет warning’а
        return (
            DocumentInstance.objects
            .filter(user=self.request.user)
            .select_related("template")
            .prefetch_related("field_values__field")
            .order_by("id")
        )

    def get_serializer_class(self):
        return DocumentInstanceCreateSerializer if self.action == "create" else DocumentInstanceSerializer


# ──────────────────── DocumentFieldValueViewSet ────────────────────────
@extend_schema(tags=["SEMD module"])
@extend_schema_view(
    list=extend_schema(summary="Все значения полей", responses=DocumentFieldValueSerializer(many=True)),
    partial_update=extend_schema(summary="Обновить одно значение",
                                 request=DocumentFieldValueUpdateSerializer,
                                 responses=DocumentFieldValueSerializer),
)
class DocumentFieldValueViewSet(mixins.ListModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    # --- helper ---------------------------------------------------------
    def _get_parent_or_404(self):
        try:
            return DocumentInstance.objects.get(
                pk=self.kwargs["document_pk"], user=self.request.user
            )
        except DocumentInstance.DoesNotExist:
            raise Http404

    # --- queryset -------------------------------------------------------
    def get_queryset(self):
        self._get_parent_or_404()                       # 404, если чужой документ
        return (
            DocumentFieldValue.objects
            .filter(document_id=self.kwargs["document_pk"])
            .select_related("field")
            .order_by("id")
        )

    def get_serializer_class(self):
        return (
            DocumentFieldValueUpdateSerializer
            if self.action in {"partial_update", "bulk_update"}
            else DocumentFieldValueSerializer
        )

    # --- bulk-patch -----------------------------------------------------
    @extend_schema(
        summary="Массовое обновление значений",
        request=DocumentFieldValueBulkUpdateListSerializer,
        responses=DocumentFieldValueSerializer(many=True),
    )
    @action(methods=["patch"], detail=False, url_path="bulk_update")
    def bulk_update(self, request, *args, **kwargs):
        self._get_parent_or_404()                       # защита от чужих документов
        qs = list(self.get_queryset())
        ser = DocumentFieldValueBulkUpdateListSerializer(
            instance=qs, data=request.data, context={"request": request}
        )
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(DocumentFieldValueSerializer(qs, many=True).data,
                        status=status.HTTP_200_OK)
