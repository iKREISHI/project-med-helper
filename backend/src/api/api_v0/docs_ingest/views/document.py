from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes, OpenApiExample
)

from apps.docs_ingest.models import Document
from api.api_v0.docs_ingest.serializers.document_basic import DocumentUploadSerializer, DocumentOutSerializer
from apps.docs_ingest.tasks import pipeline_index_document
from apps.docs_ingest.vectors import delete_doc

logger = logging.getLogger(__name__)

_tag_name = "Клинические рекомендации"

@extend_schema_view(
    list=extend_schema(
        tags=[_tag_name],
        summary="Список документов",
        description="Возвращает список загруженных документов, отсортированных по дате создания (DESC).",
        responses=DocumentOutSerializer,
        parameters=[
            OpenApiParameter(name="search", type=OpenApiTypes.STR, required=False,
                             description="(опц.) Поиск по title/source (если добавите фильтрацию)"),
        ],
    ),
    retrieve=extend_schema(
        tags=[_tag_name],
        summary="Получить документ",
        responses=DocumentOutSerializer,
    ),
    create=extend_schema(
        tags=[_tag_name],
        summary="Загрузить документ",
        description="Загружает файл (PDF/DOCX/...), создаёт запись и ставит в очередь пайплайн парсинга/индексации.",
        request=DocumentUploadSerializer,
        responses=DocumentOutSerializer,
        examples=[
            OpenApiExample(
                "Загрузка PDF",
                value={"title": "КР ХОБЛ", "source": "upload", "language": "ru"},
            )
        ],
    ),
)
class DocumentViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all().order_by("-created_at")

    def get_queryset(self):
        # по умолчанию показываем документы владельца
        return super().get_queryset().filter(owner=self.request.user)

    def get_serializer_class(self):
        return DocumentUploadSerializer if self.action == "create" else DocumentOutSerializer

    def perform_create(self, serializer):
        """
        Создаём документ и запускаем пайплайн индексации.
        В дев-окружении (или если брокер недоступен) пытаемся выполнить задачу синхронно,
        чтобы не падать 500-кой при отсутствии Redis/Celery worker.
        """
        doc = serializer.save(owner=self.request.user, status=Document.Status.UPLOADED)
        # Сохраним content_type из загруженного файла, чтобы парсер мог использовать подсказку
        uploaded = self.request.FILES.get('file')
        if uploaded is not None:
            ct = getattr(uploaded, 'content_type', '') or ''
            if ct and ct != (doc.content_type or ''):
                doc.content_type = ct
                doc.save(update_fields=["content_type"]) 
        try:
            # Пытаемся отправить задачу в очередь (обычный путь)
            logger.info("[api] Постановка задачи индексирования в очередь: doc_id=%s", doc.id)
            pipeline_index_document.delay(doc.id)
        except Exception as exc:
            # Если брокер недоступен, выполним задачу локально
            logger.warning("[api] Не удалось отправить задачу в очередь, выполняем локально: %s", exc)
            try:
                from kombu.exceptions import OperationalError
            except Exception:
                OperationalError = tuple()  # запасной вариант, если kombu не установлен
            if isinstance(exc, OperationalError) or getattr(exc, "errno", None) is not None:
                # Выполнить синхронно — без брокера
                logger.info("[api] Запуск индексирования синхронно: doc_id=%s", doc.id)
                pipeline_index_document.apply(args=(doc.id,))
            else:
                # Пробрасываем непривычные исключения дальше
                raise

    @extend_schema(
        tags=["Documents"],
        summary="Переиндексировать документ",
        description="Повторно запускает пайплайн парсинга/чанкинга/эмбеддингов/апсерта в Qdrant.",
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=["post"])
    def reindex(self, request, pk=None):
        """
        Переиндексация по требованию. Если брокер сообщений недоступен,
        выполняем задачу синхронно, чтобы вернуть валидный ответ в дев-среде.
        """
        try:
            pipeline_index_document.delay(pk)
            return Response({"status": "queued"}, status=200)
        except Exception as exc:
            try:
                from kombu.exceptions import OperationalError
            except Exception:
                OperationalError = tuple()
            if isinstance(exc, OperationalError) or getattr(exc, "errno", None) is not None:
                pipeline_index_document.apply(args=(pk,))
                return Response({"status": "executed"}, status=200)
            raise

    @extend_schema(
        tags=["Documents"],
        summary="Удалить документ и его эмбеддинги",
        description="Удаляет документ из БД и все связанные точки из Qdrant.",
        responses={204: None},
    )
    @action(detail=True, methods=["delete"])
    def purge(self, request, pk=None):
        delete_doc(int(pk), owner_id=request.user.id)
        Document.objects.filter(pk=pk, owner=request.user).delete()
        return Response(status=204)
