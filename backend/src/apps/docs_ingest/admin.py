"""
Регистрация моделей приложения docs_ingest в административной панели Django.

Все комментарии и описания на русском языке согласно правилам проекта.
"""
from django.contrib import admin

from .models import Document, Chunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Админ-представление для модели медицинского документа."""

    list_display = (
        "id",
        "title",
        "owner",
        "status",
        "content_type",
        "language",
        "created_at",
    )
    list_select_related = ("owner",)
    list_filter = ("status", "language", "source", "content_type", "created_at")
    search_fields = ("title", "file", "owner__username")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("owner",)


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    """Админ-представление для модели фрагмента (chunk) документа."""

    list_display = (
        "id",
        "document",
        "idx",
        "owner",
        "section",
        "page_from",
        "page_to",
        "tokens",
    )
    list_select_related = ("owner", "document")
    list_filter = ("section",)
    search_fields = ("document__title", "document__file", "owner__username", "text")
    autocomplete_fields = ("owner", "document")
