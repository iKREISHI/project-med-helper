import os
from config.settings import BASE_DIR


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STORAGES = {
    # "default": {
    #     "BACKEND": "minio_storage.storage.MinioMediaStorage",
    # },
    # "staticfiles": {
    #     "BACKEND": ""minio_storage.storage.MinioMediaStorage"",
    # },
    # or "django.contrib.staticfiles.storage.StaticFilesStorage",
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
}