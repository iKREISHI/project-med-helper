# Серверная часть веб-приложения

## Разработка:

### Установка пакетов:
```bash
make start-app
```

Пример **.env** для работы приложения:
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=med_db
DATABASE_URL=postgres://postgres:postgres@127.0.0.1:5432/med_db

REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=med_docs
EMB_MODEL=BAAI/bge-m3

MINIO_ENDPOINT_URL=http://minio:9000
MINIO_BUCKET=med-docs
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

```
