from django.db import models
from .semd_fields import FieldDefinition


class DocumentTemplate(models.Model):
    """
    Шаблон документа СЭМД под любые документы.
    """
    name = models.CharField(
        max_length=255,
        verbose_name="Название шаблона",
        help_text="Название медицинского документа (например 'Эпикриз')."
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Код шаблона",
        help_text="Уникальный системный идентификатор шаблона (например 'epicrisis')."
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Для чего предназначен данный шаблон."
    )

    fields = models.ManyToManyField(
        FieldDefinition,
        through="TemplateField",
        related_name="templates",
        verbose_name="Поля",
        help_text="Какие поля входят в данный шаблон."
    )

    class Meta:
        db_table = "document_template"
        verbose_name = "Шаблон документа"
        verbose_name_plural = "Шаблоны документов"

    def __str__(self):
        return self.name


class TemplateField(models.Model):
    """
    Проходное поле для связи ManyToManyField
    """
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.CASCADE,
        verbose_name="Шаблон"
    )

    field = models.ForeignKey(
        FieldDefinition,
        on_delete=models.CASCADE,
        verbose_name="Поле"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
        help_text="Определяет порядок отображения поля в шаблоне."
    )

    class Meta:
        db_table = "template_field"
        unique_together = [("template", "field")]
        ordering = ["template", "order"]
        verbose_name = "Поле шаблона"
        verbose_name_plural = "Поля шаблонов"

    def __str__(self):
        return f"{self.template.slug}:{self.field.key}"
