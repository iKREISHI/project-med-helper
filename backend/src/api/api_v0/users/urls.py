"""Маршруты модуля users для API v0.

Здесь определяется DRF-роутер и регистрируются viewset'ы, относящиеся к пользователям.
Подключается в api/api_v0/urls.py через include.
"""
from rest_framework.routers import DefaultRouter

from .views import LoginViewSet, UsersViewSet, RegisterViewSet, LogoutViewSet

router = DefaultRouter()
router.register(r'auth/login', LoginViewSet, basename='login')
router.register(r'auth/logout', LogoutViewSet, basename='logout')
router.register(r'auth/register', RegisterViewSet, basename='register')
router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [] + router.urls
