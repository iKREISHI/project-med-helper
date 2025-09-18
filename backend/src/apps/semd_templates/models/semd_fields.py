from django.db import models
from django.contrib.postgres.fields import ArrayField


class FieldType(models.TextChoices):
    TEXT = 'text', 'Текст'
    LONG_TEXT = 'long_text', 'Длинный текст'
    NUMBER = 'number', 'Число'
    INTEGER = 'integer', 'Целое'
    DECIMAL = 'decimal', 'Десятичное'
    DATE = 'date', 'Дата'
    DATETIME = 'datetime', 'Дата и время'
    BOOLEAN = 'boolean', 'Логический (да/нет)'


class ValidationStrategy(models.TextChoices):
    NONE = 'none', 'Нет'
    SERVER = 'server', 'Серверная'
    LLM = 'llm', 'ИИ (LLM)'
    BOTH = 'both', 'Обе'


class FieldDefinition(models.Model):
    key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Ключ поля",
        help_text="Уникальный технический идентификатор поля в системе (например 'anamnesis')."
    )

    label = models.CharField(
        max_length=255,
        verbose_name="Название поля",
        help_text="Отображаемое название поля для пользователя (например 'Анамнез')."
    )

    field_type = models.CharField(
        max_length=30,
        choices=FieldType.choices,
        default=FieldType.TEXT,
        verbose_name="Тип поля",
        help_text="Определяет, какой вид данных ожидается (текст, число, дата и т.п.)."
    )

    required = models.BooleanField(
        default=False,
        verbose_name="Обязательное",
        help_text="Если включено — поле должно быть заполнено."
    )

    server_validators = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        verbose_name="Серверные валидаторы",
        help_text="Список встроенных правил проверки, например ['not_empty', 'max_length:1000']."
    )

    validation_strategy = models.CharField(
        max_length=10,
        choices=ValidationStrategy.choices,
        default=ValidationStrategy.SERVER,
        verbose_name="Варианты валидации",
        help_text="Каким образом проверяется поле: сервер, ИИ или обе стратегии."
    )

    class Meta:
        verbose_name = "Определение поля"
        verbose_name_plural = "Определения полей"

    def __str__(self):
        return self.key
