import os
from email.policy import default

import environ
from pathlib import Path

from django.template.defaultfilters import default

# Определяем корневую директорию, где должен находиться файл .env.
ENV_PATH = Path(__file__).resolve().parents[2]

# Инициализируем объект окружения
env = environ.Env()

# Определяем путь к файлу .env
env_file = ENV_PATH / '.env'

# Если файл .env существует, загружаем его
if env_file.exists():
    environ.Env.read_env(str(env_file))

# ---------------------------
# Чтение переменных окружения
# ---------------------------
# POSTGRES
DATABASES_URL = env.db(
    'DATABASE_URL',
    default='postgres://meduser:medpass@127.0.0.1:5432/medhelper'
)

DATABASE_URL = env('DATABASE_URL', default='postgres://postgres:postgres@127.0.0.1:5432/med_db')

# MINIO
MINIO_ROOT_USER = env('MINIO_ROOT_USER', default='minioadmin')
MINIO_ROOT_PASSWORD = env('MINIO_ROOT_PASSWORD', default='minioadmin')
MINIO_INSTANCE_ADDRESS = env('MINIO_INSTANCE_ADDRESS', default='127.0.0.1:9000')

SERVER_BACKEND_IP_ADDRESS = env('SERVER_BACKEND_IP_ADDRESS', default='127.0.0.1:8000')

# Celery
CELERY_BROKER_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Qdrant
QDRANT_URL = env("QDRANT_URL", default="http://127.0.0.1:6333")
QDRANT_COLLECTION = env("QDRANT_COLLECTION", default="med_docs")
EMB_MODEL = env("EMB_MODEL", default="BAAI/bge-m3")