# Серверная часть веб-приложения

## Разработка:

### Подготовка рабочего окружения для первого запуска:
```bash
make start-app
```
### Для последующих запусков окружения:
```bash
make run-dev
```

## Как запустить проект:
```bash
make runserver
```

## Чтобы запустить задачи в celery:
```bash
# откройте новую вкладку терминала и выполните запуск службы воркера:
make celery-worker 

# откройте новую вкладку терминала и выполните запуск службы расписания:
make celery-beat 
```
## Чтобы импортировать набор документов выполните:
```bash
make import-templates-semd-document
```
## Зазгрузить в БД PDF-ки:
```bash
 uv run src/manage.py import_pdfs --path /Users/vadimaskarov/PycharmProjects/project-med-helper/backend/pdf_examples --owner 2    
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

# LLM PROVIDER API KEYS
OPENROUTER_API_KEY=your_key
GIGACHAT_API_KEY=your_key
LOCAL_LLM_API=http://localhost:11434
LLM_PROVIDER=gigachat
```

Пример **.env** для локальной разработки:
```bash
# Postgres
POSTGRES_DB=medhelper
POSTGRES_USER=meduser
POSTGRES_PASSWORD=medpass
DATABASE_URL=postgresql://meduser:medpass@127.0.0.1:5432/medhelper

# Redis/Celery
REDIS_URL=redis://127.0.0.1:6379/0

# Qdrant
QDRANT_URL=http://127.0.0.1:6333
QDRANT_COLLECTION=med_docs
EMB_MODEL=BAAI/bge-m3

# MinIO (S3 backend)
MINIO_ENDPOINT_URL=http://127.0.0.1:9000
MINIO_BUCKET=med-docs
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
AWS_S3_ENDPOINT_URL=http://127.0.0.1:9000
AWS_STORAGE_BUCKET_NAME=med-docs
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_S3_USE_SSL=false
AWS_S3_VERIFY=false

# LLM PROVIDER API KEYS
OPENROUTER_API_KEY=your_key
GIGACHAT_API_KEY=your_key
LOCAL_LLM_API=http://localhost:11434
LLM_PROVIDER=gigachat
```
