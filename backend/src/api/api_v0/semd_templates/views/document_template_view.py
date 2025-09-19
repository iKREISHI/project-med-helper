import logging
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from api.api_v0.semd_templates.serializers.document_template_serializer import DocumentTemplateSerializer
from apps.semd_templates.models.semd_docs_templates import DocumentTemplate

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        tags=["SEMD module"],
        summary="Список шаблонов документов",
        description="Возвращает список шаблонов документов с их полями.",
        responses=DocumentTemplateSerializer,
        parameters=[
            OpenApiParameter(
                name="page", type=OpenApiTypes.INT, required=False,
                description="Номер страницы"
            ),
            OpenApiParameter(
                name="page_size", type=OpenApiTypes.INT, required=False,
                description="Количество элементов на странице"
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["SEMD module"],
        summary="Получить шаблон документа",
        description="Возвращает один шаблон документа по ID.",
        responses=DocumentTemplateSerializer,
    ),
)
class DocumentTemplateViewSet(mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    queryset = DocumentTemplate.objects.prefetch_related("templatefield_set__field").all()
    serializer_class = DocumentTemplateSerializer
    pagination_class = StandardResultsSetPagination