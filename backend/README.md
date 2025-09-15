# Серверная часть веб-приложения

## Разработка:

### Установка пакетов:
```bash
make start-app
```

Пример **.env** для работы приложения:
```bash
# Postgres
POSTGRES_DB=medhelper
POSTGRES_USER=meduser
POSTGRES_PASSWORD=medpass
DATABASE_URL=postgresql://meduser:medpass@postgres:5432/medhelper

# Redis/Celery
REDIS_URL=redis://redis:6379/0

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=med_docs
EMB_MODEL=BAAI/bge-m3

# MinIO (S3 backend)
MINIO_ENDPOINT_URL=http://minio:9000
MINIO_BUCKET=med-docs
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
AWS_S3_ENDPOINT_URL=http://minio:9000
AWS_STORAGE_BUCKET_NAME=med-docs
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_S3_USE_SSL=false
AWS_S3_VERIFY=false
```
