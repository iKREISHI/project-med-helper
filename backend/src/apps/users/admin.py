from django.contrib import admin

# Регистрация моделей в админ‑панели Django.
from .models import User, Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Админ‑настройки для модели «Должность»"""
    list_display = ("id", "name", "short_name", "minzdrav_position")
    search_fields = ("name", "short_name", "minzdrav_position")
    list_display_links = ("id", "name")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Простая регистрация кастомной модели пользователя в админке.
    В дальнейшем при необходимости можно заменить на наследование от
    django.contrib.auth.admin.UserAdmin и детально настроить поля.
    """
    list_display = ("id", "username", "first_name", "last_name", "position", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "position")
    list_display_links = ("id", "username")
