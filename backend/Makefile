sync:
	uv sync

migrate:
	uv run src/manage.py makemigrations users docs_ingest llm semd_templates chat
	uv run src/manage.py migrate

collect-static:
	uv run src/manage.py collectstatic --no-input

copy-sample-env:
	cp .env.sample .env
	cp ../.env.sample ../.env

start-docker-postgres:
	docker compose --file ../docker-compose-local-dev.yml up postgres -d

start-docker-redis:
	docker compose --file ../docker-compose-local-dev.yml up redis -d

start-docker-minio:
	docker compose --file ../docker-compose-local-dev.yml up minio -d

start-docker-qdrant:
	docker compose --file ../docker-compose-local-dev.yml up qdrant -d

start-docker-nginx:
	docker compose --file ../docker-compose-local-dev.yml up nginx -d

start-docker-develop-environment: \
		start-docker-postgres \
		start-docker-redis \
		start-docker-minio \
		start-docker-qdrant \
		start-docker-nginx

runserver:
	uv run src/manage.py runserver

celery-worker:
	cd ./src; uv run celery -A config.celery worker --loglevel=info

celery-beat:
	cd ./src; uv run celery -A config.celery beat --loglevel=info

import-field-definitions:
	uv run src/manage.py import_field_definitions_from_json

export-field-definitions:
	uv run src/manage.py export_field_definitions_to_json

import-document-templates:
	uv run src/manage.py import_document_templates

export-document-templates:
	uv run src/manage.py export_document_templates

entrypoint:
	uv run src/manage.py create_superuser --username admin --dev-pass
	uv run src/manage.py create_positions --medical-set

start-app:  sync copy-sample-env \
			start-docker-develop-environment \
			migrate collect-static \
			import-field-definitions \
			import-document-templates \
			entrypoint

schema-api:
	uv run src/manage.py spectacular --color --file ../schema.yml

test:
	uv run src/manage.py test apps api --parallel


stop-docker-containers:
	docker compose --file ../docker-compose-local-dev.yml stop

down-docker-containers:
	docker compose --file ../docker-compose-local-dev.yml down

