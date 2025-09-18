from django.contrib import admin
from .models import FieldDefinition, DocumentTemplate, TemplateField


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

