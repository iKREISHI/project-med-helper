from django.db import models
from django.conf import settings
from apps.semd_templates.models import DocumentTemplate, FieldDefinition


class DocumentInstance(models.Model):
    """
    Заполненный документ
    """
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.PROTECT,
        verbose_name="Шаблон документа"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "document_instance"
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return f"{self.template.name} (ID={self.id})"


class DocumentFieldValue(models.Model):
    """
    Поля заполненного документа
    """
    document = models.ForeignKey(
        DocumentInstance,
        on_delete=models.CASCADE,
        related_name="field_values",
        verbose_name="Документ"
    )

    field = models.ForeignKey(
        FieldDefinition,
        on_delete=models.PROTECT,
        verbose_name="Определение поля"
    )

    value = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Значение"
    )

    class Meta:
        db_table = "document_field_value"
        unique_together = [("document", "field")]
        verbose_name = "Значение поля документа"
        verbose_name_plural = "Значения полей документов"

    def __str__(self):
        return f"{self.document.id}:{self.field.key}={self.value}"
