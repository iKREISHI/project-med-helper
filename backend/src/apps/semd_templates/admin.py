from django.contrib import admin
from .models import FieldDefinition, DocumentTemplate, TemplateField, DocumentFieldValue, DocumentInstance


@admin.register(FieldDefinition)
class FieldDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "label",
        "field_type",
        "required",
        "validation_strategy",
    )
    list_filter = ("field_type", "validation_strategy", "required")
    search_fields = ("key", "label")
    ordering = ("key",)


class TemplateFieldInline(admin.TabularInline):
    model = TemplateField
    extra = 1
    autocomplete_fields = ("field",)
    ordering = ("order",)


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TemplateFieldInline]
    ordering = ("name",)

# Inline для значений полей
class DocumentFieldValueInline(admin.TabularInline):
    model  = DocumentFieldValue
    extra  = 0
    # если полей много, автокомплит удобнее селекта
    autocomplete_fields = ("field",)
    # значение (JSON) редактируется прямо в таблице
    fields = ("field", "value")
    readonly_fields = ()           # можно добавить "id", если нужно


# Документы
@admin.register(DocumentInstance)
class DocumentInstanceAdmin(admin.ModelAdmin):
    list_display  = ("id", "template", "user", "created_at", "updated_at")
    list_filter   = ("template", "user", "created_at")
    search_fields = ("id", "template__name", "user__username")
    date_hierarchy = "created_at"

    autocomplete_fields = ("template", "user")
    inlines = [DocumentFieldValueInline]


@admin.register(DocumentFieldValue)
class DocumentFieldValueAdmin(admin.ModelAdmin):
    list_display  = ("id", "document", "field")
    list_filter   = ("field",)
    search_fields = ("document__id", "field__key", "field__label")
    autocomplete_fields = ("document", "field")

