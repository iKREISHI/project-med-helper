from django.db import models
from apps.docs_ingest.models import Document
from django.conf import settings


class Chunk(models.Model):
    """
    Модель для хранения чанков мед. документов
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chunks",
        verbose_name="Владелец"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks"
    )
    idx = models.IntegerField()
    text = models.TextField()
    section = models.CharField(max_length=256, blank=True)
    page_from = models.IntegerField(null=True, blank=True)
    page_to = models.IntegerField(null=True, blank=True)
    tokens = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("document", "idx")
        verbose_name = 'Чанк клинических рекомендаций'
        verbose_name_plural = 'Чанки клинических рекомендаций'

    def __str__(self):
        return f"Chunk {self.idx} of {self.document} ({self.owner})"