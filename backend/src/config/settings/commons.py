"""
Базовые настройки Django для проекта config.

Сгенерировано с помощью 'django-admin startproject' на Django 5.2.4.

Подробнее о настройках:
https://docs.djangoproject.com/en/5.2/topics/settings/

Полный список параметров и их значения:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
from config import settings
from config.settings import BASE_DIR


# Быстрый старт для разработки — не подходит для продакшена
# Чек-лист по настройке продакшена:
# https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# ВНИМАНИЕ: храните секретный ключ в секрете на продакшене!
SECRET_KEY = 'django-insecure-&o_e04nx5*$a@e!y!c!gnbqfp&lj52iusf%_w0sn3nffri5-a%'

# ВНИМАНИЕ: не запускайте проект с DEBUG=True на продакшене!
DEBUG = True

# Конфигурация точек входа
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# Валидация паролей
# Документация: https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Тип поля первичного ключа по умолчанию
# Документация: https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
