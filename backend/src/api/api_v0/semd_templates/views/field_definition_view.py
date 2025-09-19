import logging
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from apps.semd_templates.models.semd_fields import FieldDefinition
from api.api_v0.semd_templates.serializers.field_definition_serializer import FieldDefinitionSerializer

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        tags=["SEMD module"],
        summary="Список полей",
        description="Возвращает список полей с пагинацией.",
        responses=FieldDefinitionSerializer,
        parameters=[
            OpenApiParameter(
                name="page", type=OpenApiTypes.INT, required=False,
                description="Номер страницы"
            ),
            OpenApiParameter(
                name="page_size", type=OpenApiTypes.INT, required=False,
                description="Количество элементов на странице (по умолчанию 10)"
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["SEMD module"],
        summary="Получить поле",
        description="Возвращает одно поле по ID.",
        responses=FieldDefinitionSerializer,
    ),
)
class FieldDefinitionViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    queryset = FieldDefinition.objects.all().order_by("id")
    serializer_class = FieldDefinitionSerializer
    pagination_class = StandardResultsSetPagination
