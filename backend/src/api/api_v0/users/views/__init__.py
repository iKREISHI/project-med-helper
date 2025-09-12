"""Пакет с view-наборами для пользователей (API v0)."""
from .login import LoginViewSet  # re-export для удобного импорта в urls
from .user import UsersViewSet  # экспорт для роутинга users
from .register import RegisterViewSet  # экспорт для роутинга регистрации
