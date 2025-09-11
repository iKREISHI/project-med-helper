sync:
	uv sync

migrate:
	uv run src/manage.py makemigrations users
	uv run src/manage.py migrate

collect-static:
	uv run src/manage.py collectstatic --no-input

start-app: sync migrate collect-static

schema-api:
	uv run src/manage.py spectacular --color --file schema.yml

test:
	uv run src/manage.py test apps --parallel
