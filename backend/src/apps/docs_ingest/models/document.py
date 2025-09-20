from django.conf import settings
from django.db import models


class Document(models.Model):
    """
    Модель для хранения мед. документов
    """
    class Status(models.TextChoices):
        UPLOADED="UPLOADED"; PARSED="PARSED"; INDEXED="INDEXED"; FAILED="FAILED"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Владелец"
    )
    title = models.CharField(max_length=512, blank=True)
    file = models.FileField(upload_to="docs/")
    source = models.CharField(max_length=128, default="upload")
    content_type = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=16, default="ru")
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.UPLOADED
    )
    error = models.TextField(blank=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or self.file.name} ({self.owner})"

    class Meta:
        verbose_name = 'Клинические рекомендации'